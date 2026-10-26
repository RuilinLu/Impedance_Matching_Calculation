"""Provider catalog, model profile and usage/cost tests."""

from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from impedance_mcp import config, providers, usage  # noqa: E402


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_catalog = config.CATALOG_DIR
        self.old_usage = config.USAGE_PATH
        config.CATALOG_DIR = self.root / "catalog"
        config.CATALOG_DIR.mkdir(parents=True, exist_ok=True)
        config.USAGE_PATH = self.root / "usage.jsonl"

    def tearDown(self):
        config.CATALOG_DIR = self.old_catalog
        config.USAGE_PATH = self.old_usage
        self.tmp.cleanup()

    def test_twenty_providers_and_deepseek(self):
        catalog = providers.all()
        self.assertEqual(len(catalog), 20)
        deepseek = providers.find("deepseek")
        self.assertIsNotNone(deepseek)
        ids = {model["id"] for model in deepseek["models"]}
        self.assertIn("deepseek-flash", ids)
        self.assertIn("deepseek-v4-pro", ids)
        profile = providers.model_meta("deepseek", "deepseek-flash")
        self.assertEqual(profile["context"], 1_000_000)
        self.assertEqual(profile["max_output"], 393216)
        self.assertTrue(profile["vision"])
        self.assertEqual(profile["concurrency"], 2500)
        self.assertIn("peak", profile["pricing"])

    def test_cost_peak_and_cache(self):
        profile = providers.model_meta("deepseek", "deepseek-flash")
        stats = usage.compute_cost(profile, {
            "prompt_tokens": 100000,
            "cached_tokens": 60000,
            "completion_tokens": 10000,
        }, when=datetime(2026, 10, 27, 12, 0), auto_peak=True)
        self.assertEqual(stats["price_bucket"], "peak")
        self.assertAlmostEqual(stats["cache_hit_rate"], 0.6, places=4)
        self.assertAlmostEqual(stats["context_pct"], 0.1, places=4)
        self.assertAlmostEqual(stats["total_cost"], 0.1624, places=6)

    def test_override_validation_and_rollback(self):
        first = providers.save_patch([{
            "id": "deepseek",
            "models": [
                {"id": "deepseek-new-model", "name": "New", "context": 128000},
                {"id": "~bad id~", "name": "Bad"},
            ],
        }], source="unit-test")
        self.assertTrue(first["ok"])
        self.assertGreaterEqual(len(first["warnings"]), 1)
        loaded = providers.find("deepseek")
        ids = {model["id"] for model in loaded["models"]}
        self.assertIn("deepseek-new-model", ids)
        second = providers.save_patch([{
            "id": "deepseek",
            "models": [{"id": "deepseek-second-model", "name": "Second"}],
        }], source="unit-test-2")
        self.assertTrue(second["ok"])
        rollback = providers.rollback()
        self.assertTrue(rollback["ok"])
        loaded = providers.find("deepseek")
        ids = {model["id"] for model in loaded["models"]}
        self.assertNotIn("deepseek-second-model", ids)
        self.assertIn("deepseek-new-model", ids)

    def test_usage_record_and_summary(self):
        profile = providers.model_meta("deepseek", "deepseek-flash")
        record = usage.record(profile, {
            "prompt_tokens": 1000, "cached_tokens": 500,
            "completion_tokens": 200,
        }, "deepseek-flash", 1.2, "unit-test")
        self.assertEqual(record["model"], "deepseek-flash")
        summary = usage.summary()
        self.assertEqual(summary["all"]["requests"], 1)
        self.assertGreater(summary["all"]["total_tokens"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
