"""MCP protocol smoke test: initialize, tools, resources, prompts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "app" / "run_mcp.py"


class MCPProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2025-06-18",
                        "capabilities": {},
                        "clientInfo": {"name": "unittest", "version": "1.0"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "design_matching_network",
                        "arguments": {"topology": "auto", "frequency_mhz": 2400,
                                      "load_r": 20, "load_x": 5}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
             "params": {"name": "evaluate_network",
                        "arguments": {"topology": "l_right", "frequency_mhz": 2400,
                                      "load_r": 20, "load_x": 5,
                                      "L_uh": 0.001939, "C1_pF": 1.6244,
                                      "C2_pF": 6.8033}}},
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
             "params": {"name": "scan_matching_range",
                        "arguments": {"topology": "l_right", "frequency_mhz": 2400,
                                      "L_uh": 0.001939, "steps": 20}}},
            {"jsonrpc": "2.0", "id": 6, "method": "tools/call",
             "params": {"name": "compute_voltage_stress",
                        "arguments": {"topology": "l_right", "frequency_mhz": 2400,
                                      "load_r": 20, "load_x": 5,
                                      "L_uh": 0.001939, "C1_pF": 1.6244,
                                      "C2_pF": 6.8033, "power_w": 10}}},
            {"jsonrpc": "2.0", "id": 7, "method": "tools/call",
             "params": {"name": "search_knowledge", "arguments": {"query": "史密斯圆图"}}},
            {"jsonrpc": "2.0", "id": 8, "method": "tools/call",
             "params": {"name": "get_system_status", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 9, "method": "resources/list", "params": {}},
            {"jsonrpc": "2.0", "id": 10, "method": "resources/read",
             "params": {"uri": "impedance://catalog"}},
            {"jsonrpc": "2.0", "id": 11, "method": "prompts/list", "params": {}},
            {"jsonrpc": "2.0", "id": 12, "method": "prompts/get",
             "params": {"name": "design_match",
                        "arguments": {"frequency_mhz": "2400", "load": "20+j5"}}},
            {"jsonrpc": "2.0", "id": 13, "method": "ping", "params": {}},
            {"jsonrpc": "2.0", "id": 14, "method": "tools/call",
             "params": {"name": "does_not_exist", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 15, "method": "tools/call",
             "params": {"name": "design_matching_network",
                        "arguments": {"topology": "l_left", "frequency_mhz": 1000,
                                      "load_r": 20, "load_x": 0}}},
        ]
        payload = "".join(json.dumps(m, ensure_ascii=False) + "\n" for m in cls.messages)
        env = dict(os.environ)
        env.update({"PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"})
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=payload, text=True, capture_output=True, timeout=90,
            cwd=str(ROOT), env=env, encoding="utf-8", errors="replace",
        )
        cls.proc = proc
        cls.responses = {}
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "id" in obj:
                cls.responses[obj["id"]] = obj

    def test_initialize(self):
        r = self.responses[1]
        self.assertEqual(r["result"]["serverInfo"]["name"], "impedance-matching-ai")
        self.assertIn("protocolVersion", r["result"])
        self.assertIn("tools", r["result"]["capabilities"])

    def test_tools_list(self):
        tools = self.responses[2]["result"]["tools"]
        names = {t["name"] for t in tools}
        self.assertEqual(len(tools), 20)
        for expected in ("design_matching_network", "scan_matching_range",
                         "evaluate_network", "compute_voltage_stress",
                         "analyze_bandwidth", "compare_topologies",
                         "validate_design", "export_design_report",
                         "search_textbooks", "read_textbook_page",
                         "translate_textbook_page", "search_docs",
                         "get_code_reference", "get_library_status",
                         "get_system_status"):
            self.assertIn(expected, names)
        for tool in tools:
            self.assertIn("inputSchema", tool)
            self.assertEqual(tool["inputSchema"].get("type"), "object")

    def test_design_tool(self):
        r = self.responses[3]["result"]
        self.assertFalse(r["isError"])
        data = r["structuredContent"]
        self.assertTrue(data["ok"])
        self.assertLess(data["vswr"], 1.001)
        self.assertGreater(data["components"]["C1_pF"], 0)
        self.assertIn("VSWR", r["content"][0]["text"])

    def test_evaluate_tool(self):
        data = self.responses[4]["result"]["structuredContent"]
        self.assertTrue(data["ok"])
        self.assertLess(data["vswr"], 1.001)
        self.assertAlmostEqual(data["input_impedance"]["re"], 50.0, delta=0.05)

    def test_scan_tool(self):
        data = self.responses[5]["result"]["structuredContent"]
        self.assertTrue(data["ok"])
        self.assertLessEqual(data["r_min"], data["r_max"])
        self.assertGreater(data["points_count"], 0)

    def test_stress_tool(self):
        data = self.responses[6]["result"]["structuredContent"]
        self.assertTrue(data["ok"])
        self.assertAlmostEqual(data["input_voltage_peak"], 31.6228, delta=0.2)
        self.assertAlmostEqual(data["efficiency"], 1.0, delta=0.02)

    def test_knowledge_and_status(self):
        k = self.responses[7]["result"]["structuredContent"]
        self.assertTrue(k["results"])
        s = self.responses[8]["result"]["structuredContent"]
        self.assertTrue(s["ok"])
        self.assertIn("version", s)

    def test_resources(self):
        res = self.responses[9]["result"]["resources"]
        uris = {r["uri"] for r in res}
        self.assertIn("impedance://catalog", uris)
        self.assertIn("impedance://knowledge", uris)
        self.assertIn("impedance://library", uris)
        self.assertIn("impedance://docs", uris)
        read = self.responses[10]["result"]["contents"][0]
        self.assertIn("topologies", read["text"])

    def test_prompts(self):
        prompts = self.responses[11]["result"]["prompts"]
        self.assertTrue(any(p["name"] == "design_match" for p in prompts))
        self.assertTrue(any(p["name"] == "find_textbook" for p in prompts))
        msg = self.responses[12]["result"]["messages"][0]
        self.assertEqual(msg["role"], "user")
        self.assertIn("design_matching_network", msg["content"]["text"])

    def test_ping_and_errors(self):
        self.assertEqual(self.responses[13]["result"], {})
        self.assertTrue(self.responses[14]["result"]["isError"])
        failed = self.responses[15]["result"]
        self.assertFalse(failed["isError"])
        self.assertFalse(failed["structuredContent"]["ok"])

    def test_no_stdout_pollution(self):
        # Every stdout line must be valid JSON-RPC; logs belong on stderr.
        for line in self.proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            self.assertEqual(obj.get("jsonrpc"), "2.0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
