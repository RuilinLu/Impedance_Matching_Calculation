"""MCP (Model Context Protocol) server over stdio / optional local HTTP.

MCP clients such as ZCode can connect with:

    python app/run_mcp.py

The server exposes the matching engine as 15 tools plus documentation resources.
Only JSON-RPC messages are written to stdout; logs go to stderr.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from typing import Any, Dict, Iterable, List, Optional

from . import config, engine, knowledge, tools

PROTOCOL_VERSIONS = {"2024-11-05", "2025-03-26", "2025-06-18"}
DEFAULT_PROTOCOL = "2025-06-18"

INSTRUCTIONS = (
    "这是「智配芯生 · ImpedanceMCP」微波阻抗匹配计算与仿真服务器。"
    "任何涉及频率、负载阻抗、L/C 元件值、VSWR、带宽、耐压的具体问题，"
    "请先调用 design_matching_network / evaluate_network / scan_matching_range 等工具，"
    "再基于工具返回值解释。topology=auto 会自动比较 L/T/π 五种拓扑。"
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
                    "name": "impedance-mcp",
                    "title": "智配芯生 · 微波阻抗匹配 MCP",
                    "version": config.VERSION,
                    "websiteUrl": "https://github.com/RuilinLu/Impedance_Matching_Calculation",
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
             "description": "版本、LLM、MATLAB、原版 exe 与 MCP 状态",
             "mimeType": "application/json"},
        ]

    def _read_resource(self, uri: str) -> Any:
        if uri == "impedance://catalog":
            text = json.dumps(engine.catalog(), ensure_ascii=False, indent=2)
            mime = "application/json"
        elif uri == "impedance://knowledge":
            parts = []
            for s in knowledge.all_sections():
                parts.append(f"## {s['title']}\n\n{s['text']}")
            text = "\n\n".join(parts)
            mime = "text/markdown"
        elif uri == "impedance://status":
            text = json.dumps(config.status(), ensure_ascii=False, indent=2)
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
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    server = MCPServer()

    class Handler(BaseHTTPRequestHandler):
        server_version = "ImpedanceMCP/" + config.VERSION

        def do_GET(self):  # noqa: N802
            if self.path in ("/health", "/"):
                body = json.dumps(config.status(), ensure_ascii=False).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_error(404)

        def do_POST(self):  # noqa: N802
            if self.path not in ("/mcp", "/"):
                self.send_error(404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self.send_error(400)
                return
            if length > 2_000_000:
                self.send_error(413)
                return
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                self._json(MCPServer._error(None, -32700, "Parse error"))
                return
            response = server.handle(msg)
            if response is None:
                self.send_response(202)
                self.end_headers()
            else:
                self._json(response)

        def _json(self, payload: Dict[str, Any]):
            body = json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):  # noqa: A003
            _log(fmt % args)

    httpd = ThreadingHTTPServer((host, port), Handler)
    _log(f"HTTP MCP server listening on http://{host}:{port}/mcp")
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
