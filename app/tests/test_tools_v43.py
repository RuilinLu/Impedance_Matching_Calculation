"""Citation and pricing-schedule tests."""

from __future__ import annotations

import json
import sys
import unittest
import urllib.parse
from datetime import datetime
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from impedance_mcp import providers, tools, usage  # noqa: E402


class CitationTests(unittest.TestCase):
    def test_citation_has_crop_url(self):
        citation = tools._citation({
            "doc_id": 3, "page": 21, "title": "Microwave Engineering",
            "snippet": "Smith chart", "rects": [[0.1, 0.2, 0.3, 0.25]],
        })
        self.assertEqual(citation["kind"], "textbook")
        self.assertIn("/api/library/crop", citation["crop_url"])
        query = urllib.parse.parse_qs(urllib.parse.urlparse(citation["crop_url"]).query)
        self.assertEqual(json.loads(query["rects"][0]), [[0.1, 0.2, 0.3, 0.25]])

    def test_deepseek_off_peak_window(self):
        profile = providers.model_meta("deepseek", "deepseek-flash")
        schedule = profile.get("pricing_schedule") or {}
        self.assertTrue(usage._in_off_peak(schedule, datetime(2026, 10, 27, 1, 0)))
        self.assertFalse(usage._in_off_peak(schedule, datetime(2026, 10, 27, 12, 0)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
