"""Engine regression tests (run with: python -m unittest discover -s app/tests -v)."""

from __future__ import annotations

import math
import random
import sys
import unittest
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from impedance_mcp import engine  # noqa: E402


CASES = [
    ("l_right", 2400.0, 20.0, 5.0, None, None),
    ("l_left", 2400.0, 100.0, -30.0, None, None),
    ("t", 2400.0, 50.0, 20.0, None, None),
    ("pi1", 2400.0, 30.0, -15.0, None, None),
    ("pi2", 2400.0, 20.0, 5.0, None, None),
    ("l_right", 433.0, 15.0, 0.0, None, None),
    ("l_left", 915.0, 80.0, 20.0, None, None),
    ("t", 1000.0, 25.0, 10.0, 10.0, 2.0),
    ("pi1", 5800.0, 35.0, 12.0, None, None),
    ("pi2", 1800.0, 12.0, -8.0, None, None),
]


class EngineTests(unittest.TestCase):
    def test_known_cases(self):
        for top, f, r, x, l, c3 in CASES:
            with self.subTest(top=top, f=f, load=(r, x)):
                d = engine.design_network(top, f, r, x, L_uh=l, c3_pf=c3)
                self.assertLess(d["vswr"], 1.001)
                zin = complex(d["input_impedance"]["re"], d["input_impedance"]["im"])
                self.assertLess(abs(zin - 50.0), 0.01)
                self.assertGreater(d["components"]["C1_pF"], 0)
                self.assertGreater(d["components"]["C2_pF"], 0)

    def test_evaluate_matches_design(self):
        for top, f, r, x, _, _ in CASES:
            d = engine.design_network(top, f, r, x)
            c = d["components"]
            ev = engine.evaluate(top, f, r, x, c["L_uH"], c["C1_pF"], c["C2_pF"], c["C3_pF"])
            self.assertLess(ev["vswr"], 1.001)

    def test_random_feasible_designs(self):
        random.seed(20261026)
        ok = 0
        for _ in range(120):
            top = random.choice(["l_right", "l_left", "t", "pi1", "pi2"])
            f = random.choice([100.0, 433.0, 915.0, 1800.0, 2400.0, 5800.0])
            if top == "l_right":
                r = random.uniform(5, 45)
            elif top == "l_left":
                r = random.uniform(55, 250)
            else:
                r = random.uniform(8, 180)
            x = random.uniform(-40, 40)
            try:
                d = engine.design_network(top, f, r, x)
            except engine.DesignError:
                continue
            self.assertLess(d["vswr"], 1.001)
            self.assertTrue(math.isfinite(d["s11_db"]))
            ok += 1
        self.assertGreaterEqual(ok, 60, "too few feasible random cases")

    def test_topology_constraints(self):
        with self.assertRaises(engine.DesignError):
            engine.design_network("l_right", 1000, 100, 0)
        with self.assertRaises(engine.DesignError):
            engine.design_network("l_left", 1000, 20, 0)
        with self.assertRaises(engine.DesignError):
            engine.design_network("l_right", 0, 20, 0)
        with self.assertRaises(engine.DesignError):
            engine.design_network("l_right", 1000, -5, 0)

    def test_scan_contains_design_load(self):
        d = engine.design_network("l_right", 2400, 20, 5)
        c = d["components"]
        scan = engine.scan_matchable_range(
            "l_right", 2400, 50, c["L_uH"],
            (c["C1_pF"] * 0.3, c["C1_pF"] * 3),
            (c["C2_pF"] * 0.3, c["C2_pF"] * 3),
            steps=45,
        )
        self.assertTrue(scan["ok"])
        self.assertLessEqual(scan["r_min"], 20.0)
        self.assertGreaterEqual(scan["r_max"], 20.0)
        self.assertLessEqual(scan["x_min"], 5.0)
        self.assertGreaterEqual(scan["x_max"], 5.0)

    def test_bandwidth_and_stress(self):
        d = engine.design_network("l_right", 2400, 20, 5)
        c = d["components"]
        bw = d["bandwidth"]
        self.assertLessEqual(bw["low_mhz"], 2400.0)
        self.assertGreaterEqual(bw["high_mhz"], 2400.0)
        st = engine.voltage_stress("l_right", 2400, 20, 5,
                                   c["L_uH"], c["C1_pF"], c["C2_pF"], 0.0, 10.0)
        self.assertAlmostEqual(st["input_voltage_peak"], math.sqrt(2 * 10 * 50), delta=0.1)
        self.assertAlmostEqual(st["efficiency"], 1.0, delta=0.01)
        self.assertGreater(len(st["elements"]), 0)

    def test_convert_roundtrip(self):
        z = complex(20, 5)
        y = engine.z_to_y(z)
        self.assertAlmostEqual(abs(engine.y_to_z(y) - z), 0.0, places=12)

    def test_report(self):
        from impedance_mcp import reports
        d = engine.design_network("auto", 2400, 20, 5)
        p = reports.generate(d, fmt="html", note="unit-test")
        self.assertTrue(p.exists())
        text = p.read_text(encoding="utf-8")
        self.assertIn("微波阻抗匹配设计报告", text)
        self.assertIn("节点法复核", text)
        pm = reports.generate(d, fmt="md", note="unit-test")
        self.assertTrue(pm.exists())
        self.assertIn("# 微波阻抗匹配设计报告", pm.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
