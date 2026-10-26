"""Web help regression: HTTP headers must stay latin-1 while names stay CJK."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from impedance_mcp import web_server  # noqa: E402


class HelpHeaderTests(unittest.TestCase):
    def test_disposition_is_ascii_and_keeps_utf8_name(self):
        value = web_server._inline_disposition("用户手册.html")
        value.encode("latin-1")  # Header values are sent as latin-1 by http.server.
        self.assertIn("filename*=UTF-8''", value)
        self.assertIn("%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C.html", value)
        self.assertTrue(value.startswith('inline; filename="document.html"'))

    def test_installation_guide_is_served(self):
        self.assertIn("安装与杀毒软件说明.html", web_server.HELP_FILES)
        self.assertIn("安装与杀毒软件说明.pdf", web_server.HELP_FILES)


if __name__ == "__main__":
    unittest.main()
