"""Local HTTP API and static server for the desktop shell."""

from __future__ import annotations

import json
import mimetypes
import re
import threading
import time
import traceback
import urllib.parse
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from . import (agent, attachments, code_docs, config, docs_hub, engine, knowledge,
               library, llm, media, providers, reports, tools, update_check, usage)

MAX_BODY = 160 * 1024 * 1024  # base64 textbook uploads
JSON_LIMIT = 64 * 1024 * 1024
MAX_CHUNK = 8 * 1024 * 1024
MAX_CHUNK_TOTAL = 120 * 1024 * 1024
CHUNK_ID_PATTERN = re.compile(r"^[a-f0-9]{16,64}$")


def _inline_disposition(name: str) -> str:
    suffix = Path(name).suffix or ".html"
    quoted = urllib.parse.quote(name, safe="")
    return f'inline; filename="document{suffix}"; filename*=UTF-8\'\'{quoted}'


def _json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "ImpedanceMatchingAI/" + config.VERSION
    protocol_version = "HTTP/1.1"

    # -- helpers ----------------------------------------------------------
    def _send(self, status: int, body: bytes, ctype: str,
              extra: Optional[Dict[str, str]] = None) -> None:
        try:
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cache-Control", "no-store")
            for key, value in (extra or {}).items():
                self.send_header(key, value)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            # The client disconnected while we were replying; this is normal
            # under bursty load and must not be logged as a 500.
            self.close_connection = True

    def _json(self, payload: Any, status: int = 200) -> None:
        self._send(status, _json_bytes(payload), "application/json; charset=utf-8")

    def _error(self, message: str, hint: str = "", status: int = 400,
               code: str = "error") -> None:
        self._json({"ok": False, "error_code": code, "message": message,
                    "hint": hint}, status)

    def _body(self) -> Dict[str, Any]:
        if getattr(self, "_body_cache", None) is not None:
            return self._body_cache
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("无效的 Content-Length")
        if length <= 0:
            self._body_cache = {}
            return self._body_cache
        if length > MAX_BODY:
            raise ValueError(f"请求体过大（上限 {MAX_BODY // 1024 // 1024} MB）")
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"请求体不是合法 JSON：{exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("请求体必须是 JSON 对象")
        self._body_cache = data
        return data

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
        try:
            import sys
            sys.stderr.write("[web] " + (fmt % args) + "\n")
        except Exception:
            pass

    def _query(self) -> Dict[str, str]:
        parsed = urllib.parse.urlparse(self.path)
        return {key: values[0] for key, values in
                urllib.parse.parse_qs(parsed.query).items()}

    # -- routing ----------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/status":
                state = config.status()
                state["web_url"] = f"http://{self.headers.get('Host', '127.0.0.1')}"
                state["mcp"]["running"] = True
                try:
                    state["library"] = library.status()
                except Exception:
                    state["library"] = {}
                return self._json(state)
            if path == "/api/config":
                return self._json({"ok": True, "config": config.public_config()})
            if path == "/api/catalog":
                return self._json({"ok": True, **engine.catalog()})
            if path == "/api/providers":
                data = providers.load()
                data["summary"] = providers.update_summary()
                return self._json({"ok": True, **data})
            if path == "/api/providers/summary":
                return self._json(providers.update_summary())
            if path == "/api/presets":
                return self._json(tools.list_presets({}))
            if path == "/api/mcp/config":
                return self._json({"ok": True, "servers": config.mcp_client_config(),
                                   "snippet": json.dumps(
                                       {"mcp": {"servers": config.mcp_client_config()}},
                                       ensure_ascii=False, indent=2)})
            if path == "/api/knowledge":
                return self._json(knowledge.search(self._query().get("q", "")))
            if path == "/api/health":
                return self._json({"ok": True, "version": config.VERSION})
            if path == "/api/docs/list":
                return self._json(docs_hub.list_docs(self._query().get("lang", "zh")))
            if path == "/api/docs/get":
                return self._json(docs_hub.get_doc(
                    self._query().get("category", "features"),
                    self._query().get("lang", "zh")))
            if path == "/api/docs/search":
                query = self._query()
                return self._json(docs_hub.search_docs(
                    query.get("q", ""), category=query.get("category") or None,
                    lang=query.get("lang", "zh"),
                    fuzzy=query.get("fuzzy", "1") not in ("0", "false"),
                    limit=int(query.get("limit", "60") or 60)))
            if path == "/api/library/status":
                state = library.status()
                if (state.get("docs", 0) == 0 and not state.get("running")
                        and config.load_config().get("library", {}).get("auto_index", True)):
                    state["started"] = True
                    library.start_index()
                return self._json(state)
            if path == "/api/library/sources":
                return self._json(self._library_sources_payload())
            if path == "/api/update/progress":
                return self._json({"ok": True, **update_check.download_progress()})
            if path == "/api/update/check":
                query = self._query()
                result = update_check.check(
                    force=query.get("force", "0") not in ("0", "false", ""),
                    use_model=query.get("use_model", "1") not in ("0", "false"))
                return self._json(result)
            if path == "/api/library/docs":
                return self._json({"ok": True, "documents": library.doc_list()})
            if path == "/api/library/doc":
                return self._json(library.doc_info(int(self._query().get("id", "0") or 0)))
            if path == "/api/library/toc":
                info = library.doc_info(int(self._query().get("id", "0") or 0))
                return self._json({"ok": info.get("ok"), "toc": info.get("toc", []),
                                   "title": info.get("title", "")})
            if path == "/api/library/page":
                query = self._query()
                data = library.render_page(
                    int(query.get("doc", "0") or 0),
                    int(query.get("page", "1") or 1),
                    float(query.get("zoom", "1") or 1))
                return self._send(200, data, "image/png")
            if path == "/api/library/crop":
                query = self._query()
                rects = []
                try:
                    raw_rects = json.loads(query.get("rects", "[]"))
                    for rect in raw_rects[:40]:
                        if isinstance(rect, list) and len(rect) == 4:
                            rects.append([max(0.0, min(1.0, float(x))) for x in rect])
                except Exception:
                    rects = []
                data = library.crop_page(
                    int(query.get("doc", "0") or 0),
                    int(query.get("page", "1") or 1),
                    rects, dpi=int(query.get("dpi", "220") or 220))
                return self._send(200, data, "image/png")
            if path == "/api/library/page_info":
                query = self._query()
                return self._json(library.page_info(
                    int(query.get("doc", "0") or 0),
                    int(query.get("page", "1") or 1),
                    query.get("lang", "zh")))
            if path == "/api/library/search":
                query = self._query()
                return self._json(library.search(
                    query.get("q", ""),
                    doc_id=int(query["doc_id"]) if query.get("doc_id") else None,
                    limit=int(query.get("limit", "24") or 24),
                    fuzzy=query.get("fuzzy", "1") not in ("0", "false")))
            if path == "/api/usage/summary":
                return self._json(usage.summary())
            if path.startswith("/api/media/"):
                return self._serve_media(path.split("/")[-1])
            if path.startswith("/api/report/"):
                return self._serve_report(path.split("/")[-1])
            if path in ("/", "/index.html"):
                return self._serve_static("index.html")
            if path == "/favicon.ico":
                return self._serve_static("favicon.svg")
            return self._serve_static(path.lstrip("/"))
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            self.close_connection = True
            return
        except ValueError as exc:
            if path.startswith("/api/library/page") or path.startswith("/api/library/crop"):
                return self._error(str(exc), status=404, code="not_found")
            return self._error(str(exc), status=400, code="bad_request")
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            return self._error(str(exc), status=500, code="server_error")

    def do_HEAD(self) -> None:  # noqa: N802
        return self.do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        self._body_cache = None
        try:
            # Raw binary chunk upload: do not try to decode it as JSON.
            if path == "/api/upload/chunk":
                return self._upload_chunk()
            # Always consume the request body before dispatching.  Otherwise a
            # route that ignores the body leaves "{}" in the keep-alive socket
            # and the next request line becomes "{}GET ..." (HTTP 501).
            self._body()
            routes = {
                "/api/chat": self._chat,
                "/api/config": self._save_config,
                "/api/config/test": self._test_llm,
                "/api/models": self._models,
                "/api/connections/activate": self._connections_activate,
                "/api/connections/delete": self._connections_delete,
                "/api/design": self._design,
                "/api/scan": self._scan,
                "/api/scan/stream": self._scan_stream,
                "/api/evaluate": self._evaluate,
                "/api/stress": self._stress,
                "/api/stress/stream": self._stress_stream,
                "/api/bandwidth": self._bandwidth,
                "/api/suggest": self._suggest,
                "/api/convert": self._convert,
                "/api/upload": self._upload,
                "/api/upload/init": self._upload_init,
                "/api/upload/complete": self._upload_complete,
                "/api/upload-text": self._upload_text,
                "/api/report": self._report,
                "/api/docs/ai_search": self._docs_ai_search,
                "/api/library/index": self._library_index,
                "/api/library/sources": self._library_sources_save,
                "/api/library/ocr": self._library_ocr,
                "/api/library/ocr_book": self._library_ocr_book,
                "/api/library/translate": self._library_translate,
                "/api/library/upload": self._library_upload,
                "/api/library/ai_search": self._library_ai_search,
                "/api/providers/update": self._providers_update,
                "/api/providers/rollback": self._providers_rollback,
                "/api/providers/reset": self._providers_reset,
                "/api/usage/clear": self._usage_clear,
                "/api/update/check": self._update_check,
                "/api/update/download": self._update_download,
                "/api/update/install": self._update_install,
                "/api/update/skip": self._update_skip,
            }
            handler = routes.get(path)
            if handler:
                return handler()
            return self._error("未知接口", status=404, code="not_found")
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            self.close_connection = True
            return
        except (KeyError, TypeError) as exc:
            return self._error(f"参数错误：{exc}", "请检查必填字段与数值类型。",
                               status=400, code="bad_request")
        except ValueError as exc:
            return self._error(str(exc), status=400, code="bad_request")
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            return self._error(str(exc), status=500, code="server_error")

    # -- static / reports -------------------------------------------------
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
        elif target.suffix in (".html", ".css", ".svg", ".json"):
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
                   {"Content-Disposition": _inline_disposition(safe)})

    def _serve_media(self, name: str) -> None:
        path = media.resolve(urllib.parse.unquote(name))
        if path is None:
            return self._error("媒体文件不存在", status=404, code="not_found")
        quoted = urllib.parse.quote(path.name, safe="")
        disposition = (f'inline; filename="media{path.suffix}"; '
                       f"filename*=UTF-8''{quoted}")
        self._send(200, path.read_bytes(), media.content_type(path), {
            "Content-Disposition": disposition,
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; img-src data:",
        })

    # -- config / LLM -----------------------------------------------------
    def _save_config(self) -> None:
        data = self._body()
        if "llm" in data and isinstance(data["llm"], dict):
            llm_data = data["llm"]
            base = llm_data.get("base_url")
            if base:
                try:
                    llm.normalize_base(base, llm_data.get("protocol") or llm_data.get("api_style", "openai"),
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
        connection_id = str(data.get("connection_id") or "").strip()
        if connection_id:
            try:
                cfg = config.cfg_for_connection(cfg, connection_id)
            except ValueError as exc:
                raise ValueError(str(exc)) from exc
        if posted:
            key = posted.get("api_key")
            if key in ("", "***", "******"):
                posted.pop("api_key", None)
            if not connection_id and not posted.get("api_key"):
                target_provider = str(posted.get("provider") or "")
                target_base = str(posted.get("base_url") or "").rstrip("/").lower()
                for candidate in config.list_connections(cfg):
                    if (str(candidate.get("provider") or "") == target_provider
                            and str(candidate.get("base_url") or "").rstrip("/").lower()
                            == target_base):
                        cfg = config.cfg_for_connection(
                            cfg, str(candidate.get("id") or ""),
                            str(posted.get("model") or ""))
                        break
            cfg = config.deep_merge(cfg, {"llm": posted})
        return cfg

    def _test_llm(self) -> None:
        cfg = self._merged_config()
        try:
            return self._json(llm.test_connection(cfg))
        except llm.LLMError as exc:
            return self._error(exc.message, exc.hint, 400, "llm_error")

    def _models(self) -> None:
        cfg = self._merged_config()
        try:
            result = llm.list_models(cfg)
        except llm.LLMError as exc:
            return self._error(exc.message, exc.hint, 400, "llm_error")
        cid = str(cfg.get("llm", {}).get("active_connection") or "")
        models = result.get("models") or []
        if cid and models:
            try:
                config.upsert_connection(cfg, {
                    "id": cid,
                    "provider": cfg["llm"].get("provider", ""),
                    "provider_name": cfg["llm"].get("provider_name", ""),
                    "protocol": cfg["llm"].get("protocol", "openai"),
                    "base_url": cfg["llm"].get("base_url", ""),
                    "model": cfg["llm"].get("model", ""),
                    "models": models,
                }, activate=False)
                config.save_config({"llm": {"connections": cfg["llm"]["connections"],
                                            "active_connection": cid}})
            except Exception:
                pass
        return self._json(result)

    def _connections_activate(self) -> None:
        data = self._body()
        cfg = config.load_config()
        try:
            conn = config.activate_connection(
                cfg, str(data.get("id") or ""), str(data.get("model") or ""))
        except ValueError as exc:
            return self._error(str(exc), status=404, code="not_found")
        merged = config.save_config({"llm": cfg.get("llm") or {}})
        status = config.llm_status(merged)
        return self._json({"ok": True, "connection": config.public_connection(conn),
                           "config": config.public_config(merged), "llm": status})

    def _connections_delete(self) -> None:
        data = self._body()
        cfg = config.load_config()
        if not config.delete_connection(cfg, str(data.get("id") or "")):
            return self._error("连接不存在", status=404, code="not_found")
        merged = config.save_config({"llm": cfg.get("llm") or {}})
        return self._json({"ok": True, "config": config.public_config(merged),
                           "llm": config.llm_status(merged)})

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
        try:
            result = engine.scan_matchable_range(
                data["topology"], float(data["frequency_mhz"]),
                float(data.get("z0", 50.0)), float(data["L_uh"]),
                data.get("c1_range_pf"), data.get("c2_range_pf"), data.get("c3_range_pf"),
                int(data.get("steps", 45)),
                int(data.get("max_points", 12000) or 12000),
                int(data.get("points_budget") or data.get("sim_points") or 0),
            )
            return self._json(result)
        except engine.DesignError as exc:
            return self._json({"ok": False, "error_code": exc.code,
                               "message": exc.message, "hint": exc.hint}, 200)

    def _evaluate(self) -> None:
        data = self._body()
        result = engine.evaluate(
            data["topology"], float(data["frequency_mhz"]),
            float(data["load_r"]), float(data.get("load_x", 0.0)),
            float(data["L_uh"]), float(data["C1_pF"]), float(data["C2_pF"]),
            float(data.get("C3_pF", 0.0)), float(data.get("z0", 50.0)),
            float(data.get("power_w", 1.0)),
        )
        return self._json(result)

    def _stress(self) -> None:
        data = self._body()
        result = engine.voltage_stress(
            data["topology"], float(data["frequency_mhz"]),
            float(data["load_r"]), float(data.get("load_x", 0.0)),
            float(data["L_uh"]), float(data["C1_pF"]), float(data["C2_pF"]),
            float(data.get("C3_pF", 0.0)), float(data.get("power_w", 10.0)),
            float(data.get("z0", 50.0)),
            None if data.get("rated_voltage") in (None, "", 0)
            else float(data["rated_voltage"]),
            sweep=bool(data.get("sweep", True)),
            sweep_points=int(data.get("sweep_points", 21)),
            frequency_span=float(data.get("frequency_span", 0.2)),
        )
        return self._json(result)

    def _bandwidth(self) -> None:
        data = self._body()
        comps = {"L_uH": float(data["L_uh"]), "C1_pF": float(data["C1_pF"]),
                 "C2_pF": float(data["C2_pF"]), "C3_pF": float(data.get("C3_pF", 0.0))}
        result = engine.bandwidth(
            data["topology"], float(data["frequency_mhz"]),
            complex(float(data["load_r"]), float(data.get("load_x", 0.0))),
            comps, float(data.get("z0", 50.0)),
            float(data.get("vswr_limit", 2.0)), float(data.get("span", 0.6)),
        )
        result["ok"] = True
        return self._json(result)

    def _suggest(self) -> None:
        data = self._body()
        result = engine.suggest_topologies(
            float(data["frequency_mhz"]),
            complex(float(data["load_r"]), float(data.get("load_x", 0.0))),
            float(data.get("z0", 50.0)),
        )
        return self._json({"ok": True, "alternatives": result})

    def _convert(self) -> None:
        data = self._body()
        mode = str(data.get("mode", "z2y")).lower()
        if mode not in ("z2y", "y2z"):
            return self._error("mode 必须是 z2y 或 y2z", status=400, code="bad_request")
        value = complex(float(data["real"]), float(data.get("imag", 0.0)))
        if mode == "z2y":
            result = engine.z_to_y(value)
            return self._json({"ok": True, "mode": "z2y",
                               "z": [value.real, value.imag],
                               "y": [result.real, result.imag],
                               "display": f"Y = {engine.fmt_complex(result)} S"})
        result = engine.y_to_z(value)
        return self._json({"ok": True, "mode": "y2z",
                           "y": [value.real, value.imag],
                           "z": [result.real, result.imag],
                           "display": f"Z = {engine.fmt_complex(result)} Ω"})

    def _upload(self) -> None:
        data = self._body()
        name = str(data.get("name") or "attachment")
        content = data.get("content_base64") or data.get("content") or ""
        info = attachments.save_upload(name, content)
        # Keep text/images in the server-side cache for the follow-up chat
        # call; only the wire payload is trimmed.
        public = dict(info)
        public.pop("text", None)
        public.pop("images", None)
        public.pop("path", None)
        return self._json(public)

    def _upload_text(self) -> None:
        data = self._body()
        info = attachments.save_text(str(data.get("text") or ""),
                                     str(data.get("name") or ""))
        public = dict(info)
        public.pop("text", None)
        public.pop("images", None)
        public.pop("path", None)
        return self._json(public)

    # -- progressive analysis --------------------------------------------
    def _sse_start(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

    def _sse_emit(self, event: str, payload: Dict[str, Any]) -> None:
        body = f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
        self.wfile.write(body.encode("utf-8"))
        self.wfile.flush()

    def _scan_stream(self) -> None:
        data = self._body()
        try:
            plan = engine.scan_plan(
                data["topology"], float(data["frequency_mhz"]),
                float(data.get("z0", 50.0)), float(data["L_uh"]),
                data.get("c1_range_pf"), data.get("c2_range_pf"),
                data.get("c3_range_pf"),
                steps=int(data.get("steps", 45)),
                points_budget=int(data.get("points_budget")
                                   or data.get("max_points") or 0),
            )
        except engine.DesignError as exc:
            return self._json({"ok": False, "error_code": exc.code,
                               "message": exc.message, "hint": exc.hint}, 200)
        self._sse_start()
        started = time.perf_counter()
        accumulator = engine.ScanAccumulator(plan["z0"], grid=160)
        batch = []
        try:
            self._sse_emit("meta", {
                "ok": True, "topology": plan["topology"],
                "total": plan["total"], "per_dimension": plan["per"],
                "grid_steps": plan["grid_steps"], "dims": plan["dims"],
                "frequency_mhz": plan["frequency_mhz"], "z0": plan["z0"],
            })
            for loads, connect in engine.iter_scan_groups(plan):
                raw = np.asarray(loads, dtype=np.complex128).ravel()
                accumulator.add(raw, connect=connect)
                valid = raw[np.isfinite(raw) & (raw.real > 0)]
                if valid.size:
                    gamma = (valid - plan["z0"]) / (valid + plan["z0"])
                    for point, g in zip(valid, gamma):
                        batch.append({"re": float(point.real), "im": float(point.imag),
                                      "g": {"re": float(g.real), "im": float(g.imag),
                                            "magnitude": float(abs(g))}})
                if len(batch) >= 500:
                    self._sse_emit("points", {
                        "points": batch,
                        "evaluated": accumulator.evaluated,
                        "valid": accumulator.valid,
                        "total": plan["total"],
                    })
                    batch = []
            if batch:
                self._sse_emit("points", {
                    "points": batch,
                    "evaluated": accumulator.evaluated,
                    "valid": accumulator.valid,
                    "total": plan["total"],
                })
            elapsed = int((time.perf_counter() - started) * 1000)
            result = accumulator.finish(plan, elapsed_ms=elapsed, limit_points=0)
            self._sse_emit("done", result)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            try:
                self._sse_emit("error", {"message": f"扫描失败：{exc}"})
            except Exception:
                pass
        finally:
            self.close_connection = True

    def _stress_stream(self) -> None:
        data = self._body()
        params = {
            "topology": data["topology"],
            "frequency_mhz": float(data["frequency_mhz"]),
            "load_r": float(data["load_r"]),
            "load_x": float(data.get("load_x", 0.0)),
            "L_uh": float(data["L_uh"]),
            "c1_pf": float(data["C1_pF"]),
            "c2_pf": float(data["C2_pF"]),
            "c3_pf": float(data.get("C3_pF", 0.0)),
            "power_w": float(data.get("power_w", 10.0)),
            "z0": float(data.get("z0", 50.0)),
            "rated_voltage": (None if data.get("rated_voltage") in (None, "", 0)
                              else float(data["rated_voltage"])),
            "sweep": bool(data.get("sweep", True)),
            "sweep_points": int(data.get("sweep_points", 21)),
            "frequency_span": float(data.get("frequency_span", 0.2)),
        }
        self._sse_start()
        try:
            self._sse_emit("meta", {
                "ok": True, "sweep_points": params["sweep_points"],
                "frequency_span": params["frequency_span"],
                "total": ((max(2, min(params["sweep_points"], 41)) ** 2) + 1
                          if params["sweep"] else 1),
            })

            def progress(info: Dict[str, Any]) -> None:
                self._sse_emit("progress", info)

            result = engine.voltage_stress(progress=progress, **params)
            self._sse_emit("done", result)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            try:
                self._sse_emit("error", {"message": f"耐压分析失败：{exc}"})
            except Exception:
                pass
        finally:
            self.close_connection = True

    # -- chunked uploads --------------------------------------------------
    def _chunk_paths(self, upload_id: str):
        if not CHUNK_ID_PATTERN.match(str(upload_id or "")):
            raise ValueError("无效的上传会话")
        base = config.UPLOAD_CHUNK_DIR.resolve()
        base.mkdir(parents=True, exist_ok=True)
        meta = (base / (upload_id + ".json")).resolve()
        part = (base / (upload_id + ".part")).resolve()
        if meta.parent != base or part.parent != base:
            raise ValueError("上传路径越界")
        return meta, part

    def _upload_init(self) -> None:
        data = self._body()
        name = str(data.get("name") or "attachment")[:200]
        size = int(data.get("size") or 0)
        if size <= 0:
            return self._error("文件为空", status=400, code="bad_request")
        if size > MAX_CHUNK_TOTAL:
            return self._error(
                f"文件过大（上限 {MAX_CHUNK_TOTAL // 1024 // 1024} MB）",
                status=413, code="too_large")
        config.ensure_dirs()
        cutoff = time.time() - 24 * 3600
        for stale in config.UPLOAD_CHUNK_DIR.glob("*"):
            try:
                if stale.is_file() and stale.stat().st_mtime < cutoff:
                    stale.unlink()
            except Exception:
                pass
        upload_id = uuid.uuid4().hex
        meta, part = self._chunk_paths(upload_id)
        meta.write_text(json.dumps({"name": name, "size": size, "received": 0,
                                    "created": time.time()}, ensure_ascii=False),
                        encoding="utf-8")
        part.touch()
        return self._json({"ok": True, "upload_id": upload_id, "size": size,
                           "chunk_size": 2 * 1024 * 1024})

    def _upload_chunk(self) -> None:
        query = self._query()
        upload_id = query.get("upload_id", "")
        try:
            meta_path, part_path = self._chunk_paths(upload_id)
        except ValueError as exc:
            return self._error(str(exc), status=400, code="bad_request")
        if not meta_path.is_file() or not part_path.is_file():
            return self._error("上传会话不存在或已过期", status=404, code="not_found")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self._error("无效的 Content-Length", status=400, code="bad_request")
        if length <= 0 or length > MAX_CHUNK:
            return self._error("分块大小无效", status=400, code="bad_request")
        raw = self.rfile.read(length)
        if len(raw) != length:
            return self._error("分块读取不完整", status=400, code="bad_request")
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            return self._error("上传会话元数据损坏", status=500, code="server_error")
        current = part_path.stat().st_size
        if current != int(meta.get("received") or 0):
            return self._error("分块顺序错误，请重新上传", status=409, code="conflict")
        if current + len(raw) > int(meta.get("size") or 0):
            return self._error("上传内容超过声明大小", status=413, code="too_large")
        with part_path.open("ab") as handle:
            handle.write(raw)
        meta["received"] = current + len(raw)
        meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        total = int(meta.get("size") or 0)
        return self._json({"ok": True, "received": meta["received"], "total": total,
                           "percent": round(100.0 * meta["received"] / max(1, total), 1)})

    def _upload_complete(self) -> None:
        data = self._body()
        upload_id = str(data.get("upload_id") or "")
        try:
            meta_path, part_path = self._chunk_paths(upload_id)
        except ValueError as exc:
            return self._error(str(exc), status=400, code="bad_request")
        if not meta_path.is_file() or not part_path.is_file():
            return self._error("上传会话不存在或已过期", status=404, code="not_found")
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            return self._error("上传会话元数据损坏", status=500, code="server_error")
        received = part_path.stat().st_size
        if received != int(meta.get("size") or 0):
            return self._error("上传尚未完成", status=409, code="incomplete")
        raw = part_path.read_bytes()
        info = attachments.save_bytes(str(meta.get("name") or "attachment"), raw)
        try:
            part_path.unlink()
            meta_path.unlink()
        except Exception:
            pass
        public = dict(info)
        public.pop("text", None)
        public.pop("images", None)
        public.pop("path", None)
        return self._json(public)

    # -- library paths ----------------------------------------------------
    def _library_sources_payload(self) -> Dict[str, Any]:
        cfg = config.load_config()
        sources = config.resolve_library_sources(cfg)
        return {
            "ok": True,
            "install_dir": str(config.INSTALL_DIR),
            "data_dir": str(config.PROJECT_ROOT),
            "data_root_file": str(config.DATA_ROOT_FILE),
            "sources": sources,
            "current": next((item["path"] for item in sources
                             if item["enabled"] and item["exists"]), ""),
            "status": library.status(),
        }

    def _library_sources_save(self) -> None:
        data = self._body()
        sources = data.get("sources")
        if not isinstance(sources, list):
            return self._error("sources 必须是数组", status=400, code="bad_request")
        for item in sources:
            if not isinstance(item, dict):
                return self._error("路径条目格式错误", status=400, code="bad_request")
            if str(item.get("kind") or "") == "custom":
                path = Path(str(item.get("path") or ""))
                if not path.is_dir():
                    return self._error(f"目录不存在：{path}",
                                       "请选择本机已存在的文件夹。", 400, "invalid_path")
        config.save_library_sources(sources)
        if data.get("reindex", True):
            library.start_index(force=False)
        return self._json(self._library_sources_payload())

    # -- updates ----------------------------------------------------------
    def _update_check(self) -> None:
        data = self._body()
        result = update_check.check(
            force=bool(data.get("force", False)),
            use_model=(None if data.get("use_model") is None
                       else bool(data.get("use_model"))),
        )
        return self._json(result)

    def _update_download(self) -> None:
        data = self._body()
        try:
            progress = update_check.start_download(str(data.get("url") or ""))
        except ValueError as exc:
            return self._error(str(exc), status=400, code="bad_url")
        return self._json({"ok": True, **progress})

    def _update_install(self) -> None:
        try:
            result = update_check.install_downloaded()
        except ValueError as exc:
            return self._error(str(exc), status=400, code="not_ready")
        return self._json(result)

    def _update_skip(self) -> None:
        data = self._body()
        update_check.skip_version(str(data.get("version") or ""))
        return self._json({"ok": True})

    def _report(self) -> None:
        data = self._body()
        try:
            design = engine.design_network(
                data.get("topology", "auto"), float(data["frequency_mhz"]),
                float(data["load_r"]), float(data.get("load_x", 0.0)),
                float(data.get("z0", 50.0)),
                L_uh=None if data.get("L_uh") in (None, "", 0) else float(data["L_uh"]),
                c3_pf=None if data.get("c3_pf") in (None, "", 0) else float(data["c3_pf"]),
                power_w=float(data.get("power_w", 1.0)),
            )
        except engine.DesignError as exc:
            return self._json({"ok": False, "error_code": exc.code,
                               "message": exc.message, "hint": exc.hint}, 200)
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
            verification = engine.analyze_network(design["topology"], fm, zl, comps, z0)
            design["components"] = comps
            design["verification"] = verification
            design["input_impedance"] = verification["input_impedance"]
            design["input_impedance_display"] = engine.fmt_complex(
                complex(verification["input_impedance"]["re"],
                        verification["input_impedance"]["im"]))
            design["vswr"] = verification["vswr"]
            design["s11_db"] = verification["s11_db"]
            design["return_loss_db"] = verification["return_loss_db"]
            design["steps"] = engine.build_steps(design["topology"], fm, zl, comps, z0)
            design["bandwidth"] = engine.bandwidth(design["topology"], fm, zl, comps, z0)
            design["sensitivity"] = engine.sensitivity(design["topology"], fm, zl, comps, z0)
        fmt = str(data.get("format", "html")).lower()
        if fmt not in ("html", "md", "markdown"):
            return self._error("报告格式只支持 html 或 md", status=400, code="bad_request")
        path = reports.generate(design, fmt=fmt, note=str(data.get("note", "")))
        return self._json({"ok": True, "path": str(path),
                           "url": f"/api/report/{path.name}",
                           "format": fmt,
                           "summary": f"报告已生成：{path.name}"})

    # -- docs / library ---------------------------------------------------
    def _docs_ai_search(self) -> None:
        data = self._body()
        cfg = config.load_config()
        result = docs_hub.ai_search_docs(
            str(data.get("query") or ""), cfg,
            category=data.get("category") or None,
            lang=str(data.get("lang", "zh")),
            limit=int(data.get("limit", 60)))
        return self._json(result)

    def _library_index(self) -> None:
        data = self._body()
        return self._json(library.start_index(force=bool(data.get("force")),
                                              ocr_first_pages=int(
                                                  data.get("ocr_first_pages", 2))))

    def _library_ocr(self) -> None:
        data = self._body()
        return self._json(library.ocr_page(int(data["doc_id"]), int(data["page"]),
                                           force=bool(data.get("force"))))

    def _library_ocr_book(self) -> None:
        data = self._body()
        return self._json(library.ocr_document(
            int(data["doc_id"]), int(data.get("start", 1)),
            int(data["end"]) if data.get("end") else None,
            int(data.get("max_pages", 40))))

    def _library_translate(self) -> None:
        data = self._body()
        try:
            result = library.translate_page(
                int(data["doc_id"]), int(data["page"]), config.load_config(),
                target_lang=data.get("target_lang") or None)
            return self._json(result)
        except llm.LLMError as exc:
            return self._error(exc.message, exc.hint, 400, "llm_error")

    def _library_upload(self) -> None:
        data = self._body()
        result = library.add_book(str(data.get("name") or "book.pdf"),
                                  data.get("content_base64") or "")
        return self._json(result)

    def _library_ai_search(self) -> None:
        data = self._body()
        cfg = config.load_config()
        result = library.ai_search(
            str(data.get("query") or ""), cfg,
            doc_id=int(data["doc_id"]) if data.get("doc_id") else None,
            lang=str(data.get("lang", "zh")),
            limit=int(data.get("limit", 24)))
        return self._json(result)

    # -- providers / usage ------------------------------------------------
    def _providers_update(self) -> None:
        data = self._body()
        mode = str(data.get("mode") or "models_dev")
        cfg = config.load_config()
        if mode == "models_dev":
            return self._json(providers.update_from_models_dev())
        if mode == "provider_api":
            return self._json(providers.update_from_provider_api(cfg))
        if mode == "announcements":
            pid = str(data.get("provider_id") or
                      (cfg.get("llm") or {}).get("provider") or "")
            return self._json(providers.fetch_announcements(pid))
        if mode == "ai":
            ids = data.get("provider_ids") or None
            return self._json(providers.ai_update(cfg, ids))
        return self._error("未知更新模式", status=400, code="bad_request")

    def _providers_rollback(self) -> None:
        return self._json(providers.rollback())

    def _providers_reset(self) -> None:
        return self._json(providers.reset_override())

    def _usage_clear(self) -> None:
        return self._json(usage.clear())

    # -- chat SSE ---------------------------------------------------------
    def _chat(self) -> None:
        data = self._body()
        messages = data.get("messages") or []
        attach = data.get("attachments") or []
        context = data.get("context") if isinstance(data.get("context"), dict) else None
        cfg = config.load_config()
        connection_id = str(data.get("connection_id") or "").strip()
        if connection_id:
            try:
                cfg = config.cfg_for_connection(cfg, connection_id,
                                                str(data.get("model") or ""))
            except ValueError as exc:
                return self._error(str(exc), status=400, code="unknown_connection")
        model = str(data.get("model") or "").strip()
        if model and len(model) <= 120:
            cfg["llm"]["model"] = model
        protocol = str(data.get("protocol") or "").strip()
        if protocol in ("openai", "anthropic", "custom", "as_is"):
            cfg["llm"]["protocol"] = protocol
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
            agent.run_chat(cfg, messages, attach, emit, context=context)
        except llm.LLMError as exc:
            emit("error", {"message": exc.message, "hint": exc.hint,
                           "status": exc.status})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
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

    parser = argparse.ArgumentParser(description="Impedance Matching AI desktop shell")
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
    print(f"\n  {config.APP_NAME} · {config.APP_NAME_ZH} v{config.VERSION}")
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
