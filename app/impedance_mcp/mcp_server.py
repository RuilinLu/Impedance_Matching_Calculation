"""MCP (Model Context Protocol) server over stdio / optional local HTTP.

MCP clients such as ZCode can connect with:

    python app/run_mcp.py

The server exposes the matching engine as 15 tools plus documentation resources.
Only JSON-RPC messages are written to stdout; logs go to stderr.
"""

from __future__ import annotations

import json
import os
import queue
import sys
import threading
import traceback
import urllib.parse
import uuid
from typing import Any, Dict, Iterable, List, Optional

from . import config, docs_hub, engine, knowledge, library, tools

PROTOCOL_VERSIONS = {"2024-11-05", "2025-03-26", "2025-06-18"}
DEFAULT_PROTOCOL = "2025-06-18"

INSTRUCTIONS = (
    "这是「Impedance Matching AI」微波阻抗匹配计算、仿真与教材检索服务器。"
    "任何涉及频率、负载阻抗、L/C 元件值、VSWR、带宽、耐压的具体问题，"
    "请先调用 design_matching_network / evaluate_network / scan_matching_range 等工具，"
    "再基于工具返回值解释。topology=auto 会自动比较 L/T/π 五种拓扑。"
    "涉及教材原文、公式出处、Smith 圆图、传输线、波导、天线时，"
    "请调用 search_textbooks / read_textbook_page / translate_textbook_page；"
    "引用必须带书名与页码。软件自身的使用说明可调用 search_docs 或 get_code_reference。"
    "单位：频率 MHz，阻抗 Ω，电感 µH，电容 pF。"
)


def _log(*args: Any) -> None:
    try:
        print("[impedance-mcp]", *args, file=sys.stderr, flush=True)
    except Exception:
        pass


def _result_text(result: Dict[str, Any]) -> str:
    summary = result.get("summary") or result.get("message") or ""
    body = {k: v for k, v in result.items() if k != "summary"}
    text = json.dumps(body, ensure_ascii=False, indent=1)
    return (summary + "\n\n" + text).strip()


class MCPServer:
    def __init__(self) -> None:
        self.initialized = False
        self.client_info: Dict[str, Any] = {}
        self.protocol = DEFAULT_PROTOCOL
        self.exiting = False

    # -- JSON-RPC plumbing -------------------------------------------------
    def handle(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(msg, dict):
            return self._error(None, -32600, "Invalid Request")
        method = msg.get("method")
        msg_id = msg.get("id", None)
        params = msg.get("params") or {}
        is_notification = "id" not in msg

        if not isinstance(method, str):
            return None if is_notification else self._error(msg_id, -32600, "Invalid Request")

        try:
            result = self._dispatch(method, params)
        except Exception as exc:  # noqa: BLE001
            _log("error in", method, ":", traceback.format_exc(limit=6))
            if is_notification:
                return None
            return self._error(msg_id, -32603, f"Internal error: {exc}")

        if is_notification:
            return None
        if isinstance(result, JsonRpcError):
            return self._error(msg_id, result.code, result.message, result.data)
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    def _dispatch(self, method: str, params: Dict[str, Any]) -> Any:
        if method == "initialize":
            requested = str(params.get("protocolVersion") or DEFAULT_PROTOCOL)
            self.protocol = requested if requested in PROTOCOL_VERSIONS else DEFAULT_PROTOCOL
            self.initialized = True
            self.client_info = params.get("clientInfo") or {}
            _log("initialize from", self.client_info.get("name"), "protocol", self.protocol)
            return {
                "protocolVersion": self.protocol,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "prompts": {"listChanged": False},
                    "logging": {},
                },
                "serverInfo": {
                    "name": "impedance-matching-ai",
                    "title": "Impedance Matching AI · 微波阻抗匹配与教材检索",
                    "version": config.VERSION,
                    "websiteUrl": "https://github.com/SkywalkerHolmes/Impedance_Matching_Calculation",
                },
                "instructions": INSTRUCTIONS,
            }
        if method == "notifications/initialized":
            return {}
        if method == "ping":
            return {}
        if method == "tools/list":
            return {"tools": tools.TOOL_SPECS}
        if method == "tools/call":
            name = str(params.get("name") or "")
            args = params.get("arguments") or {}
            if not isinstance(args, dict):
                return JsonRpcError(-32602, "工具参数必须是对象")
            result = tools.call_tool(name, args)
            known = name in tools.TOOL_MAP
            return {
                "content": [{"type": "text", "text": _result_text(result)}],
                "structuredContent": result,
                "isError": (not known) or bool(result.get("error_code") == "internal_error"),
            }
        if method == "resources/list":
            return {"resources": self._resources()}
        if method == "resources/read":
            uri = str(params.get("uri") or "")
            return self._read_resource(uri)
        if method == "resources/templates/list":
            return {"resourceTemplates": []}
        if method == "prompts/list":
            return {"prompts": self._prompts()}
        if method == "prompts/get":
            return self._get_prompt(str(params.get("name") or ""), params.get("arguments") or {})
        if method == "completion/complete":
            return {"completion": {"values": [], "total": 0, "hasMore": False}}
        if method == "logging/setLevel":
            return {}
        if method in ("shutdown", "exit"):
            self.exiting = True
            return {}
        if method.startswith("notifications/"):
            return {}
        return JsonRpcError(-32601, f"Method not found: {method}")

    @staticmethod
    def _error(msg_id: Any, code: int, message: str,
               data: Any = None) -> Dict[str, Any]:
        err: Dict[str, Any] = {"code": code, "message": message}
        if data is not None:
            err["data"] = data
        return {"jsonrpc": "2.0", "id": msg_id, "error": err}

    # -- resources / prompts ----------------------------------------------
    def _resources(self) -> List[Dict[str, Any]]:
        return [
            {"uri": "impedance://catalog", "name": "拓扑目录",
             "description": "五种匹配拓扑的适用条件、电路结构与公式",
             "mimeType": "application/json"},
            {"uri": "impedance://knowledge", "name": "微波匹配知识库",
             "description": "圆图、Q/带宽、寄生、耐压、选型与常见问题",
             "mimeType": "text/markdown"},
            {"uri": "impedance://status", "name": "运行状态",
             "description": "版本、LLM、MCP 与教材目录状态",
             "mimeType": "application/json"},
            {"uri": "impedance://library", "name": "教材库目录",
             "description": "已索引教材、页数、OCR 状态与教材库统计",
             "mimeType": "application/json"},
            {"uri": "impedance://docs", "name": "软件文档目录",
             "description": "四类文档（功能、代码、AI 接口、MCP）的入口",
             "mimeType": "application/json"},
        ]

    def _read_resource(self, uri: str) -> Any:
        if uri == "impedance://catalog":
            text = json.dumps(engine.catalog(), ensure_ascii=False, indent=2)
            mime = "application/json"
        elif uri == "impedance://knowledge":
            parts = []
            for section in knowledge.all_sections():
                parts.append(f"## {section['title']}\n\n{section['text']}")
            text = "\n\n".join(parts)
            mime = "text/markdown"
        elif uri == "impedance://status":
            text = json.dumps(config.status(), ensure_ascii=False, indent=2)
            mime = "application/json"
        elif uri == "impedance://library":
            text = json.dumps({
                "status": library.status(),
                "documents": library.doc_list(),
            }, ensure_ascii=False, indent=2)
            mime = "application/json"
        elif uri == "impedance://docs":
            text = json.dumps(docs_hub.list_docs("zh"), ensure_ascii=False, indent=2)
            mime = "application/json"
        else:
            return JsonRpcError(-32602, f"未知资源：{uri}")
        return {"contents": [{"uri": uri, "mimeType": mime, "text": text}]}

    @staticmethod
    def _prompts() -> List[Dict[str, Any]]:
        return [
            {
                "name": "design_match",
                "title": "设计一个匹配网络",
                "description": "根据频率与负载阻抗给出完整匹配方案",
                "arguments": [
                    {"name": "frequency_mhz", "description": "频率 MHz", "required": True},
                    {"name": "load", "description": "负载阻抗，如 20+j10", "required": True},
                    {"name": "topology", "description": "拓扑或 auto", "required": False},
                ],
            },
            {
                "name": "explain_topology",
                "title": "解释一种拓扑",
                "description": "讲解 L/T/π 网络的原理与适用条件",
                "arguments": [
                    {"name": "topology", "description": "l_right/l_left/t/pi1/pi2",
                     "required": True},
                ],
            },
            {
                "name": "troubleshoot",
                "title": "排查匹配问题",
                "description": "分析无解、VSWR 偏高、带宽不足等问题",
                "arguments": [
                    {"name": "problem", "description": "现象描述", "required": True},
                ],
            },
            {
                "name": "find_textbook",
                "title": "在教材中查找",
                "description": "检索教材库并定位到具体页码与段落",
                "arguments": [
                    {"name": "topic", "description": "要查找的概念或公式", "required": True},
                    {"name": "book", "description": "可选：书名或 doc_id", "required": False},
                ],
            },
            {
                "name": "explain_textbook_page",
                "title": "讲解教材页",
                "description": "读取指定教材页，解释公式与工程含义",
                "arguments": [
                    {"name": "doc_id", "description": "教材 id", "required": True},
                    {"name": "page", "description": "页码", "required": True},
                ],
            },
        ]

    def _get_prompt(self, name: str, args: Dict[str, Any]) -> Any:
        if name == "design_match":
            f = args.get("frequency_mhz", "")
            load = args.get("load", "")
            top = args.get("topology", "auto")
            text = (
                f"请为 {f} MHz、负载 {load} Ω 设计一个阻抗匹配网络（拓扑：{top}）。"
                "先调用 design_matching_network 工具，再给出元件表、VSWR、带宽、"
                "灵敏度与工程建议。若不可行，请比较其他拓扑。"
            )
        elif name == "explain_topology":
            top = args.get("topology", "")
            text = (f"请解释 {top} 匹配网络的电路结构、适用负载、设计公式与优缺点，"
                    "可调用 get_topology_guide 和 search_knowledge。")
        elif name == "troubleshoot":
            problem = args.get("problem", "")
            text = (f"我的匹配设计遇到问题：{problem}。请先检索知识库，"
                    "必要时调用 compare_topologies 或 design_matching_network 验证，"
                    "然后给出物理原因与可执行的修改步骤。")
        elif name == "find_textbook":
            topic = args.get("topic", "")
            book = args.get("book", "")
            text = (f"请在教材库中检索“{topic}”" +
                    (f"（限定：{book}）" if book else "") +
                    "，调用 search_textbooks，并用 read_textbook_page 阅读最相关的 1–3 页；"
                    "回答时给出书名、页码、原文摘录与你的解释。")
        elif name == "explain_textbook_page":
            doc_id = args.get("doc_id", "")
            page = args.get("page", "")
            text = (f"请读取教材 doc_id={doc_id} 第 {page} 页（read_textbook_page），"
                    "解释其中的公式、变量与工程含义；如果页面是扫描版且模型支持视觉，"
                    "请阅读返回的页面截图。引用必须带书名与页码。")
        else:
            return JsonRpcError(-32602, f"未知 prompt：{name}")
        return {"description": name, "messages": [
            {"role": "user", "content": {"type": "text", "text": text}}
        ]}


class JsonRpcError:
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data


def _iter_messages(stream) -> Iterable[Dict[str, Any]]:
    """Read newline-delimited JSON, also tolerating Content-Length framing."""
    while True:
        line = stream.readline()
        if not line:
            return
        if isinstance(line, bytes):
            line = line.decode("utf-8", errors="replace")
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower().startswith("content-length:"):
            try:
                length = int(stripped.split(":", 1)[1].strip())
            except ValueError:
                continue
            # Consume the blank line, then read exactly length bytes.
            stream.readline()
            raw = stream.read(length)
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", errors="replace")
            stripped = raw.strip()
        try:
            yield json.loads(stripped)
        except json.JSONDecodeError as exc:
            _log("JSON parse error:", exc, stripped[:200])
            yield {"jsonrpc": "2.0", "method": "__parse_error__", "id": None}


def run_stdio() -> None:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:
            pass
    server = MCPServer()
    _log("stdio server started, version", config.VERSION)
    for msg in _iter_messages(sys.stdin):
        if msg.get("method") == "__parse_error__":
            response = MCPServer._error(None, -32700, "Parse error")
        else:
            response = server.handle(msg)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        if server.exiting:
            break
    _log("stdio server stopped")


def run_http(host: str = "127.0.0.1", port: int = 8790) -> None:
    """Serve MCP over Streamable HTTP and legacy HTTP+SSE.

    Endpoints
    ---------
    POST   /mcp                    Streamable HTTP JSON-RPC (Mcp-Session-Id)
    GET    /mcp                    405 (no server-initiated messages)
    DELETE /mcp                    terminate a streamable session
    GET    /sse                    legacy HTTP+SSE endpoint event
    POST   /messages?sessionId=... legacy client -> server messages
    GET    /health                 service metadata
    """
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    sessions: Dict[str, "MCPServer"] = {}
    sse_queues: Dict[str, "queue.Queue[Optional[Dict[str, Any]]]"] = {}
    lock = threading.Lock()

    def _new_session() -> tuple:
        sid = uuid.uuid4().hex
        srv = MCPServer()
        with lock:
            sessions[sid] = srv
        return sid, srv

    def _session(sid: Optional[str]) -> tuple:
        if sid:
            with lock:
                srv = sessions.get(sid)
            if srv is not None:
                return sid, srv
        return _new_session()

    def _drop_session(sid: Optional[str]) -> None:
        if not sid:
            return
        with lock:
            sessions.pop(sid, None)
            sse_queues.pop(sid, None)

    class Handler(BaseHTTPRequestHandler):
        server_version = "ImpedanceMCP/" + config.VERSION
        protocol_version = "HTTP/1.1"

        # -- helpers ------------------------------------------------------
        def _origin_ok(self) -> bool:
            origin = self.headers.get("Origin")
            if not origin:
                return True
            try:
                parsed = urllib.parse.urlparse(origin)
                return parsed.hostname in ("127.0.0.1", "localhost", "::1")
            except Exception:
                return False

        def _cors(self) -> None:
            origin = self.headers.get("Origin")
            if origin and self._origin_ok():
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers",
                "Content-Type, Accept, Mcp-Session-Id, MCP-Protocol-Version",
            )
            self.send_header("Access-Control-Expose-Headers", "Mcp-Session-Id, MCP-Protocol-Version")

        def _send_json(self, payload: Any, status: int = 200,
                       sid: Optional[str] = None,
                       ctype: str = "application/json; charset=utf-8") -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("MCP-Protocol-Version", DEFAULT_PROTOCOL)
            if sid:
                self.send_header("Mcp-Session-Id", sid)
            self._cors()
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _send_empty(self, status: int, sid: Optional[str] = None) -> None:
            self.send_response(status)
            self.send_header("Content-Length", "0")
            self.send_header("MCP-Protocol-Version", DEFAULT_PROTOCOL)
            if sid:
                self.send_header("Mcp-Session-Id", sid)
            self._cors()
            self.end_headers()

        def _read_json(self) -> Optional[Dict[str, Any]]:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send_json(MCPServer._error(None, -32600, "Invalid Content-Length"), 400)
                return None
            if length <= 0:
                self._send_json(MCPServer._error(None, -32600, "Empty body"), 400)
                return None
            if length > 4_000_000:
                self._send_json(MCPServer._error(None, -32600, "Request too large"), 413)
                return None
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                self._send_json(MCPServer._error(None, -32700, "Parse error"), 400)
                return None
            if not isinstance(msg, dict):
                self._send_json(MCPServer._error(None, -32600, "JSON-RPC batch is not supported"), 400)
                return None
            return msg

        def _handle_streamable(self) -> None:
            if not self._origin_ok():
                self._send_json(MCPServer._error(None, -32600, "Origin not allowed"), 403)
                return
            msg = self._read_json()
            if msg is None:
                return
            sid_header = self.headers.get("Mcp-Session-Id")
            method = str(msg.get("method") or "")
            if method == "initialize" or not sid_header:
                sid, srv = _new_session()
            else:
                sid, srv = _session(sid_header)
            response = srv.handle(msg)
            if srv.exiting:
                _drop_session(sid)
            if response is None:
                self._send_empty(202, sid)
                return
            accept = (self.headers.get("Accept") or "").lower()
            if "text/event-stream" in accept and "application/json" not in accept:
                body = ("event: message\ndata: " +
                        json.dumps(response, ensure_ascii=False) + "\n\n").encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("MCP-Protocol-Version", DEFAULT_PROTOCOL)
                self.send_header("Mcp-Session-Id", sid)
                self._cors()
                self.end_headers()
                self.wfile.write(body)
            else:
                self._send_json(response, 200, sid)

        def _handle_legacy_sse(self) -> None:
            if not self._origin_ok():
                self._send_json(MCPServer._error(None, -32600, "Origin not allowed"), 403)
                return
            sid, srv = _new_session()
            q: "queue.Queue[Optional[Dict[str, Any]]]" = queue.Queue()
            with lock:
                sse_queues[sid] = q
            try:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-cache, no-transform")
                self.send_header("Connection", "keep-alive")
                self.send_header("X-Accel-Buffering", "no")
                self.send_header("MCP-Protocol-Version", DEFAULT_PROTOCOL)
                self.send_header("Mcp-Session-Id", sid)
                self._cors()
                self.end_headers()
                endpoint = f"/messages?sessionId={sid}"
                self.wfile.write(f"event: endpoint\ndata: {endpoint}\n\n".encode("utf-8"))
                self.wfile.flush()
                self.close_connection = False
                while True:
                    try:
                        item = q.get(timeout=15)
                    except queue.Empty:
                        self.wfile.write(b": keepalive\n\n")
                        self.wfile.flush()
                        continue
                    if item is None:
                        break
                    payload = json.dumps(item, ensure_ascii=False)
                    self.wfile.write(f"event: message\ndata: {payload}\n\n".encode("utf-8"))
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                _drop_session(sid)

        def _handle_legacy_message(self) -> None:
            if not self._origin_ok():
                self._send_json(MCPServer._error(None, -32600, "Origin not allowed"), 403)
                return
            parsed = urllib.parse.urlparse(self.path)
            sid = urllib.parse.parse_qs(parsed.query).get("sessionId", [None])[0]
            if not sid:
                self._send_json(MCPServer._error(None, -32600, "Missing sessionId"), 400)
                return
            with lock:
                srv = sessions.get(sid)
                q = sse_queues.get(sid)
            if srv is None or q is None:
                self._send_json(MCPServer._error(None, -32000, "Unknown or expired session"), 404)
                return
            msg = self._read_json()
            if msg is None:
                return
            response = srv.handle(msg)
            if response is not None:
                q.put(response)
            self._send_empty(202, sid)

        # -- HTTP verbs ---------------------------------------------------
        def do_OPTIONS(self):  # noqa: N802
            if not self._origin_ok():
                self._send_empty(403)
                return
            self._send_empty(204)

        def do_GET(self):  # noqa: N802
            path = urllib.parse.urlparse(self.path).path
            if path in ("/health", "/"):
                self._send_json(config.status())
            elif path == "/sse":
                self._handle_legacy_sse()
            elif path == "/mcp":
                self.send_response(405)
                self.send_header("Allow", "POST, DELETE, OPTIONS")
                self.send_header("Content-Length", "0")
                self.end_headers()
            else:
                self.send_error(404)

        def do_POST(self):  # noqa: N802
            path = urllib.parse.urlparse(self.path).path
            if path in ("/mcp", "/"):
                self._handle_streamable()
            elif path == "/messages":
                self._handle_legacy_message()
            else:
                self.send_error(404)

        def do_DELETE(self):  # noqa: N802
            path = urllib.parse.urlparse(self.path).path
            if path == "/mcp":
                _drop_session(self.headers.get("Mcp-Session-Id"))
                self._send_empty(204)
            else:
                self.send_error(404)

        def log_message(self, fmt, *args):  # noqa: A003
            _log(fmt % args)

    httpd = ThreadingHTTPServer((host, port), Handler)
    httpd.daemon_threads = True
    _log(f"HTTP MCP server listening on http://{host}:{port}/mcp "
         f"(legacy SSE: http://{host}:{port}/sse)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


def main(argv: Optional[List[str]] = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if "--http" in args:
        port = 8790
        i = args.index("--http")
        if i + 1 < len(args):
            try:
                port = int(args[i + 1])
            except ValueError:
                pass
        run_http(port=port)
    else:
        run_stdio()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
