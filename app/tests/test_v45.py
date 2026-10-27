"""v4.5 regression tests: chat connections, multimodal output, SSE, stress."""

from __future__ import annotations

import concurrent.futures
import http.client
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from impedance_mcp import agent, config, library, llm, media, tools, web_server  # noqa: E402

SECRET_A = "unit-test-key-aaaaaaaaaaaa"
SECRET_B = "unit-test-key-bbbbbbbbbbbb"


class TempDataMixin:
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._saved = {
            name: getattr(config, name) for name in (
                "DATA_DIR", "CONFIG_PATH", "UPLOAD_DIR", "REPORT_DIR", "MEDIA_DIR",
                "LIBRARY_DIR", "CATALOG_DIR", "USAGE_PATH", "UPDATE_CACHE_PATH",
                "UPLOAD_CHUNK_DIR",
            )
        }
        config.DATA_DIR = self.root / "data"
        config.CONFIG_PATH = config.DATA_DIR / "config.json"
        config.UPLOAD_DIR = config.DATA_DIR / "uploads"
        config.REPORT_DIR = config.DATA_DIR / "reports"
        config.MEDIA_DIR = config.DATA_DIR / "media"
        config.LIBRARY_DIR = config.DATA_DIR / "library"
        config.CATALOG_DIR = config.DATA_DIR / "catalog"
        config.USAGE_PATH = config.DATA_DIR / "usage.jsonl"
        config.UPDATE_CACHE_PATH = config.DATA_DIR / "update_cache.json"
        config.UPLOAD_CHUNK_DIR = config.UPLOAD_DIR / "chunks"
        config.ensure_dirs()

    def tearDown(self):
        for name, value in self._saved.items():
            setattr(config, name, value)
        self.tmp.cleanup()


class ConnectionTests(TempDataMixin, unittest.TestCase):
    def _save(self, provider, base, model, key):
        return config.save_config({"llm": {
            "provider": provider, "provider_name": provider.title(),
            "protocol": "openai", "base_url": base, "model": model,
            "api_key": key,
        }})

    def test_legacy_single_model_becomes_connection(self):
        cfg = config.default_config()
        cfg["llm"].update({
            "provider": "deepseek", "provider_name": "DeepSeek",
            "protocol": "openai", "base_url": "https://api.deepseek.com",
            "api_key": SECRET_A, "model": "deepseek-flash",
        })
        migrated = config._migrate_config(cfg, cfg)
        items = migrated["llm"]["connections"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["provider"], "deepseek")
        self.assertTrue(items[0]["api_key"])
        public = config.public_config(migrated)
        blob = json.dumps(public)
        self.assertNotIn(SECRET_A, blob)
        self.assertTrue(public["llm"]["connections"][0]["has_key"])

    def test_multiple_connections_and_activation_keep_keys(self):
        a = self._save("deepseek", "https://api.deepseek.com", "deepseek-flash", SECRET_A)
        self.assertEqual(len(a["llm"]["connections"]), 1)
        b = self._save("zhipu", "https://open.bigmodel.cn/api/paas/v4", "glm-5.3", SECRET_B)
        self.assertEqual(len(b["llm"]["connections"]), 2)
        ids = {item["provider"]: item["id"] for item in b["llm"]["connections"]}
        active = config.activate_connection(b, ids["deepseek"], "deepseek-v4-pro")
        self.assertEqual(active["model"], "deepseek-v4-pro")
        self.assertEqual(b["llm"]["model"], "deepseek-v4-pro")
        # Persist the active vendor first; the next save must still reuse the
        # target connection's own key instead of the active vendor's key.
        config.save_config({"llm": b["llm"]})
        merged = config.save_config({"llm": {
            "provider": "zhipu", "provider_name": "Zhipu",
            "protocol": "openai",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-5.3",
        }})
        zhipu = next(item for item in merged["llm"]["connections"]
                     if item["provider"] == "zhipu")
        deepseek = next(item for item in merged["llm"]["connections"]
                        if item["provider"] == "deepseek")
        self.assertEqual(zhipu["api_key"], SECRET_B)
        self.assertEqual(deepseek["api_key"], SECRET_A)
        self.assertEqual(merged["llm"]["api_key"], SECRET_B)

    def test_cfg_for_connection_and_delete(self):
        cfg = self._save("deepseek", "https://api.deepseek.com", "deepseek-flash", SECRET_A)
        cid = cfg["llm"]["connections"][0]["id"]
        selected = config.cfg_for_connection(cfg, cid, "deepseek-reasoner")
        self.assertEqual(selected["llm"]["model"], "deepseek-reasoner")
        self.assertEqual(selected["llm"]["api_key"], SECRET_A)
        self.assertEqual(cfg["llm"]["model"], "deepseek-flash")
        self.assertTrue(config.delete_connection(cfg, cid))
        self.assertFalse(cfg["llm"]["connections"])
        self.assertEqual(cfg["llm"]["model"], "")

    def test_connection_id_is_stable_and_masked(self):
        first = config.connection_id("deepseek", "https://api.deepseek.com")
        second = config.connection_id("deepseek", "https://api.deepseek.com/")
        self.assertEqual(first, second)
        conn = {"id": first, "provider": "deepseek", "api_key": SECRET_A,
                "base_url": "https://api.deepseek.com"}
        public = config.public_connection(conn)
        self.assertEqual(public["api_key"], "")
        self.assertTrue(public["has_key"])
        self.assertNotIn(SECRET_A, json.dumps(public))


class MediaTests(TempDataMixin, unittest.TestCase):
    def test_media_extraction_from_openai_blocks(self):
        text, items = llm._media_from_blocks([
            {"type": "text", "text": "结果如下"},
            {"type": "image_url", "image_url": {"url": "https://example.com/a.png"}},
            {"type": "image", "source": {"type": "base64",
                                         "media_type": "image/png", "data": "AAAA"}},
            {"type": "audio", "audio_url": {"url": "https://example.com/a.mp3"}},
        ])
        self.assertEqual(text, "结果如下")
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["type"], "image")
        self.assertTrue(items[1]["url"].startswith("data:image/png;base64,"))
        self.assertEqual(items[2]["type"], "audio")

    def test_top_level_media_arrays_and_b64(self):
        items = llm._collect_output_media({
            "images": [{"url": "https://example.com/x.png", "name": "x.png"}],
            "files": [{"url": "/api/media/doc.pdf", "name": "doc.pdf",
                       "mime_type": "application/pdf"}],
            "audio": [{"b64_json": "QUJD", "mime_type": "audio/mpeg"}],
        })
        self.assertEqual(len(items), 3)
        self.assertTrue(any(item["url"].startswith("data:audio/mpeg;base64,")
                            for item in items))
        self.assertTrue(llm._safe_media_url("javascript:alert(1)") == "")
        self.assertTrue(llm._safe_media_url("file:///C:/secret.txt") == "")

    def test_smith_svg_is_generated_and_served_safely(self):
        result = tools.get_smith_trajectory({
            "frequency_mhz": 2400, "load_r": 20, "load_x": 5,
        })
        self.assertTrue(result["ok"])
        self.assertIn("media", result)
        url = result["image_url"]
        self.assertTrue(url.startswith("/api/media/"))
        path = media.resolve(result["image_name"])
        self.assertIsNotNone(path)
        self.assertTrue(path.read_bytes().startswith(b"<svg"))
        self.assertIsNone(media.resolve("../config.json"))
        self.assertIsNone(media.resolve("not-a-media-file.exe"))


class LibraryConcurrencyTests(TempDataMixin, unittest.TestCase):
    def test_searches_do_not_fail_while_indexing(self):
        books = config.LIBRARY_DIR / "books"
        books.mkdir(parents=True, exist_ok=True)
        for index in range(6):
            (books / f"book{index}.txt").write_text(
                ("Smith chart matching network impedance VSWR " * 200)
                + f"\nbook {index}\n", encoding="utf-8")
        library.init_db(force=True)
        errors = []
        stop = threading.Event()

        def index_worker():
            try:
                library.sync_index(force=True, ocr_first_pages=0)
            except Exception as exc:  # noqa: BLE001
                errors.append(("index", repr(exc)))
            finally:
                stop.set()

        def search_worker():
            while not stop.is_set():
                try:
                    result = library.search("Smith", limit=5)
                    if not result.get("ok"):
                        errors.append(("search", result))
                except Exception as exc:  # noqa: BLE001
                    errors.append(("search", repr(exc)))

        index_thread = threading.Thread(target=index_worker, daemon=True)
        index_thread.start()
        threads = [threading.Thread(target=search_worker, daemon=True) for _ in range(8)]
        for thread in threads:
            thread.start()
        index_thread.join(timeout=60)
        stop.set()
        for thread in threads:
            thread.join(timeout=10)
        self.assertFalse(errors, errors[:5])
        self.assertGreaterEqual(library.status().get("docs", 0), 6)


class WebApiTests(TempDataMixin, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = web_server.create_server("127.0.0.1", 0)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def request(self, method, path, payload=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        body = None
        headers = {}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        raw = response.read()
        status = response.status
        ctype = response.getheader("Content-Type")
        conn.close()
        return status, raw, ctype

    def post(self, path, payload):
        status, raw, _ = self.request("POST", path, payload)
        return status, json.loads(raw.decode("utf-8"))

    def test_connections_api_never_returns_keys(self):
        status, saved = self.post("/api/config", {"llm": {
            "provider": "deepseek", "protocol": "openai",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-flash", "api_key": SECRET_A,
        }})
        self.assertEqual(status, 200)
        status, raw, _ = self.request("GET", "/api/config")
        self.assertEqual(status, 200)
        self.assertNotIn(SECRET_A.encode(), raw)
        data = json.loads(raw)
        self.assertEqual(len(data["config"]["llm"]["connections"]), 1)
        cid = data["config"]["llm"]["connections"][0]["id"]
        status, activated = self.post("/api/connections/activate",
                                      {"id": cid, "model": "deepseek-v4-pro"})
        self.assertEqual(status, 200)
        self.assertEqual(activated["llm"]["model"], "deepseek-v4-pro")
        status, deleted = self.post("/api/connections/delete", {"id": cid})
        self.assertEqual(status, 200)
        self.assertFalse(deleted["config"]["llm"]["connections"])

    def test_media_route_and_traversal(self):
        result = tools.get_smith_trajectory({
            "frequency_mhz": 915, "load_r": 80, "load_x": 20,
        })
        status, raw, ctype = self.request("GET", result["image_url"])
        self.assertEqual(status, 200)
        self.assertIn("image/svg+xml", ctype or "")
        self.assertTrue(raw.startswith(b"<svg"))
        status, _, _ = self.request("GET", "/api/media/..%2Fconfig.json")
        self.assertEqual(status, 404)

    def test_chat_uses_selected_connection_and_emits_media(self):
        _, saved = self.post("/api/config", {"llm": {
            "provider": "deepseek", "protocol": "openai",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-flash", "api_key": SECRET_A,
        }})
        cid = saved["config"]["llm"]["connections"][0]["id"]
        seen = {}

        def fake_run(cfg, messages, attach, emit, context=None):
            seen["model"] = cfg["llm"]["model"]
            seen["key"] = cfg["llm"]["api_key"]
            emit("token", {"text": "你好"})
            emit("media", {"type": "image", "url": "/api/media/x.svg", "name": "x"})
            emit("done", {"content": "你好", "media": [
                {"type": "image", "url": "/api/media/x.svg"}]})
            return {"content": "你好", "media": [
                {"type": "image", "url": "/api/media/x.svg"}]}

        with mock.patch.object(agent, "run_chat", side_effect=fake_run):
            status, raw, ctype = self.request("POST", "/api/chat", {
                "messages": [{"role": "user", "content": "hi"}],
                "connection_id": cid, "model": "deepseek-v4-pro",
            })
        self.assertEqual(status, 200)
        self.assertIn("text/event-stream", ctype or "")
        body = raw.decode("utf-8")
        self.assertIn("event: token", body)
        self.assertIn("event: media", body)
        self.assertEqual(seen["model"], "deepseek-v4-pro")
        self.assertEqual(seen["key"], SECRET_A)

    def test_test_connection_uses_target_saved_key(self):
        self.post("/api/config", {"llm": {
            "provider": "deepseek", "protocol": "openai",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-flash", "api_key": SECRET_A,
        }})
        self.post("/api/config", {"llm": {
            "provider": "zhipu", "protocol": "openai",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-5.3", "api_key": SECRET_B,
        }})
        seen = {}

        def fake_test(cfg, timeout=60):
            seen["key"] = cfg["llm"].get("api_key")
            seen["provider"] = cfg["llm"].get("provider")
            seen["model"] = cfg["llm"].get("model")
            return {"ok": True, "model": seen["model"], "latency_s": 0.0,
                    "reply": "ok", "usage": {}, "cost": {}, "summary": "ok"}

        with mock.patch.object(llm, "test_connection", side_effect=fake_test):
            status, payload = self.post("/api/config/test", {"llm": {
                "provider": "deepseek", "protocol": "openai",
                "base_url": "https://api.deepseek.com",
                "model": "deepseek-v4-pro",
            }})
        self.assertEqual(status, 200)
        self.assertEqual(seen["provider"], "deepseek")
        self.assertEqual(seen["model"], "deepseek-v4-pro")
        self.assertEqual(seen["key"], SECRET_A)

    def test_health_under_concurrency(self):
        def hit(_):
            conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
            conn.request("GET", "/api/health")
            response = conn.getresponse()
            payload = response.read()
            conn.close()
            return response.status, payload

        with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
            results = list(pool.map(hit, range(240)))
        self.assertTrue(all(status == 200 for status, _ in results))
        self.assertTrue(all(b'"ok": true' in payload for _, payload in results))


class UiAssetTests(unittest.TestCase):
    def test_chat_controls_and_media_assets_are_wired(self):
        root = APP.parent
        html = (root / "app/impedance_mcp/web/index.html").read_text(encoding="utf-8")
        chat = (root / "app/impedance_mcp/web/chat.js").read_text(encoding="utf-8")
        app = (root / "app/impedance_mcp/web/app.js").read_text(encoding="utf-8")
        styles = (root / "app/impedance_mcp/web/styles.css").read_text(encoding="utf-8")
        for token in ("btnToggleThinking", "btnToggleCitations", "btnToggleTools",
                      "qaModelSelect", "btnNewChat", "qaNewChat", "展示思考链路",
                      "显示引用", "显示工具调用", "chat.js"):
            self.assertIn(token, html)
        for token in ("createSession", "startEdit", "session.controller.abort",
                      "data-media-copy", "data-media-copy-link", "generation",
                      "connectionHasKey", "populateModelSelects", "copyImageFromUrl"):
            self.assertIn(token, chat)
        for token in ("data-latex", "mediaFigureHtml", "safeMediaUrl",
                      "math-inline"):
            self.assertIn(token, app)
        self.assertIn(".qa-messages > *", styles)
        self.assertIn(".hide-tool-cards .tool-card", styles)
        self.assertIn(".math-copy-btn", styles)

    def test_installer_has_reuse_detection_and_uninstall_checkbox(self):
        script = (APP.parent / "installer/ImpedanceMatchingAI.iss").read_text(encoding="utf-8")
        self.assertIn("ExistingUserData", script)
        self.assertIn("继续复用已有数据", script)
        self.assertIn("ShowUninstallOptions", script)
        self.assertIn("TNewCheckBox", script)
        self.assertIn("保留我的个人数据、设置、教材索引与文件库", script)
        self.assertIn("--delete-user-data", script)
        self.assertIn("--keep-user-data", script)


class McpHttpSessionTests(TempDataMixin, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import socket
        import subprocess

        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe.bind(("127.0.0.1", 0))
        cls.port = probe.getsockname()[1]
        probe.close()
        cls.proc = None

    def setUp(self):
        super().setUp()
        import subprocess
        env = {**os.environ, "IMPEDANCE_DATA_ROOT": str(self.root),
               "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
        self.proc = subprocess.Popen(
            [sys.executable, str(APP / "run_mcp.py"), "--http", str(self.port)],
            cwd=str(APP.parent), env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=1)
                conn.request("GET", "/health")
                if conn.getresponse().status == 200:
                    conn.close()
                    return
                conn.close()
            except Exception:
                time.sleep(0.2)
        self.fail("MCP HTTP server did not start")

    def tearDown(self):
        if self.proc is not None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=5)
            except Exception:
                self.proc.kill()
        super().tearDown()

    def rpc(self, method, params, request_id=1, sid=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=20)
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json, text/event-stream"}
        if sid:
            headers["Mcp-Session-Id"] = sid
        body = json.dumps({"jsonrpc": "2.0", "id": request_id,
                           "method": method, "params": params}).encode()
        conn.request("POST", "/mcp", body=body, headers=headers)
        response = conn.getresponse()
        raw = response.read().decode("utf-8", "replace")
        new_sid = response.getheader("Mcp-Session-Id")
        status = response.status
        conn.close()
        return status, raw, new_sid

    def test_unknown_session_is_rejected(self):
        status, raw, sid = self.rpc("initialize", {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "unit", "version": "1"},
        })
        self.assertEqual(status, 200)
        self.assertTrue(sid)
        status, raw, _ = self.rpc("tools/list", {}, request_id=2, sid=sid)
        self.assertEqual(status, 200)
        self.assertIn("design_matching_network", raw)
        status, raw, _ = self.rpc("tools/list", {}, request_id=3, sid="deadbeef")
        self.assertEqual(status, 404)
        self.assertIn("Unknown or expired session", raw)
        status, _, _ = self.rpc("tools/list", {}, request_id=4, sid=sid)
        self.assertEqual(status, 200)


class AgentMediaTests(unittest.TestCase):
    def test_agent_emits_and_returns_media(self):
        cfg = {
            "llm": {
                "provider": "deepseek", "protocol": "openai",
                "base_url": "https://api.deepseek.com",
                "model": "deepseek-flash", "api_key": "x",
                "temperature": 0.2, "max_tokens": 256,
            },
            "usage": {"auto_peak": False},
        }
        with tempfile.TemporaryDirectory() as tmp:
            old_usage = config.USAGE_PATH
            config.USAGE_PATH = Path(tmp) / "usage.jsonl"
            try:
                def fake_chat(cfg, messages, tools=None, timeout=150):
                    return {
                        "content": "图片已生成。",
                        "tool_calls": [],
                        "media": [{"type": "image", "url": "https://example.com/a.png"}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
                        "model": "mock",
                    }

                events = []
                with mock.patch.object(agent.llm, "chat", side_effect=fake_chat):
                    result = agent.run_chat(
                        cfg, [{"role": "user", "content": "画一张图"}], [],
                        lambda name, data: events.append((name, data)))
            finally:
                config.USAGE_PATH = old_usage
        self.assertIn("media", [name for name, _ in events])
        self.assertEqual(len(result["media"]), 1)

    def test_history_is_bounded_for_long_conversations(self):
        messages = []
        for index in range(400):
            messages.append({"role": "user" if index % 2 == 0 else "assistant",
                             "content": f"message {index}"})
        normalized = agent._normalize_history(messages)
        self.assertLessEqual(len(normalized), 18)
        self.assertEqual(normalized[0]["role"], "user")


if __name__ == "__main__":
    unittest.main(verbosity=2)
