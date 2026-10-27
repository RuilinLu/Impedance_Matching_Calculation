"""Regression tests for v4.4 features: paths, scan, stress, uploads, updates."""

from __future__ import annotations

import copy
import http.client
import json
import sys
import threading
import unittest
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from impedance_mcp import config, engine, update_check, web_server  # noqa: E402


class ConfigAndPathTests(unittest.TestCase):
    def test_defaults_are_private_by_default(self):
        cfg = config.default_config()
        self.assertFalse(cfg["ui"]["show_thinking"])
        self.assertFalse(cfg["ui"]["show_citations"])
        self.assertTrue(cfg["update"]["auto_check"])
        self.assertEqual(cfg["settings_version"], config.SETTINGS_VERSION)

    def test_legacy_config_is_not_destructive(self):
        base = config.default_config()
        stored = {
            "ui": {"lang": "en", "library_zoom": 1.75},
            "library": {"source_dirs": ["D:/LegacyBooks"]},
            "llm": {"provider": "deepseek", "model": "deepseek-flash"},
        }
        merged = config.deep_merge(base, stored)
        migrated = config._migrate_config(merged, stored)
        self.assertEqual(migrated["ui"]["lang"], "en")
        self.assertEqual(migrated["ui"]["library_zoom"], 1.75)
        self.assertEqual(migrated["llm"]["provider"], "deepseek")
        self.assertEqual(migrated["settings_version"], config.SETTINGS_VERSION)
        custom = [item for item in migrated["library"]["search_dirs"]
                  if item.get("kind") == "custom"]
        self.assertTrue(any(item.get("path") == "D:/LegacyBooks" for item in custom))

    def test_search_dirs_are_ordered_and_deduplicated(self):
        cfg = config.default_config()
        cfg["library"]["search_dirs"] = [
            {"kind": "custom", "path": "D:/One", "enabled": True},
            {"kind": "custom", "path": "D:/One", "enabled": False},
            {"kind": "install_textbook", "enabled": True},
            {"kind": "library_books", "enabled": True},
        ]
        sources = config.resolve_library_sources(cfg)
        custom = [item for item in sources if item["kind"] == "custom"]
        self.assertEqual(len(custom), 1)
        self.assertTrue(custom[0]["path"].replace("\\", "/").lower().endswith("d:/one"))
        install = next(item for item in sources if item["kind"] == "install_textbook")
        self.assertTrue(install["path"].startswith(str(config.INSTALL_DIR)))


class ScanTests(unittest.TestCase):
    def test_coverage_is_monotonic_when_range_grows(self):
        design = engine.design_network("l_right", 2400, 20, 5)
        comps = design["components"]
        coverages = []
        for upper in (10, 30, 100, 1000):
            result = engine.scan_matchable_range(
                "l_right", 2400, 50, comps["L_uH"],
                (0.5, 10), (0.5, upper), points_budget=10000)
            self.assertTrue(result["ok"])
            self.assertEqual(result["evaluated_count"], result["points_count"])
            coverages.append(result["coverage_fraction"])
        for previous, current in zip(coverages, coverages[1:]):
            self.assertGreaterEqual(current + 0.005, previous,
                                    f"coverage shrank: {coverages}")

    def test_scan_contains_design_load_and_legacy_api(self):
        design = engine.design_network("l_left", 915, 80, 20)
        comps = design["components"]
        result = engine.scan_matchable_range(
            "l_left", 915, 50, comps["L_uH"],
            (comps["C1_pF"] * 0.5, comps["C1_pF"] * 2),
            (comps["C2_pF"] * 0.5, comps["C2_pF"] * 2),
            steps=30, max_points=3000)
        self.assertTrue(result["ok"])
        self.assertIn("coverage", result)
        self.assertIn("grid_size", result)
        self.assertLessEqual(len(result["points"]), 3000)
        self.assertLessEqual(result["r_min"], 80)
        self.assertGreaterEqual(result["r_max"], 80)

    def test_three_element_scan(self):
        for topology in ("t", "pi1", "pi2"):
            result = engine.scan_matchable_range(
                topology, 2400, 50, 0.003,
                (0.5, 10), (0.5, 10), (0.2, 10), points_budget=4096)
            self.assertTrue(result["ok"], topology)
            self.assertGreater(result["coverage_fraction"], 0.01, topology)


class StressTests(unittest.TestCase):
    def test_sweep_reports_real_solves_and_worst_case(self):
        design = engine.design_network("l_right", 2400, 20, 5)
        comps = design["components"]
        result = engine.voltage_stress(
            "l_right", 2400, 20, 5, comps["L_uH"],
            comps["C1_pF"], comps["C2_pF"], 0.0, 10.0,
            sweep=True, sweep_points=11, frequency_span=0.2)
        self.assertGreaterEqual(result["solves"], 121)
        self.assertGreaterEqual(result["elapsed_ms"], 0)
        self.assertEqual(result["sweep"]["points_count"], 121)
        worst = result["sweep"]["worst"]
        self.assertGreater(worst["voltage_peak"], 0)
        for element in result["elements"]:
            self.assertGreaterEqual(element["voltage_peak_worst"],
                                    element["voltage_peak"])

    def test_single_point_is_one_solve(self):
        design = engine.design_network("l_right", 2400, 20, 5)
        comps = design["components"]
        result = engine.voltage_stress(
            "l_right", 2400, 20, 5, comps["L_uH"],
            comps["C1_pF"], comps["C2_pF"], 0.0, 10.0, sweep=False)
        self.assertEqual(result["solves"], 1)
        self.assertEqual(result["sweep"]["points_count"], 0)


class UpdateVersionTests(unittest.TestCase):
    def test_semver(self):
        self.assertEqual(update_check.version_tuple("v4.4.0"), (4, 4, 0, 0))
        self.assertTrue(update_check.is_newer("4.4.0", "4.3.0"))
        self.assertFalse(update_check.is_newer("4.3.9", "4.4.0"))
        self.assertTrue(update_check.is_newer("4.10.0", "4.9.9"))

    def test_unsafe_download_urls_are_rejected(self):
        for value in ("http://api.github.com/x", "https://example.com/x",
                      "https://127.0.0.1/x", "file:///C:/x"):
            with self.assertRaises(ValueError):
                update_check._validate_target(value)


class WebUploadTests(unittest.TestCase):
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

    def _json(self, method, path, payload=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=60)
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"} if body else {}
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        conn.close()
        return response.status, data

    def test_chunked_upload(self):
        raw = ("chunked upload test \u4e2d\u6587\n" * 20).encode("utf-8")
        status, init = self._json("POST", "/api/upload/init",
                                  {"name": "chunk.txt", "size": len(raw)})
        self.assertEqual(status, 200)
        upload_id = init["upload_id"]
        half = len(raw) // 2
        for chunk in (raw[:half], raw[half:]):
            conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=60)
            conn.request("POST", f"/api/upload/chunk?upload_id={upload_id}",
                         body=chunk, headers={"Content-Type": "application/octet-stream"})
            response = conn.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
            conn.close()
            self.assertEqual(response.status, 200)
            self.assertTrue(payload["ok"])
        status, info = self._json("POST", "/api/upload/complete",
                                  {"upload_id": upload_id})
        self.assertEqual(status, 200)
        self.assertTrue(info["ok"])
        self.assertEqual(info["size"], len(raw))
        self.assertEqual(info["kind"], "text")

    def test_library_sources_endpoint(self):
        status, payload = self._json("GET", "/api/library/sources")
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        self.assertIn("install_dir", payload)
        self.assertIn("data_dir", payload)
        self.assertIsInstance(payload["sources"], list)

    def test_scan_stream_emits_meta_points_done(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=60)
        body = json.dumps({
            "topology": "l_right", "frequency_mhz": 2400, "z0": 50,
            "L_uh": 0.001939, "points_budget": 900,
            "c1_range_pf": [0.5, 10], "c2_range_pf": [0.5, 10],
        }).encode("utf-8")
        conn.request("POST", "/api/scan/stream", body=body,
                     headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        text = response.read().decode("utf-8")
        conn.close()
        self.assertEqual(response.status, 200)
        self.assertIn("event: meta", text)
        self.assertIn("event: points", text)
        self.assertIn("event: done", text)
        done = text.split("event: done")[-1].split("data:", 1)[1].strip()
        payload = json.loads(done)
        self.assertEqual(payload["evaluated_count"], 900)
        self.assertIn("coverage", payload)


if __name__ == "__main__":
    unittest.main(verbosity=2)
