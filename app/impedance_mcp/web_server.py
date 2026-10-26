"""Local web application server for the ImpedanceMCP desktop shell."""

from __future__ import annotations

import json
import mimetypes
import os
import sys
import threading
import traceback
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from . import agent, attachments, config, engine, knowledge, llm, matlab_bridge, providers, reports, tools

MAX_BODY = 42 * 1024 * 1024  # base64 uploads


def _json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "ImpedanceMCP/" + config.VERSION
    protocol_version = "HTTP/1.1"

    # -- helpers ----------------------------------------------------------
    def _send(self, status: int, body: bytes, ctype: str,
              extra: Optional[Dict[str, str]] = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, payload: Any, status: int = 200) -> None:
        self._send(status, _json_bytes(payload), "application/json; charset=utf-8")

    def _error(self, message: str, hint: str = "", status: int = 400,
               code: str = "error") -> None:
        self._json({"ok": False, "error_code": code, "message": message,
                    "hint": hint}, status)

    def _body(self) -> Dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("无效的 Content-Length")
        if length <= 0:
            return {}
        if length > MAX_BODY:
            raise ValueError("请求体过大（上限 42 MB）")
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"请求体不是合法 JSON：{exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("请求体必须是 JSON 对象")
        return data

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
        sys.stderr.write("[web] " + (fmt % args) + "\n")

    # -- routing ----------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/status":
                st = config.status()
                st["web_url"] = f"http://{self.headers.get('Host', '127.0.0.1')}"
                st["mcp"]["running"] = True
                return self._json(st)
            if path == "/api/config":
                return self._json({"ok": True, "config": config.public_config()})
            if path == "/api/catalog":
                return self._json({"ok": True, **engine.catalog()})
            if path == "/api/providers":
                data = providers.load()
                return self._json({"ok": True, **data})
            if path == "/api/presets":
                return self._json(tools.list_presets({}))
            if path == "/api/mcp/config":
                return self._json({"ok": True, "servers": config.mcp_client_config(),
                                   "snippet": json.dumps({"mcp": {"servers": config.mcp_client_config()}},
                                                         ensure_ascii=False, indent=2)})
            if path == "/api/knowledge":
                q = urllib.parse.parse_qs(parsed.query).get("q", [""])[0]
                return self._json(knowledge.search(q))
            if path == "/api/health":
                return self._json({"ok": True, "version": config.VERSION})
            if path.startswith("/api/report/"):
                return self._serve_report(path.split("/")[-1])
            if path in ("/", "/index.html"):
                return self._serve_static("index.html")
            if path.startswith("/assets/"):
                return self._serve_static(path[len("/assets/"):])
            if path == "/favicon.ico":
                return self._serve_static("favicon.svg")
            return self._serve_static(path.lstrip("/"))
        except BrokenPipeError:
            return
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(traceback.format_exc())
            return self._error(str(exc), status=500, code="server_error")

    def do_HEAD(self) -> None:  # noqa: N802
        return self.do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/chat":
                return self._chat()
            if path == "/api/config":
                return self._save_config()
            if path == "/api/config/test":
                return self._test_llm()
            if path == "/api/models":
                return self._models()
            if path == "/api/design":
                return self._design()
            if path == "/api/scan":
                return self._scan()
            if path == "/api/evaluate":
                return self._evaluate()
            if path == "/api/stress":
                return self._stress()
            if path == "/api/bandwidth":
                return self._bandwidth()
            if path == "/api/suggest":
                return self._suggest()
            if path == "/api/convert":
                return self._convert()
            if path == "/api/upload":
                return self._upload()
            if path == "/api/report":
                return self._report()
            if path == "/api/matlab/open":
                return self._json(matlab_bridge.launch_classic_app())
            if path == "/api/matlab/verify":
                return self._matlab_verify()
            if path == "/api/matlab/status":
                return self._json(matlab_bridge.status())
            return self._error("未知接口", status=404, code="not_found")
        except BrokenPipeError:
            return
        except ValueError as exc:
            return self._error(str(exc), status=400, code="bad_request")
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(traceback.format_exc())
            return self._error(str(exc), status=500, code="server_error")

    # -- static -----------------------------------------------------------
    def _serve_static(self, rel: str) -> None:
        rel = urllib.parse.unquote(rel)
        target = (config.WEB_DIR / rel).resolve()
        try:
            target.relative_to(config.WEB_DIR.resolve())
        except ValueError:
            return self._error("非法路径", status=403, code="forbidden")
        if not target.is_file():
            return self._error("文件不存在", status=404, code="not_found")
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        if target.suffix == ".js":
            ctype = "text/javascript; charset=utf-8"
        elif target.suffix in (".html", ".css", ".svg"):
            ctype += "; charset=utf-8"
        self._send(200, target.read_bytes(), ctype)

    def _serve_report(self, name: str) -> None:
        safe = Path(urllib.parse.unquote(name)).name
        if not safe.startswith("impedance_report_") or not safe.endswith((".html", ".md")):
            return self._error("非法报告文件名", status=403, code="forbidden")
        path = (config.REPORT_DIR / safe).resolve()
        if not path.is_file() or config.REPORT_DIR.resolve() not in path.parents:
            return self._error("报告不存在", status=404, code="not_found")
        ctype = "text/html; charset=utf-8" if path.suffix == ".html" else "text/markdown; charset=utf-8"
        self._send(200, path.read_bytes(), ctype,
                   {"Content-Disposition": f'inline; filename="{safe}"'})

    # -- config / LLM -----------------------------------------------------
    def _save_config(self) -> None:
        data = self._body()
        if "llm" in data and isinstance(data["llm"], dict):
            llm_data = data["llm"]
            base = llm_data.get("base_url")
            if base:
                try:
                    llm.normalize_base(base, llm_data.get("api_style", "openai"),
                                       llm_data.get("chat_path", ""))
                except llm.LLMError as exc:
                    return self._error(exc.message, exc.hint, 400, "invalid_base_url")
        cfg = config.save_config(data)
        return self._json({"ok": True, "config": config.public_config(cfg),
                           "summary": "设置已保存。"})

    def _merged_config(self) -> Dict[str, Any]:
        data = self._body()
        posted = data.get("llm") if isinstance(data.get("llm"), dict) else None
        cfg = config.load_config()
        if posted:
            key = posted.get("api_key")
            if key in ("", "***", "******"):
                posted.pop("api_key", None)
            cfg = config.deep_merge(cfg, {"llm": posted})
        return cfg

    def _test_llm(self) -> None:
        cfg = self._merged_config()
        try:
            result = llm.test_connection(cfg)
            return self._json(result)
        except llm.LLMError as exc:
            return self._error(exc.message, exc.hint, 400, "llm_error")

    def _models(self) -> None:
        cfg = self._merged_config()
        try:
            return self._json(llm.list_models(cfg))
        except llm.LLMError as exc:
            return self._error(exc.message, exc.hint, 400, "llm_error")

    # -- design -----------------------------------------------------------
    def _design(self) -> None:
        data = self._body()
        try:
            result = engine.design_network(
                data.get("topology", "auto"),
                float(data["frequency_mhz"]),
                float(data["load_r"]),
                float(data.get("load_x", 0.0)),
                float(data.get("z0", 50.0)),
                L_uh=None if data.get("L_uh") in (None, "", 0) else float(data["L_uh"]),
                c3_pf=None if data.get("c3_pf") in (None, "", 0) else float(data["c3_pf"]),
                power_w=float(data.get("power_w", 1.0)),
            )
            return self._json({"ok": True, **result})
        except engine.DesignError as exc:
            return self._json({"ok": False, "error_code": exc.code,
                               "message": exc.message, "hint": exc.hint}, 200)

    def _scan(self) -> None:
        data = self._body()
        r = engine.scan_matchable_range(
            data["topology"], float(data["frequency_mhz"]),
            float(data.get("z0", 50.0)), float(data["L_uh"]),
            data.get("c1_range_pf"), data.get("c2_range_pf"), data.get("c3_range_pf"),
            int(data.get("steps", 45)),
        )
        return self._json(r)

    def _evaluate(self) -> None:
        data = self._body()
        r = engine.evaluate(
            data["topology"], float(data["frequency_mhz"]),
            float(data["load_r"]), float(data.get("load_x", 0.0)),
            float(data["L_uh"]), float(data["C1_pF"]), float(data["C2_pF"]),
            float(data.get("C3_pF", 0.0)), float(data.get("z0", 50.0)),
            float(data.get("power_w", 1.0)),
        )
        return self._json(r)

    def _stress(self) -> None:
        data = self._body()
        r = engine.voltage_stress(
            data["topology"], float(data["frequency_mhz"]),
            float(data["load_r"]), float(data.get("load_x", 0.0)),
            float(data["L_uh"]), float(data["C1_pF"]), float(data["C2_pF"]),
            float(data.get("C3_pF", 0.0)), float(data.get("power_w", 10.0)),
            float(data.get("z0", 50.0)),
            None if data.get("rated_voltage") in (None, "", 0)
            else float(data["rated_voltage"]),
        )
        return self._json(r)

    def _bandwidth(self) -> None:
        data = self._body()
        comps = {"L_uH": float(data["L_uh"]), "C1_pF": float(data["C1_pF"]),
                 "C2_pF": float(data["C2_pF"]), "C3_pF": float(data.get("C3_pF", 0.0))}
        r = engine.bandwidth(
            data["topology"], float(data["frequency_mhz"]),
            complex(float(data["load_r"]), float(data.get("load_x", 0.0))),
            comps, float(data.get("z0", 50.0)),
            float(data.get("vswr_limit", 2.0)), float(data.get("span", 0.6)),
        )
        r["ok"] = True
        return self._json(r)

    def _suggest(self) -> None:
        data = self._body()
        r = engine.suggest_topologies(
            float(data["frequency_mhz"]),
            complex(float(data["load_r"]), float(data.get("load_x", 0.0))),
            float(data.get("z0", 50.0)),
        )
        return self._json({"ok": True, "alternatives": r})

    def _convert(self) -> None:
        data = self._body()
        mode = str(data.get("mode", "z2y")).lower()
        z = complex(float(data["real"]), float(data.get("imag", 0.0)))
        if mode == "z2y":
            y = engine.z_to_y(z)
            return self._json({"ok": True, "mode": "z2y", "z": [z.real, z.imag],
                               "y": [y.real, y.imag],
                               "display": f"Y = {engine.fmt_complex(y)} S"})
        z2 = engine.y_to_z(z)
        return self._json({"ok": True, "mode": "y2z", "y": [z.real, z.imag],
                           "z": [z2.real, z2.imag],
                           "display": f"Z = {engine.fmt_complex(z2)} Ω"})

    def _upload(self) -> None:
        data = self._body()
        name = str(data.get("name") or "upload")
        content = data.get("content_base64") or data.get("content") or ""
        info = attachments.save_upload(name, content)
        info.pop("text", None)  # the server keeps the text; the UI gets a preview
        return self._json(info)

    def _report(self) -> None:
        data = self._body()
        d = engine.design_network(
            data.get("topology", "auto"), float(data["frequency_mhz"]),
            float(data["load_r"]), float(data.get("load_x", 0.0)),
            float(data.get("z0", 50.0)),
            L_uh=None if data.get("L_uh") in (None, "", 0) else float(data["L_uh"]),
            c3_pf=None if data.get("c3_pf") in (None, "", 0) else float(data["c3_pf"]),
            power_w=float(data.get("power_w", 1.0)),
        )
        # If the client sends the exact solved C1/C2, use them verbatim so the
        # report matches the screen instead of re-solving from a rounded L.
        if data.get("C1_pF") and data.get("C2_pF"):
            comps = {
                "L_uH": float(data["L_uh"]),
                "C1_pF": float(data["C1_pF"]),
                "C2_pF": float(data["C2_pF"]),
                "C3_pF": float(data.get("c3_pf") or 0.0),
            }
            zl = complex(float(data["load_r"]), float(data.get("load_x", 0.0)))
            z0 = float(data.get("z0", 50.0))
            fm = float(data["frequency_mhz"])
            ver = engine.analyze_network(d["topology"], fm, zl, comps, z0)
            d["components"] = comps
            d["verification"] = ver
            d["input_impedance"] = ver["input_impedance"]
            d["input_impedance_display"] = engine.fmt_complex(
                complex(ver["input_impedance"]["re"], ver["input_impedance"]["im"]))
            d["vswr"] = ver["vswr"]
            d["s11_db"] = ver["s11_db"]
            d["return_loss_db"] = ver["return_loss_db"]
            d["steps"] = engine.build_steps(d["topology"], fm, zl, comps, z0)
            d["bandwidth"] = engine.bandwidth(d["topology"], fm, zl, comps, z0)
            d["sensitivity"] = engine.sensitivity(d["topology"], fm, zl, comps, z0)
        fmt = str(data.get("format", "html")).lower()
        path = reports.generate(d, fmt=fmt, note=str(data.get("note", "")))
        return self._json({"ok": True, "path": str(path),
                           "url": f"/api/report/{path.name}",
                           "format": fmt,
                           "summary": f"报告已生成：{path.name}"})

    def _matlab_verify(self) -> None:
        data = self._body()
        r = matlab_bridge.run_matlab_design(
            data["topology"], float(data["frequency_mhz"]),
            float(data["load_r"]), float(data.get("load_x", 0.0)),
            None if data.get("L_uh") in (None, "", 0) else float(data["L_uh"]),
            None if data.get("c3_pf") in (None, "", 0) else float(data["c3_pf"]),
            float(data.get("z0", 50.0)),
        )
        return self._json(r)

    # -- chat SSE ---------------------------------------------------------
    def _chat(self) -> None:
        data = self._body()
        messages = data.get("messages") or []
        attach = data.get("attachments") or []
        cfg = config.load_config()
        model = str(data.get("model") or "").strip()
        if model and len(model) <= 80:
            cfg["llm"]["model"] = model
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        lock = threading.Lock()

        def emit(event: str, payload: Dict[str, Any]) -> None:
            with lock:
                body = f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
                self.wfile.write(body.encode("utf-8"))
                self.wfile.flush()

        try:
            agent.run_chat(cfg, messages, attach, emit)
        except llm.LLMError as exc:
            emit("error", {"message": exc.message, "hint": exc.hint,
                           "status": exc.status})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(traceback.format_exc())
            try:
                emit("error", {"message": f"智能体运行失败：{exc}",
                               "hint": "请查看终端日志，或检查模型服务配置。"})
            except Exception:
                pass
        finally:
            self.close_connection = True


def create_server(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    config.ensure_dirs()
    httpd = ThreadingHTTPServer((host, port), Handler)
    httpd.daemon_threads = True
    return httpd


def main(argv: Optional[list] = None) -> int:
    import argparse
    import webbrowser

    parser = argparse.ArgumentParser(description="ImpedanceMCP desktop shell")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--find-port", action="store_true", default=True)
    args = parser.parse_args(argv)

    httpd = None
    last_error = None
    for offset in range(0, 12):
        try:
            httpd = create_server(args.host, args.port + offset)
            break
        except OSError as exc:
            last_error = exc
            continue
    if httpd is None:
        raise SystemExit(f"无法启动本地服务：{last_error}")
    port = httpd.server_address[1]
    url = f"http://{args.host}:{port}/"
    print(f"\n  智配芯生 · ImpedanceMCP v{config.VERSION}")
    print(f"  Web 界面: {url}")
    print(f"  MCP stdio: python {config.PROJECT_ROOT / 'app' / 'run_mcp.py'}")
    print("  按 Ctrl+C 退出\n")
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
