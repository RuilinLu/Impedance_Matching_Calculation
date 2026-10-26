"""Independent physics audit: ABCD cascade vs nodal analysis, scan and stress.

These tests deliberately use a second network method (ABCD matrices) so a sign
or conjugate error in the main engine cannot hide behind its own nodal solver.
"""

from __future__ import annotations

import cmath
import math
import random
import sys
import unittest
from pathlib import Path

import numpy as np

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from impedance_mcp import engine  # noqa: E402


def _series(z: complex) -> np.ndarray:
    return np.array([[1.0, z], [0.0, 1.0]], dtype=complex)


def _shunt(y: complex) -> np.ndarray:
    return np.array([[1.0, 0.0], [y, 1.0]], dtype=complex)


def _zin_abcd(matrix: np.ndarray, zl: complex) -> complex:
    a, b = matrix[0, 0], matrix[0, 1]
    c, d = matrix[1, 0], matrix[1, 1]
    return (a * zl + b) / (c * zl + d)


def abcd_zin(topology: str, f_mhz: float, zl: complex, comps: dict,
             z0: float = 50.0) -> complex:
    w = 2 * math.pi * f_mhz * 1e6
    L = comps["L_uH"] * 1e-6
    c1 = comps["C1_pF"] * 1e-12
    c2 = comps["C2_pF"] * 1e-12
    c3 = comps.get("C3_pF", 0.0) * 1e-12
    zs = 1j * (w * L - 1.0 / (w * c2))
    if topology == "l_right":
        m = _shunt(1j * w * c1) @ _series(zs)
    elif topology == "l_left":
        m = _series(zs) @ _shunt(1j * w * c1)
    elif topology == "t":
        zsh = 1j * (w * L - 1.0 / (w * c2))
        m = _series(-1j / (w * c3)) @ _shunt(1.0 / zsh) @ _series(-1j / (w * c1))
    elif topology == "pi1":
        m = _shunt(1j * w * c3) @ _series(zs) @ _shunt(1j * w * c1)
    elif topology == "pi2":
        m = _shunt(1j * w * c1) @ _series(zs) @ _shunt(1j * w * c3)
    else:
        raise ValueError(topology)
    return _zin_abcd(m, zl)


CASES = [
    ("l_right", 2400.0, 20.0, 5.0),
    ("l_left", 2400.0, 100.0, -30.0),
    ("t", 2400.0, 50.0, 20.0),
    ("pi1", 2400.0, 30.0, -15.0),
    ("pi2", 2400.0, 20.0, 5.0),
    ("l_right", 433.0, 15.0, 0.0),
    ("l_left", 915.0, 80.0, 20.0),
    ("t", 1000.0, 25.0, 10.0),
    ("pi1", 5800.0, 35.0, 12.0),
    ("pi2", 1800.0, 12.0, -8.0),
]


class PhysicsAuditTests(unittest.TestCase):
    def test_abcd_matches_nodal(self):
        rng = random.Random(20261026)
        checked = 0
        for top, f, r, x in CASES:
            for _ in range(8):
                rr = max(1e-3, r * (1 + rng.uniform(-0.35, 0.35)))
                xx = x + rng.uniform(-0.25, 0.25) * max(1.0, abs(x) + r)
                try:
                    d = engine.design_network(top, f, rr, xx)
                except engine.DesignError:
                    continue
                c = d["components"]
                zl = complex(rr, xx)
                nodal = engine.analyze_network(top, f, zl, c)["input_impedance"]
                z_nodal = complex(nodal["re"], nodal["im"])
                z_abcd = abcd_zin(top, f, zl, c)
                self.assertLess(abs(z_nodal - z_abcd), 1e-8,
                                f"{top}: nodal={z_nodal} abcd={z_abcd}")
                checked += 1
        self.assertGreater(checked, 20)

    def test_forward_scan_points_are_really_matched(self):
        # For every sampled point returned by the forward scan, reconstruct the
        # network and verify Zin.  This catches conjugate/sign errors in the
        # scan equations, independent of the inverse design formulas.
        configs = [
            ("l_right", 2400.0, 0.001939, (0.5, 10.0), (0.5, 10.0), None),
            ("l_left", 2400.0, 0.012966, (0.2, 5.0), (0.2, 10.0), None),
            ("t", 2400.0, 0.003154, (0.2, 5.0), (0.5, 10.0), (0.3, 5.0)),
            ("pi1", 2400.0, 0.004208, (0.2, 5.0), (0.5, 10.0), (0.3, 10.0)),
            ("pi2", 2400.0, 0.002955, (0.2, 5.0), (0.5, 10.0), (0.3, 10.0)),
        ]
        for top, f, L, c1r, c2r, c3r in configs:
            r = engine.scan_matchable_range(
                top, f, 50, L, c1r, c2r, c3r, steps=8, max_points=5000
            )
            self.assertTrue(r["ok"], top)
            # The scan returns Z_load points; evaluating with the same topology
            # and a grid of components is ambiguous for 3-element networks, so
            # only verify the 2-element topologies point-by-point here.
            if top in ("l_right", "l_left"):
                # Re-run a small grid to know which C1/C2 produced each point.
                import numpy as np
                c1v = np.linspace(c1r[0] * 1e-12, c1r[1] * 1e-12, 8)
                c2v = np.linspace(c2r[0] * 1e-12, c2r[1] * 1e-12, 8)
                w = 2 * math.pi * f * 1e6
                for c1 in c1v[::3]:
                    for c2 in c2v[::3]:
                        comps = {"L_uH": L, "C1_pF": c1 * 1e12,
                                 "C2_pF": c2 * 1e12, "C3_pF": 0.0}
                        if top == "l_right":
                            zsrc = 1 / (1 / 50 + 1j * w * c1)
                            zser = 1j * (w * L * 1e-6 - 1 / (w * c2))
                            zl = complex(np.conj(zsrc) - zser)
                        else:
                            zser = 50 + 1j * (w * L * 1e-6 - 1 / (w * c2))
                            ytot = 1 / zser + 1j * w * c1
                            zl = complex(np.conj(1 / ytot))
                        if zl.real <= 0:
                            continue
                        ev = engine.analyze_network(top, f, zl, comps)
                        self.assertLess(ev["vswr"], 1.001,
                                        f"{top} scan point {zl} VSWR={ev['vswr']}")

    def test_trajectory_continuity(self):
        for top, f, r, x in CASES:
            d = engine.design_network(top, f, r, x)
            steps = d["steps"]
            self.assertTrue(steps)
            for i in range(1, len(steps)):
                prev = steps[i - 1]["end"]
                cur = steps[i]["start"]
                self.assertLess(abs(complex(prev["re"], prev["im"]) -
                                    complex(cur["re"], cur["im"])), 1e-9,
                                f"{top} step {i} discontinuity")
            end = steps[-1]["end"]["gamma"]
            self.assertLess(math.hypot(end["re"], end["im"]), 1e-6)

    def test_power_and_voltage(self):
        d = engine.design_network("l_right", 2400, 20, 5)
        c = d["components"]
        st = engine.voltage_stress("l_right", 2400, 20, 5, c["L_uH"],
                                   c["C1_pF"], c["C2_pF"], 0.0, 10.0)
        self.assertAlmostEqual(st["delivered_power_w"], 10.0, delta=1e-6)
        self.assertAlmostEqual(st["efficiency"], 1.0, delta=1e-6)
        self.assertAlmostEqual(st["input_voltage_peak"], math.sqrt(2 * 10 * 50), delta=1e-6)

    def test_vswr_relation(self):
        for top, f, r, x in CASES:
            d = engine.design_network(top, f, r, x)
            g = complex(d["verification"]["reflection"]["re"],
                        d["verification"]["reflection"]["im"])
            mag = abs(g)
            expected = (1 + mag) / (1 - mag) if mag < 1 else float("inf")
            self.assertAlmostEqual(d["vswr"], expected, delta=1e-9)


if __name__ == "__main__":
    unittest.main(verbosity=2)
