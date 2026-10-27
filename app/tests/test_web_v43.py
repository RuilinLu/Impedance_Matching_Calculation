"""HTTP API regression tests for the v4.3 application shell."""

from __future__ import annotations

import http.client
import json
import sys
import threading
import unittest
from pathlib import Path
from urllib.parse import quote

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from impedance_mcp import attachments, web_server  # noqa: E402


class WebApiTests(unittest.TestCase):
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
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=60)
        body = None
        headers = {}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        raw = response.read()
        conn.close()
        return response.status, raw

    def get_json(self, path):
        status, raw = self.request("GET", path)
        self.assertEqual(status, 200)
        return json.loads(raw.decode("utf-8"))

    def post_json(self, path, payload):
        status, raw = self.request("POST", path, payload)
        self.assertEqual(status, 200)
        return json.loads(raw.decode("utf-8"))

    def test_health_and_static(self):
        self.assertTrue(self.get_json("/api/health")["ok"])
        status, raw = self.request("GET", "/")
        self.assertEqual(status, 200)
        html = raw.decode("utf-8")
        self.assertIn("Impedance Matching AI", html)
        self.assertIn("教材库", html)
        self.assertIn("文档中心", html)
        self.assertNotIn("MATLAB 检测", html)

    def test_status_and_catalog(self):
        status = self.get_json("/api/status")
        self.assertEqual(status["version"], "4.4.1")
        self.assertIn("llm", status)
        self.assertNotIn("matlab", status)
        providers = self.get_json("/api/providers")
        self.assertEqual(len(providers["providers"]), 20)
        summary = self.get_json("/api/providers/summary")
        self.assertGreaterEqual(summary["models"], 60)

    def test_docs_api(self):
        listing = self.get_json("/api/docs/list?lang=zh")
        ids = {item["id"] for item in listing["categories"]}
        self.assertEqual(ids, {"features", "code", "ai", "mcp"})
        code = self.get_json("/api/docs/get?category=code&lang=zh")
        self.assertIn("engine.design_network", code["markdown"])
        search = self.get_json("/api/docs/search?q=DeepSeek&lang=zh")
        self.assertGreater(search["count"], 0)
        mcp = self.get_json("/api/docs/get?category=mcp&lang=zh")
        self.assertIn("search_textbooks", mcp["markdown"])

    def test_library_search(self):
        search = self.get_json("/api/library/search?q=Smith%20chart&limit=3")
        self.assertTrue(search["ok"])
        self.assertGreaterEqual(search["count"], 0)

    def test_design_and_scan(self):
        design = self.post_json("/api/design", {
            "topology": "auto", "frequency_mhz": 2400,
            "load_r": 20, "load_x": 5,
        })
        self.assertTrue(design["ok"])
        self.assertLess(design["vswr"], 1.001)
        scan = self.post_json("/api/scan", {
            "topology": "l_right", "frequency_mhz": 2400,
            "L_uh": 0.001939, "steps": 12,
        })
        self.assertTrue(scan["ok"])
        self.assertGreater(scan["points_count"], 0)

    def test_upload_text(self):
        info = self.post_json("/api/upload-text", {
            "text": "% Smith chart demo\nz = 20 + 5j;\n",
            "name": "clipboard.m",
        })
        self.assertTrue(info["ok"])
        self.assertEqual(info["kind"], "code")
        self.assertGreater(info["chars"], 0)
        self.assertNotIn("text", info)
        # The wire payload is trimmed, but the follow-up chat lookup must still
        # see the extracted text in the server-side cache.
        cached = attachments.load_attachment(info["id"])
        self.assertIn("Smith chart demo", cached.get("text") or "")

    def test_missing_fields_are_400(self):
        status, raw = self.request("POST", "/api/design", {})
        self.assertEqual(status, 400)
        self.assertEqual(json.loads(raw.decode("utf-8"))["error_code"], "bad_request")

    def test_invalid_engineering_inputs(self):
        design = self.post_json("/api/design", {
            "topology": "auto", "frequency_mhz": 0, "load_r": 20,
        })
        self.assertFalse(design["ok"])
        self.assertEqual(design["error_code"], "invalid_frequency")
        design = self.post_json("/api/design", {
            "topology": "auto", "frequency_mhz": 2450, "load_r": 20, "load_x": "nan",
        })
        self.assertFalse(design["ok"])
        self.assertEqual(design["error_code"], "invalid_input")
        scan = self.post_json("/api/scan", {
            "topology": "l_right", "frequency_mhz": 2450, "L_uh": 0, "steps": 10,
        })
        self.assertFalse(scan["ok"])
        self.assertEqual(scan["error_code"], "invalid_L")
        status, _ = self.request("POST", "/api/convert", {"mode": "bad", "real": 50})
        self.assertEqual(status, 400)

    def test_post_body_does_not_poison_keepalive(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        # /api/providers/reset ignores its body; the server must still drain it.
        conn.request("POST", "/api/providers/reset", body=b"{}",
                     headers={"Content-Type": "application/json"})
        first = conn.getresponse()
        first.read()
        self.assertEqual(first.status, 200)
        conn.request("GET", "/api/health")
        second = conn.getresponse()
        payload = json.loads(second.read().decode("utf-8"))
        conn.close()
        self.assertEqual(second.status, 200)
        self.assertTrue(payload["ok"])

    def test_long_docs_query_is_capped(self):
        search = self.get_json("/api/docs/search?q=" + quote("a" * 5000) + "&lang=zh")
        self.assertTrue(search["ok"])
        self.assertEqual(search["query"][:1], "a")


if __name__ == "__main__":
    unittest.main(verbosity=2)
