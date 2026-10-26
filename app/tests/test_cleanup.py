"""Deep-uninstall cleanup tests (no real user data is touched)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from impedance_mcp import cleanup  # noqa: E402


class CleanupTests(unittest.TestCase):
    def test_is_ours(self):
        self.assertTrue(cleanup._is_ours(
            {"command": r"C:\Apps\ImpedanceMCP\ImpedanceMCP_MCP.exe", "args": ["--mcp"]},
            None,
        ))
        self.assertFalse(cleanup._is_ours({"command": "other-server.exe"}, None))

    def test_remove_json_entry_preserves_other_servers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps({
                "mcp": {"servers": {
                    "impedance-matching": {"command": r"C:\Apps\ImpedanceMCP_MCP.exe"},
                    "other": {"command": "other-server.exe"},
                }},
            }), encoding="utf-8")
            removed = cleanup._remove_json_entry(
                path, ["mcp", "servers"], None, dry_run=False)
            assert removed is True
            data = json.loads(path.read_text(encoding="utf-8"))
            assert "impedance-matching" not in data["mcp"]["servers"]
            assert "other" in data["mcp"]["servers"]

    def test_remove_toml_section_preserves_other_servers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            path.write_text(
                "[mcp_servers.impedance-matching]\n"
                'command = "C:\\\\Apps\\\\ImpedanceMCP_MCP.exe"\n'
                'args = ["--mcp"]\n\n'
                "[mcp_servers.other]\n"
                'command = "other-server.exe"\n',
                encoding="utf-8",
            )
            removed = cleanup._remove_toml_section(
                path, "mcp_servers.impedance-matching", None, dry_run=False)
            assert removed is True
            text = path.read_text(encoding="utf-8")
            assert "impedance-matching" not in text
            assert "[mcp_servers.other]" in text


if __name__ == "__main__":
    unittest.main()
