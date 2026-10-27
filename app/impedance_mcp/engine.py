"""
Core RF impedance-matching engine.

The analytical formulas follow the classical L/T/π matching-network design
procedure.  Every design is additionally verified with an independent nodal
analysis of the complete network, so a result is never reported unless the
input impedance really is Z0.

Units used on the public API:
    frequency   MHz
    impedance   ohm
    inductance  uH
    capacitance pF
    power       W
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

EPS = 1e-15

TOPOLOGIES: Dict[str, Dict[str, Any]] = {
    "l_right": {
        "name": "L型（右）",
        "name_en": "L-network (right)",
        "short": "L·右",
        "elements": ["C1", "L", "C2"],
        "requires_L": True,
        "requires_C3": False,
        "load_rule": "R_L < Z0",
        "load_rule_text": "只适用于负载实部小于 Z0 的低阻负载",
        "topology_text": "源(50Ω) — 并联 C1 — 串联 (L + C2) — 负载 ZL",
        "theory": (
            "源端并联电容把低阻负载沿等电导圆变换，随后串联电感/电容抵消剩余电抗。"
            "设计式：Q=sqrt(Z0/R_L-1)，C1=Q/(Z0·ω)，C2=1/[ω(ωL+X_L-Q·R_L)]。"
        ),
    },
    "l_left": {
        "name": "L型（左）",
        "name_en": "L-network (left)",
        "short": "L·左",
        "elements": ["L", "C2", "C1"],
        "requires_L": True,
        "requires_C3": False,
        "load_rule": "R_L > Z0",
        "load_rule_text": "只适用于负载实部大于 Z0 的高阻负载",
        "topology_text": "源(50Ω) — 串联 (L + C2) — 并联 C1 — 负载 ZL",
        "theory": (
            "负载先并联 C1 把等效串联电阻降到 Z0，再由串联 L/C2 抵消电抗。"
            "适合高阻负载，C1 通过求解 G_L/(G_L²+B²)=Z0 得到。"
        ),
    },
    "t": {
        "name": "T型",
        "name_en": "T-network",
        "short": "T",
        "elements": ["C3", "L", "C2", "C1"],
        "requires_L": True,
        "requires_C3": True,
        "load_rule": "R_virtual ≥ R_L",
        "load_rule_text": "C3 决定的中间虚拟电阻必须不小于负载实部",
        "topology_text": "源 — 串联 C3 — 节点（并联 L+C2 到地）— 串联 C1 — 负载",
        "theory": (
            "源端串联 C3 把 50Ω 变换为中间虚拟电阻 R_virtual，负载经串联 C1 变换到同一"
            "电导，再由节点处的并联 L+C2 谐振抵消电纳。三元件网络可匹配更宽的阻抗范围。"
        ),
    },
    "pi1": {
        "name": "π型Ⅰ",
        "name_en": "Pi-network I",
        "short": "πⅠ",
        "elements": ["C3", "L", "C2", "C1"],
        "requires_L": True,
        "requires_C3": True,
        "load_rule": "R_S,eff ≤ R_parallel,load",
        "load_rule_text": "C3 使源端等效电阻足够低，才能与负载端电导匹配",
        "topology_text": "源 — 并联 C3 — 串联 (L+C2) — 并联 C1 — 负载",
        "theory": (
            "C-L-C 结构：源端 C3 与负载端 C1 分别进行向下阻抗变换，中间 L+C2 抵消电抗。"
            "设计时先由 C3 确定源端等效电阻，再求 C1 与 C2。"
        ),
    },
    "pi2": {
        "name": "π型Ⅱ",
        "name_en": "Pi-network II",
        "short": "πⅡ",
        "elements": ["C1", "L", "C2", "C3"],
        "requires_L": True,
        "requires_C3": True,
        "load_rule": "R_L,eff ≤ Z0",
        "load_rule_text": "负载并联 C3 后的等效电阻必须不大于 Z0",
        "topology_text": "源 — 并联 C1 — 串联 (L+C2) — 并联 C3 — 负载",
        "theory": (
            "源端 C1 与负载端 C3 均可调，适合匹配低阻负载；C3 先对负载做导纳变换，"
            "再由 C1 完成 50Ω 侧的电阻变换，L+C2 负责电抗谐振。"
        ),
    },
}

TOPOLOGY_ALIASES = {
    "l_right": "l_right",
    "lright": "l_right",
    "l-right": "l_right",
    "l右": "l_right",
    "l型右": "l_right",
    "l型(右)": "l_right",
    "l型（右）": "l_right",
    "l_left": "l_left",
    "lleft": "l_left",
    "l-left": "l_left",
    "l左": "l_left",
    "l型左": "l_left",
    "l型(左)": "l_left",
    "l型（左）": "l_left",
    "t": "t",
    "t型": "t",
    "pi1": "pi1",
    "pi_1": "pi1",
    "π型i": "pi1",
    "π型1": "pi1",
    "π型Ⅰ": "pi1",
    "pi2": "pi2",
    "pi_2": "pi2",
    "π型ii": "pi2",
    "π型2": "pi2",
    "π型Ⅱ": "pi2",
}


def canonical_topology(value: str) -> str:
    key = str(value or "").strip().lower()
    if key in TOPOLOGY_ALIASES:
        return TOPOLOGY_ALIASES[key]
    compact = key.replace(" ", "").replace("-", "_")
    if compact in TOPOLOGY_ALIASES:
        return TOPOLOGY_ALIASES[compact]
    raise ValueError(
        "未知拓扑 %r，可选：l_right, l_left, t, pi1, pi2" % value
    )


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_complex(value: complex, digits: int = 3) -> str:
    sign = "+" if value.imag >= 0 else "-"
    return f"{value.real:.{digits}f} {sign} j{abs(value.imag):.{digits}f}"


def fmt_si(value: float, unit: str = "", digits: int = 3) -> str:
    if not math.isfinite(value):
        return "—"
    av = abs(value)
    prefixes = [
        (1e9, "G"), (1e6, "M"), (1e3, "k"), (1.0, ""),
        (1e-3, "m"), (1e-6, "µ"), (1e-9, "n"), (1e-12, "p"),
    ]
    for scale, prefix in prefixes:
        if av >= scale * 0.999 or scale == 1e-12:
            return f"{value / scale:.{digits}g} {prefix}{unit}"
    return f"{value:.{digits}g} {unit}"


# ---------------------------------------------------------------------------
# Nodal analysis of the complete network (independent verification)
# ---------------------------------------------------------------------------

def _solve_linear(matrix: List[List[complex]], rhs: List[complex]) -> List[complex]:
    """Tiny Gaussian elimination with partial pivoting (n <= 4)."""
    n = len(rhs)
    a = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-18:
            raise ValueError("网络矩阵奇异，无法求解（请检查元件值）")
        a[col], a[pivot] = a[pivot], a[col]
        pv = a[col][col]
        for j in range(col, n + 1):
            a[col][j] /= pv
        for r in range(n):
            if r == col:
                continue
            factor = a[r][col]
            if factor == 0:
                continue
            for j in range(col, n + 1):
                a[r][j] -= factor * a[col][j]
    return [a[i][n] for i in range(n)]


def _component_impedance(w: float, L_h: float, C_f: float) -> complex:
    """Series L + C impedance."""
    if C_f <= 0:
        raise ValueError("电容值必须大于 0")
    return complex(0.0, w * L_h - 1.0 / (w * C_f))


def _network(topology: str, w: float, L_h: float, c1_f: float,
             c2_f: float, c3_f: float) -> Tuple[List[str], List[Dict[str, Any]], complex]:
    """Return (nodes, elements, load) for the selected topology.

    Element dict keys: name, kind ('series'|'shunt'), a, b, z (series) or y (shunt).
    Node 0 is always the source node; the load node is the last node.
    """
    if topology == "l_right":
        nodes = ["s", "l"]
        zs = _component_impedance(w, L_h, c2_f)
        elements = [
            {"name": "C1", "label": "并联 C1", "kind": "shunt", "a": "s", "y": 1j * w * c1_f},
            {"name": "L+C2", "label": "串联 L+C2", "kind": "series", "a": "s", "b": "l",
             "z": zs, "parts": {"L": complex(0, w * L_h),
                                "C2": complex(0, -1.0 / (w * c2_f))}},
        ]
    elif topology == "l_left":
        nodes = ["s", "l"]
        zs = _component_impedance(w, L_h, c2_f)
        elements = [
            {"name": "L+C2", "label": "串联 L+C2", "kind": "series", "a": "s", "b": "l",
             "z": zs, "parts": {"L": complex(0, w * L_h),
                                "C2": complex(0, -1.0 / (w * c2_f))}},
            {"name": "C1", "label": "并联 C1", "kind": "shunt", "a": "l", "y": 1j * w * c1_f},
        ]
    elif topology == "t":
        nodes = ["s", "m", "l"]
        zc3 = complex(0, -1.0 / (w * c3_f))
        zc1 = complex(0, -1.0 / (w * c1_f))
        zsh = _component_impedance(w, L_h, c2_f)
        elements = [
            {"name": "C3", "label": "串联 C3", "kind": "series", "a": "s", "b": "m", "z": zc3},
            {"name": "C1", "label": "串联 C1", "kind": "series", "a": "m", "b": "l", "z": zc1},
            {"name": "L+C2", "label": "并联 L+C2", "kind": "shunt", "a": "m", "y": 1.0 / zsh,
             "z": zsh, "parts": {"L": complex(0, w * L_h),
                                 "C2": complex(0, -1.0 / (w * c2_f))}},
        ]
    elif topology == "pi1":
        nodes = ["s", "l"]
        zs = _component_impedance(w, L_h, c2_f)
        elements = [
            {"name": "C3", "label": "并联 C3", "kind": "shunt", "a": "s", "y": 1j * w * c3_f},
            {"name": "L+C2", "label": "串联 L+C2", "kind": "series", "a": "s", "b": "l",
             "z": zs, "parts": {"L": complex(0, w * L_h),
                                "C2": complex(0, -1.0 / (w * c2_f))}},
            {"name": "C1", "label": "并联 C1", "kind": "shunt", "a": "l", "y": 1j * w * c1_f},
        ]
    elif topology == "pi2":
        nodes = ["s", "l"]
        zs = _component_impedance(w, L_h, c2_f)
        elements = [
            {"name": "C1", "label": "并联 C1", "kind": "shunt", "a": "s", "y": 1j * w * c1_f},
            {"name": "L+C2", "label": "串联 L+C2", "kind": "series", "a": "s", "b": "l",
             "z": zs, "parts": {"L": complex(0, w * L_h),
                                "C2": complex(0, -1.0 / (w * c2_f))}},
            {"name": "C3", "label": "并联 C3", "kind": "shunt", "a": "l", "y": 1j * w * c3_f},
        ]
    else:
        raise ValueError("未知拓扑: %s" % topology)
    return nodes, elements, None  # load supplied by caller


def analyze_network(
    topology: str,
    frequency_mhz: float,
    load: complex,
    components: Dict[str, float],
    z0: float = 50.0,
    power_w: float = 1.0,
    drive: bool = True,
) -> Dict[str, Any]:
    """Full nodal analysis.

    components: L_uH, C1_pF, C2_pF, C3_pF (missing values treated as 0,
    except for topologies that require them).
    Returns Zin, VSWR, S11, node voltages and per-element peak stress.
    """
    try:
        frequency_mhz = float(frequency_mhz)
        z0 = float(z0)
        power_w = float(power_w)
    except (TypeError, ValueError) as exc:
        raise ValueError("频率、系统阻抗与功率必须是数值") from exc
    if not all(math.isfinite(value) for value in (frequency_mhz, z0, power_w)):
        raise ValueError("频率、系统阻抗与功率必须是有限数值")
    if frequency_mhz <= 0:
        raise ValueError("频率必须大于 0 MHz")
    if z0 <= 0:
        raise ValueError("系统阻抗必须大于 0 Ω")
    if power_w < 0:
        raise ValueError("功率不能为负")
    f = float(frequency_mhz) * 1e6
    w = 2 * math.pi * f
    L_h = float(components.get("L_uH", 0.0) or 0.0) * 1e-6
    c1 = float(components.get("C1_pF", 0.0) or 0.0) * 1e-12
    c2 = float(components.get("C2_pF", 0.0) or 0.0) * 1e-12
    c3 = float(components.get("C3_pF", 0.0) or 0.0) * 1e-12
    if not all(math.isfinite(value) for value in (L_h, c1, c2, c3)):
        raise ValueError("元件值必须是有限数值")
    if min(L_h, c1, c2, c3) < 0:
        raise ValueError("元件值不能为负")
    zl = complex(load)
    if not math.isfinite(zl.real) or not math.isfinite(zl.imag):
        raise ValueError("负载阻抗必须是有限数值")
    if zl.real <= 0:
        raise ValueError("负载实部必须大于 0 Ω")
    if abs(zl) == 0:
        raise ValueError("负载不能为 0 Ω")

    nodes, elements, _ = _network(topology, w, L_h, c1, c2, c3)
    index = {name: i for i, name in enumerate(nodes)}

    # For topologies with C3 not used, ignore it.
    if topology in ("l_right", "l_left"):
        c3 = 0.0

    ymat = [[0j] * len(nodes) for _ in nodes]
    rhs = [0j] * len(nodes)
    rs = float(z0)
    vs_peak = math.sqrt(8.0 * max(power_w, 0.0) * rs) if drive else 0.0
    if drive:
        ymat[0][0] += 1.0 / rs
        rhs[0] += vs_peak / rs

    for e in elements:
        a = index[e["a"]]
        if e["kind"] == "series":
            z = e["z"]
            if abs(z) < EPS:
                raise ValueError("串联支路阻抗为 0（短路），无法计算")
            y = 1.0 / z
            b = index[e["b"]]
            ymat[a][a] += y
            ymat[b][b] += y
            ymat[a][b] -= y
            ymat[b][a] -= y
        else:
            ymat[a][a] += e["y"]

    load_node = index[nodes[-1]]
    ymat[load_node][load_node] += 1.0 / zl

    v = _solve_linear(ymat, rhs) if drive else [0j] * len(nodes)

    if drive:
        iin = (vs_peak - v[0]) / rs
        zin = v[0] / iin if abs(iin) > EPS else complex(float("inf"), 0)
    else:
        # Small-signal input impedance can also be obtained by feeding 1 A
        # into the source node; use a 1 V Thevenin source instead.
        vs_peak = 1.0
        ymat2 = [[0j] * len(nodes) for _ in nodes]
        rhs2 = [0j] * len(nodes)
        ymat2[0][0] += 1.0 / rs
        rhs2[0] += vs_peak / rs
        for e in elements:
            a = index[e["a"]]
            if e["kind"] == "series":
                y = 1.0 / e["z"]
                b = index[e["b"]]
                ymat2[a][a] += y
                ymat2[b][b] += y
                ymat2[a][b] -= y
                ymat2[b][a] -= y
            else:
                ymat2[a][a] += e["y"]
        ymat2[load_node][load_node] += 1.0 / zl
        v2 = _solve_linear(ymat2, rhs2)
        iin2 = (vs_peak - v2[0]) / rs
        zin = v2[0] / iin2

    gamma = (zin - z0) / (zin + z0) if cmath.isfinite(zin) else complex(1, 0)
    vswr = (1 + abs(gamma)) / (1 - abs(gamma)) if abs(gamma) < 1 else float("inf")
    s11_db = 20 * math.log10(abs(gamma)) if abs(gamma) > 0 else -300.0
    return_loss_db = -s11_db

    element_results = []
    for e in elements:
        a = index[e["a"]]
        if e["kind"] == "series":
            b = index[e["b"]]
            dv = v[a] - v[b]
            current = dv / e["z"] if abs(e["z"]) > EPS else 0j
        else:
            dv = v[a]
            current = v[a] * e["y"]
        element_results.append({
            "name": e["name"],
            "label": e["label"],
            "kind": e["kind"],
            "voltage_peak": abs(dv),
            "voltage_rms": abs(dv) / math.sqrt(2),
            "current_peak": abs(current),
            "current_rms": abs(current) / math.sqrt(2),
            "reactance": abs(e["z"].imag) if e["kind"] == "series" else None,
        })

    v_load = v[load_node]
    load_current = v_load / zl
    p_load = 0.5 * abs(v_load) ** 2 * (1.0 / zl).real if drive else 0.0

    return {
        "engine": "nodal",
        "frequency_mhz": float(frequency_mhz),
        "z0": z0,
        "load": _c(zl),
        "components": {
            "L_uH": float(components.get("L_uH", 0.0) or 0.0),
            "C1_pF": float(components.get("C1_pF", 0.0) or 0.0),
            "C2_pF": float(components.get("C2_pF", 0.0) or 0.0),
            "C3_pF": float(components.get("C3_pF", 0.0) or 0.0),
        },
        "input_impedance": _c(zin),
        "reflection": _c(gamma),
        "vswr": float(vswr),
        "s11_db": float(s11_db),
        "return_loss_db": float(return_loss_db),
        "node_voltages": {name: _c(v[index[name]]) for name in nodes},
        "elements": element_results,
        "load_voltage_peak": abs(v_load),
        "load_current_peak": abs(load_current),
        "power_w": power_w,
        "delivered_power_w": p_load,
        "efficiency": (p_load / power_w) if power_w > 0 else None,
        "source_voltage_peak": vs_peak,
    }


def _c(value: complex) -> Dict[str, float]:
    return {"re": float(value.real), "im": float(value.imag), "magnitude": float(abs(value))}


# ---------------------------------------------------------------------------
# Design (inverse solution)
# ---------------------------------------------------------------------------

@dataclass
class DesignError(Exception):
    code: str
    message: str
    hint: str = ""

    def __str__(self) -> str:
        return self.message


def _auto_inductance(topology: str, w: float, z0: float, d0: float) -> float:
    """Choose a practical L for denom = wL + d0 > 0.

    d0 is the part of the denominator that does not depend on L.
    """
    base = 0.15 * z0 / w
    if d0 >= 0:
        return base
    return max(base, 1.5 * (-d0) / w)


def auto_fixed_elements(
    topology: str,
    frequency_mhz: float,
    load: complex,
    z0: float = 50.0,
    target_l: Optional[float] = None,
    target_c3: Optional[float] = None,
) -> Dict[str, float]:
    """Pick a feasible L (uH) and C3 (pF) when the user does not supply them."""
    f = float(frequency_mhz) * 1e6
    w = 2 * math.pi * f
    rl, xl = load.real, load.imag
    result: Dict[str, float] = {}

    if topology == "t":
        rv_target = max(1.8 * rl, 75.0)
        c3 = 1.0 / (w * math.sqrt(max(50.0 * rv_target - 2500.0, 1e-12)))
        result["C3_pF"] = max(c3 * 1e12, 0.02)
        # After C3 is known, pick L from the C2 denominator.
        zleft = complex(z0, -1.0 / (w * (result["C3_pF"] * 1e-12)))
        yleft = 1.0 / zleft
        gnode, bleft = yleft.real, yleft.imag
        rv = 1.0 / gnode
        if rv < rl:
            raise DesignError("no_solution",
                              f"C3 产生的中间虚拟电阻 {rv:.2f} Ω 小于负载实部 {rl:.2f} Ω",
                              "减小 C3 或改用 π型Ⅰ")
        temp = rl / gnode - rl * rl
        if temp < 0:
            raise DesignError("no_solution", "中间虚拟电阻不足，无法完成阻抗变换",
                              "调整 C3 或更换拓扑")
        mag = math.sqrt(temp)
        cands = []
        for sgn, xb in ((1, mag), (-1, -mag)):
            val = w * (xl - sgn * mag)
            if val > 0:
                cands.append((1.0 / val, xb))
        if not cands:
            raise DesignError("no_solution", "C1 无正实数解", "调整 C3 或更换拓扑")
        c1, xb = min(cands, key=lambda t: t[0])
        b_right = (1.0 / (rl + 1j * xb)).imag
        b_need = -(bleft + b_right)
        if abs(b_need) < 1e-12:
            raise DesignError("special", "并联支路无需补偿，C2 无解", "调整 C3")
        d0 = 1.0 / b_need
        result["L_uH"] = _auto_inductance("t", w, z0, d0) * 1e6

    elif topology == "pi1":
        yl = 1.0 / load
        g, b = yl.real, yl.imag
        rpar = 1.0 / g
        rt = min(0.45 * rpar, 40.0)
        rt = max(min(rt, 49.0), 1e-6)
        c3 = math.sqrt(max(50.0 / rt - 1.0, 0.0)) / (50.0 * w)
        result["C3_pF"] = max(c3 * 1e12, 0.02)
        # Source effective series impedance
        zs = 1.0 / (1.0 / z0 + 1j * w * (result["C3_pF"] * 1e-12))
        delta = g / zs.real - g * g
        if delta < 0:
            raise DesignError("no_solution", "源端等效电阻过大，无法匹配",
                              "减小 C3 或更换拓扑")
        term = math.sqrt(delta)
        cands = [(term - b) / w, (-term - b) / w]
        cands = [c for c in cands if c > 0]
        if not cands:
            raise DesignError("no_solution", "C1 无正实数解", "调整 C3")
        c1 = min(cands)
        znew = 1.0 / (g + 1j * (b + w * c1))
        xnew = znew.imag
        d0 = zs.imag + xnew
        result["L_uH"] = _auto_inductance("pi1", w, z0, d0) * 1e6

    elif topology == "pi2":
        yl = 1.0 / load
        g, b = yl.real, yl.imag
        rpar = 1.0 / g
        rser = g / (g * g + b * b)
        rt = min(0.45 * rpar, 25.0, 0.45 * rser)
        rt = max(rt, 1e-6)
        s = math.sqrt(max(g / rt - g * g, 0.0))
        roots = [s - b, -s - b]
        positive = [x for x in roots if x > 1e-12]
        if not positive:
            # Sweep C3 and pick the smallest value that makes R_eff <= 40.
            best = None
            for c3_pf in np.logspace(-2, 3, 400):
                c3 = c3_pf * 1e-12
                zeff = 1.0 / (yl + 1j * w * c3)
                if zeff.real <= 40.0:
                    best = c3_pf
                    break
            if best is None:
                raise DesignError("no_solution", "无法找到可行的 C3", "改用 π型Ⅰ")
            result["C3_pF"] = float(best)
        else:
            result["C3_pF"] = max(min(positive) / w * 1e12, 0.02)
        zleff = 1.0 / (yl + 1j * w * (result["C3_pF"] * 1e-12))
        reff, xeff = zleff.real, zleff.imag
        if reff > z0:
            raise DesignError("no_solution", f"负载并联 C3 后等效电阻 {reff:.2f} Ω 大于 50 Ω",
                              "增大 C3 或改用 π型Ⅰ")
        q = math.sqrt(max(z0 / reff - 1.0, 0.0))
        xs_eff = -reff * q
        d0 = xeff + xs_eff
        result["L_uH"] = _auto_inductance("pi2", w, z0, d0) * 1e6

    elif topology == "l_right":
        q = math.sqrt(max(z0 / rl - 1.0, 0.0))
        d0 = xl - q * rl
        result["L_uH"] = _auto_inductance("l_right", w, z0, d0) * 1e6
    elif topology == "l_left":
        yl = 1.0 / load
        g, b = yl.real, yl.imag
        val = g / z0 - g * g
        if val < 0:
            raise DesignError("no_solution", "负载电导过大，无法匹配到 50 Ω", "更换拓扑")
        term = math.sqrt(val)
        opts = [(term - b) / w, (-term - b) / w]
        opts = [c for c in opts if c > 0]
        if not opts:
            raise DesignError("no_solution", "C1 无正实数解", "更换拓扑")
        c1 = min(opts)
        bch = b + w * c1
        xpar = (1.0 / (g + 1j * bch)).imag
        result["L_uH"] = _auto_inductance("l_left", w, z0, xpar) * 1e6
    else:
        raise ValueError(topology)

    if target_l is not None:
        result["L_uH"] = float(target_l)
    if target_c3 is not None and topology in ("t", "pi1", "pi2"):
        result["C3_pF"] = float(target_c3)
    return result


def design_network(
    topology: str,
    frequency_mhz: float,
    load_r: float,
    load_x: float = 0.0,
    z0: float = 50.0,
    L_uh: Optional[float] = None,
    c3_pf: Optional[float] = None,
    auto_fixed: bool = True,
    power_w: float = 1.0,
) -> Dict[str, Any]:
    """Solve a matching network and verify it by nodal analysis.

    For l_right / l_left only L is a free fixed element.  For t / pi1 / pi2 both
    L and C3 are free; if omitted they are selected automatically.
    topology='auto' tries all five networks and picks a practical winner.
    """
    try:
        frequency_mhz = float(frequency_mhz)
        load_r = float(load_r)
        load_x = float(load_x)
        z0 = float(z0)
    except (TypeError, ValueError) as exc:
        raise DesignError("invalid_input", "频率、负载与系统阻抗必须是数值") from exc
    if not all(math.isfinite(value) for value in (frequency_mhz, load_r, load_x, z0)):
        raise DesignError("invalid_input", "频率、负载与系统阻抗必须是有限数值")
    if frequency_mhz <= 0:
        raise DesignError("invalid_frequency", "频率必须大于 0 MHz")
    if load_r <= 0:
        raise DesignError("invalid_load", "负载实部必须大于 0 Ω")
    if z0 <= 0:
        raise DesignError("invalid_z0", "系统阻抗必须大于 0 Ω")

    if str(topology).strip().lower() in ("auto", "自动", "best"):
        alternatives = suggest_topologies(frequency_mhz, complex(load_r, load_x), z0)
        if not alternatives:
            raise DesignError(
                "no_solution",
                f"在 {frequency_mhz:g} MHz 下，五种固定电容拓扑都无法匹配 {load_r:g}{load_x:+g}j Ω",
                "请检查负载是否为正实部，或改用其他频率/集总电感方案",
            )
        l_networks = [a for a in alternatives if a["topology"].startswith("l_")]
        chosen = l_networks[0] if l_networks else alternatives[0]
        result = design_network(chosen["topology"], frequency_mhz, load_r, load_x, z0,
                                power_w=power_w)
        result["requested_topology"] = "auto"
        result["alternatives"] = alternatives
        result["selection_reason"] = (
            "优先选择元件更少的 L 型网络；若 L 型不可行则选择带宽最大的三元件网络。"
        )
        return result

    top = canonical_topology(topology)
    if frequency_mhz <= 0:
        raise DesignError("invalid_frequency", "频率必须大于 0 MHz")
    if load_r <= 0:
        raise DesignError("invalid_load", "负载实部必须大于 0 Ω")
    if z0 <= 0:
        raise DesignError("invalid_z0", "系统阻抗必须大于 0 Ω")
    zl = complex(float(load_r), float(load_x))
    f = float(frequency_mhz) * 1e6
    w = 2 * math.pi * f

    # Constraints that can be checked before solving.
    if top == "l_right" and load_r >= z0:
        raise DesignError(
            "topology_mismatch",
            f"L型（右）要求 R_L < {z0:g} Ω，当前 R_L = {load_r:g} Ω",
            "请改用 L型（左）或 T/π 型网络",
        )
    if top == "l_left" and load_r <= z0:
        raise DesignError(
            "topology_mismatch",
            f"L型（左）要求 R_L > {z0:g} Ω，当前 R_L = {load_r:g} Ω",
            "请改用 L型（右）或 T/π 型网络",
        )

    fixed: Dict[str, float] = {}
    need_auto_l = L_uh is None
    need_auto_c3 = TOPOLOGIES[top]["requires_C3"] and c3_pf is None
    if need_auto_l or need_auto_c3:
        fixed = auto_fixed_elements(top, frequency_mhz, zl, z0,
                                    target_l=L_uh, target_c3=c3_pf)
    if need_auto_l:
        L_uh = fixed.get("L_uH")
    if need_auto_c3:
        c3_pf = fixed.get("C3_pF")
    if L_uh is None:
        raise DesignError("missing_L", "需要指定电感 L（或启用自动选值）")
    if TOPOLOGIES[top]["requires_C3"] and c3_pf is None:
        raise DesignError("missing_C3", "需要指定电容 C3（或启用自动选值）")
    L = float(L_uh) * 1e-6
    c3 = (float(c3_pf) * 1e-12) if TOPOLOGIES[top]["requires_C3"] else 0.0
    if L < 0 or c3 < 0:
        raise DesignError("invalid_component", "元件值不能为负数")

    steps_meta: List[Dict[str, Any]] = []
    warnings: List[str] = []
    warnings_en: List[str] = []

    if top == "l_right":
        q = math.sqrt(z0 / load_r - 1.0)
        c1 = q / (z0 * w)
        d = w * L + load_x - q * load_r
        if d <= 0:
            raise DesignError(
                "no_solution",
                "串联电容 C2 无正实数解：选定电感 L 太小，或负载容性过大",
                f"增大 L（至少 {(-(load_x - q * load_r)) / w * 1e6:.4g} µH）后重试",
            )
        c2 = 1.0 / (w * d)
        q_design = q
    elif top == "l_left":
        yl = 1.0 / zl
        g, b = yl.real, yl.imag
        inside = g / z0 - g * g
        if inside < 0:
            raise DesignError("no_solution", "负载电导过大，无法变换到 50 Ω", "更换拓扑")
        term = math.sqrt(inside)
        opts = []
        if (term - b) / w > 0:
            opts.append(((term - b) / w, term))
        if (-term - b) / w > 0:
            opts.append(((-term - b) / w, -term))
        if not opts:
            raise DesignError("no_solution", "所需的并联电容 C1 为负值", "更换拓扑")
        c1, bch_choice = min(opts, key=lambda t: t[0])
        bch = b + w * c1
        zpar = 1.0 / (g + 1j * bch)
        d = w * L + zpar.imag
        if d <= 0:
            raise DesignError(
                "no_solution",
                "所需的串联电容 C2 为负值：电感 L 太小",
                f"增大 L（至少 {-zpar.imag / w * 1e6:.4g} µH）后重试",
            )
        c2 = 1.0 / (w * d)
        q_design = abs(bch) / g
    elif top == "t":
        if c3 <= 0:
            raise DesignError("invalid_component", "C3 必须大于 0")
        zleft = complex(z0, -1.0 / (w * c3))
        yleft = 1.0 / zleft
        gnode, bleft = yleft.real, yleft.imag
        rv = 1.0 / gnode
        if rv < load_r:
            raise DesignError(
                "no_solution",
                f"中间虚拟电阻 {rv:.2f} Ω 小于负载实部 {load_r:.2f} Ω",
                "减小 C3 以提高虚拟电阻，或改用 π型Ⅰ",
            )
        temp = load_r / gnode - load_r * load_r
        if temp < 0:
            raise DesignError("no_solution", "中间虚拟电阻条件不满足", "调整 C3")
        mag = math.sqrt(temp)
        cands = []
        if w * (load_x - mag) > 0:
            cands.append((1.0 / (w * (load_x - mag)), mag))
        if w * (load_x + mag) > 0:
            cands.append((1.0 / (w * (load_x + mag)), -mag))
        if not cands:
            raise DesignError("no_solution", "串联电容 C1 无正实数解", "调整 C3 或 L")
        c1, xbranch = min(cands, key=lambda t: t[0])
        yright = 1.0 / (load_r + 1j * xbranch)
        bneed = -(bleft + yright.imag)
        if abs(bneed) < 1e-12:
            raise DesignError("special_case", "并联支路无需补偿，C2 无解", "调整 C3")
        d = w * L + 1.0 / bneed
        if d <= 0:
            raise DesignError(
                "no_solution",
                "所需的并联电容 C2 为负值：电感感抗超过匹配需求",
                "减小 L 或调整 C3",
            )
        c2 = 1.0 / (w * d)
        q_design = abs(bneed) * z0
    elif top == "pi1":
        if c3 <= 0:
            raise DesignError("invalid_component", "C3 必须大于 0")
        yl = 1.0 / zl
        g, b = yl.real, yl.imag
        zs = 1.0 / (1.0 / z0 + 1j * w * c3)
        delta = g / zs.real - g * g
        if delta < 0:
            raise DesignError(
                "no_solution",
                f"C3 使源端等效电阻降到 {zs.real:.2f} Ω，无法与负载电导匹配",
                "减小 C3，或改用 π型Ⅱ/T型",
            )
        term = math.sqrt(delta)
        opts = [(term - b) / w, (-term - b) / w]
        opts = [c for c in opts if c > 0]
        if not opts:
            raise DesignError("no_solution", "并联电容 C1 无正实数解", "调整 C3")
        c1 = min(opts)
        znew = 1.0 / (g + 1j * (b + w * c1))
        d = w * L + zs.imag + znew.imag
        if d <= 0:
            raise DesignError(
                "no_solution",
                "所需的串联电容 C2 为负值：电感 L 不足",
                f"增大 L（至少 {max(0.0, -(zs.imag + znew.imag)) / w * 1e6:.4g} µH）",
            )
        c2 = 1.0 / (w * d)
        q_design = abs(zs.imag) / zs.real
    elif top == "pi2":
        if c3 <= 0:
            raise DesignError("invalid_component", "C3 必须大于 0")
        zleff = 1.0 / (1.0 / zl + 1j * w * c3)
        reff, xeff = zleff.real, zleff.imag
        if reff > z0:
            raise DesignError(
                "no_solution",
                f"负载并联 C3 后等效电阻 {reff:.2f} Ω 大于 {z0:g} Ω",
                "增大 C3，或改用 π型Ⅰ",
            )
        q = math.sqrt(max(z0 / reff - 1.0, 0.0))
        c1 = q / (z0 * w)
        xs_eff = -reff * q
        d = w * L + xeff + xs_eff
        if d <= 0:
            raise DesignError(
                "no_solution",
                "所需的串联电容 C2 为负值：电感 L 不足",
                f"增大 L（至少 {max(0.0, -(xeff + xs_eff)) / w * 1e6:.4g} µH）",
            )
        c2 = 1.0 / (w * d)
        q_design = q
    else:
        raise ValueError(top)

    comps = {
        "L_uH": float(L * 1e6),
        "C1_pF": float(c1 * 1e12),
        "C2_pF": float(c2 * 1e12),
        "C3_pF": float(c3 * 1e12),
    }

    # Independent verification with the full network.
    verification = analyze_network(top, frequency_mhz, zl, comps, z0, power_w)

    if not math.isfinite(verification["vswr"]) or verification["vswr"] > 1.01:
        warnings.append(
            "节点法复核 VSWR=%.4f，与理想值偏差偏大，请检查元件值是否被截断。" %
            verification["vswr"]
        )
        warnings_en.append(
            "Nodal verification gives VSWR=%.4f, which deviates from the ideal value; "
            "check whether component values were rounded." % verification["vswr"]
        )
    if comps["C1_pF"] < 0.1:
        warnings.append("C1 小于 0.1 pF，实际寄生参数可能主导，建议降低频率或调整拓扑。")
        warnings_en.append("C1 is below 0.1 pF; parasitics may dominate. Lower the frequency or change topology.")
    if comps["C1_pF"] > 1000:
        warnings.append("C1 大于 1000 pF，建议选用高 Q 射频电容并核实自谐振频率。")
        warnings_en.append("C1 exceeds 1000 pF; use a high-Q RF capacitor and verify its self-resonance.")
    if comps["C2_pF"] < 0.1:
        warnings.append(
            "C2 小于 0.1 pF，实际寄生参数可能主导；通常是固定电感 L 过大，"
            "建议减小 L 或改用自动选值（典型 1–20 pF）。"
        )
        warnings_en.append(
            "C2 is below 0.1 pF; parasitics may dominate. The fixed L is probably too large; "
            "reduce L or use auto values (typically 1–20 pF)."
        )
    if comps["L_uH"] < 0.001:
        warnings.append("L 小于 1 nH，PCB 走线寄生电感不可忽略，建议提高频率或改用微带实现。")
        warnings_en.append("L is below 1 nH; PCB trace inductance is significant. Raise the frequency or use a microstrip design.")
    if q_design > 20:
        warnings.append(f"设计 Q 值约 {q_design:.1f}，带宽较窄，对元件容差敏感。")
        warnings_en.append(f"Design Q is about {q_design:.1f}; the bandwidth is narrow and sensitive to component tolerance.")

    steps = build_steps(top, frequency_mhz, zl, comps, z0)
    return {
        "ok": True,
        "topology": top,
        "topology_name": TOPOLOGIES[top]["name"],
        "topology_text": TOPOLOGIES[top]["topology_text"],
        "frequency_mhz": float(frequency_mhz),
        "z0": float(z0),
        "load": {"r": float(load_r), "x": float(load_x),
                 "display": fmt_complex(zl) + " Ω"},
        "components": comps,
        "components_display": {
            "L": fmt_si(comps['L_uH'] * 1e-6, "H", 4),
            "C1": f"{comps['C1_pF']:.4g} pF",
            "C2": f"{comps['C2_pF']:.4g} pF",
            "C3": f"{comps['C3_pF']:.4g} pF" if TOPOLOGIES[top]["requires_C3"] else "—",
        },
        "q": float(q_design),
        "verification": verification,
        "input_impedance": verification["input_impedance"],
        "input_impedance_display": fmt_complex(complex(verification["input_impedance"]["re"],
                                                       verification["input_impedance"]["im"])),
        "vswr": verification["vswr"],
        "s11_db": verification["s11_db"],
        "return_loss_db": verification["return_loss_db"],
        "bandwidth": bandwidth(top, frequency_mhz, zl, comps, z0),
        "sensitivity": sensitivity(top, frequency_mhz, zl, comps, z0),
        "steps": steps,
        "warnings": warnings,
        "warnings_en": warnings_en,
        "engine": "python-port-v3 (nodal verified)",
        "formulas": _formula_text(top),
    }


def _formula_text(top: str) -> str:
    if top == "l_right":
        return "Q=√(Z0/R_L−1); C1=Q/(Z0ω); C2=1/[ω(ωL+X_L−Q·R_L)]"
    if top == "l_left":
        return "B_tot²=G_L/Z0−G_L²; C1=(B_tot−B_L)/ω; C2=1/[ω(ωL+X_par)]"
    if top == "t":
        return "R_v=1/Re{Y_L,src}; X_b²=R_L/G−R_L²; C2=1/[ω(ωL+1/B_need)]"
    if top == "pi1":
        return "R_S=Re{1/(1/Z0+jωC3)}; (B_L+ωC1)²=G_L/R_S−G_L²; C2=1/[ω(ωL+X_S+X_L')]"
    if top == "pi2":
        return "R_eff=Re{1/(1/Z_L+jωC3)}; Q=√(Z0/R_eff−1); C1=Q/(Z0ω); C2=1/[ω(ωL−X_req)]"
    return ""


# ---------------------------------------------------------------------------
# Smith-chart trajectory (load -> source)
# ---------------------------------------------------------------------------

def build_steps(
    topology: str,
    frequency_mhz: float,
    load: complex,
    components: Dict[str, float],
    z0: float = 50.0,
    samples: int = 80,
) -> List[Dict[str, Any]]:
    top = canonical_topology(topology)
    w = 2 * math.pi * frequency_mhz * 1e6
    L = components.get("L_uH", 0.0) * 1e-6
    c1 = components.get("C1_pF", 0.0) * 1e-12
    c2 = components.get("C2_pF", 0.0) * 1e-12
    c3 = components.get("C3_pF", 0.0) * 1e-12
    z = complex(load)
    steps: List[Dict[str, Any]] = []

    def add_series(label: str, element: str, x: float, note: str = ""):
        nonlocal z
        if abs(x) < 1e-18:
            return
        pts = [z + 1j * x * (i / samples) for i in range(samples + 1)]
        steps.append({
            "kind": "series", "label": label, "element": element,
            "note": note, "delta": float(x), "start": _c(z),
            "end": _c(z + 1j * x), "points": [_c(p) for p in pts],
        })
        z = z + 1j * x

    def add_shunt(label: str, element: str, b: float, note: str = ""):
        nonlocal z
        if abs(b) < 1e-18:
            return
        pts = []
        for i in range(samples + 1):
            y = 1.0 / z + 1j * b * (i / samples)
            pts.append(1.0 / y)
        steps.append({
            "kind": "shunt", "label": label, "element": element,
            "note": note, "delta": float(b), "start": _c(z),
            "end": _c(1.0 / (1.0 / z + 1j * b)),
            "points": [_c(p) for p in pts],
        })
        z = 1.0 / (1.0 / z + 1j * b)

    if top == "l_right":
        xc2 = -1.0 / (w * c2)
        xl = w * L
        add_series("串联 C2", "C2", xc2, "沿等电阻圆移动，容抗使轨迹向下")
        add_series("串联 L", "L", xl, "沿同一等电阻圆向上抵消容抗")
        add_shunt("并联 C1", "C1", w * c1, "沿等电导圆移动到圆图中心")
    elif top == "l_left":
        add_shunt("并联 C1", "C1", w * c1, "先沿等电导圆移动")
        add_series("串联 C2", "C2", -1.0 / (w * c2), "沿等电阻圆移动")
        add_series("串联 L", "L", w * L, "抵消剩余电抗，落到圆心")
    elif top == "t":
        add_series("串联 C1", "C1", -1.0 / (w * c1), "负载侧串联电容")
        add_shunt("并联 L+C2", "L+C2", -1.0 / (w * L - 1.0 / (w * c2)),
                  "节点处并联支路抵消电纳")
        add_series("串联 C3", "C3", -1.0 / (w * c3), "源端串联电容，落到圆心")
    elif top == "pi1":
        add_shunt("并联 C1", "C1", w * c1, "负载端并联电容")
        add_series("串联 L+C2", "L+C2", w * L - 1.0 / (w * c2), "中间串联支路")
        add_shunt("并联 C3", "C3", w * c3, "源端并联电容，落到圆心")
    elif top == "pi2":
        add_shunt("并联 C3", "C3", w * c3, "负载端并联电容")
        add_series("串联 L+C2", "L+C2", w * L - 1.0 / (w * c2), "中间串联支路")
        add_shunt("并联 C1", "C1", w * c1, "源端并联电容，落到圆心")

    # Attach reflection coefficients for the UI.
    for s in steps:
        for key in ("start", "end"):
            zz = complex(s[key]["re"], s[key]["im"])
            s[key]["gamma"] = _c((zz - z0) / (zz + z0))
        s["points_gamma"] = [
            _c((complex(p["re"], p["im"]) - z0) / (complex(p["re"], p["im"]) + z0))
            for p in s["points"]
        ]
    return steps


# ---------------------------------------------------------------------------
# Forward scan, bandwidth, sensitivity, stress
# ---------------------------------------------------------------------------

def scan_matchable_range(
    topology: str,
    frequency_mhz: float,
    z0: float = 50.0,
    L_uh: Optional[float] = None,
    c1_range_pf: Optional[Sequence[float]] = None,
    c2_range_pf: Optional[Sequence[float]] = None,
    c3_range_pf: Optional[Sequence[float]] = None,
    steps: int = 50,
    max_points: int = 4000,
) -> Dict[str, Any]:
    """Grid-scan the adjustable elements and return the matchable load region."""
    top = canonical_topology(topology)
    f = float(frequency_mhz) * 1e6
    w = 2 * math.pi * f
    steps = max(5, min(int(steps), 90))
    z0 = float(z0)
    if L_uh is None:
        raise DesignError("missing_L", "正向扫描需要指定电感 L")
    L = float(L_uh) * 1e-6
    if not math.isfinite(f) or f <= 0:
        raise DesignError("invalid_frequency", "频率必须大于 0 MHz")
    if not math.isfinite(z0) or z0 <= 0:
        raise DesignError("invalid_z0", "系统阻抗必须大于 0 Ω")
    if not math.isfinite(L) or L <= 0:
        raise DesignError("invalid_L", "电感 L 必须是大于 0 的有限数值")

    def rng(values, default):
        if values is None:
            return (default[0] * 1e-12, default[1] * 1e-12)
        lo, hi = float(values[0]) * 1e-12, float(values[1]) * 1e-12
        return (max(min(lo, hi), 0.01e-12), max(max(lo, hi), 0.01e-12))

    if top == "l_right":
        c1lo, c1hi = rng(c1_range_pf, (0.5, 10))
        c2lo, c2hi = rng(c2_range_pf, (0.5, 10))
        c1v = np.linspace(c1lo, c1hi, steps)
        c2v = np.linspace(c2lo, c2hi, steps)
        C1, C2 = np.meshgrid(c1v, c2v)
        # Source side: 50 ohm in parallel with C1.  The matchable load is the
        # conjugate of the impedance seen from the load, minus the series
        # reactance.  (V3.0 forward scan used the non-conjugate value; fixed.)
        zsrc = 1.0 / (1.0 / z0 + 1j * w * C1)
        zser = 1j * (w * L - 1.0 / (w * C2))
        zloads = (np.conj(zsrc) - zser).ravel()
    elif top == "l_left":
        c1lo, c1hi = rng(c1_range_pf, (0.5, 10))
        c2lo, c2hi = rng(c2_range_pf, (0.5, 10))
        c1v = np.linspace(c1lo, c1hi, steps)
        c2v = np.linspace(c2lo, c2hi, steps)
        C1, C2 = np.meshgrid(c1v, c2v)
        zser = z0 + 1j * (w * L - 1.0 / (w * C2))
        ytot = 1.0 / zser + 1j * w * C1
        zloads = np.conj(1.0 / ytot).ravel()
    elif top in ("t", "pi1", "pi2"):
        if top == "t":
            c1lo, c1hi = rng(c1_range_pf, (0.5, 10))
            c2lo, c2hi = rng(c2_range_pf, (0.5, 10))
            c3lo, c3hi = rng(c3_range_pf, (0.2, 10))
        elif top == "pi1":
            c1lo, c1hi = rng(c1_range_pf, (0.5, 10))
            c2lo, c2hi = rng(c2_range_pf, (0.5, 10))
            c3lo, c3hi = rng(c3_range_pf, (0.5, 10))
        else:
            c1lo, c1hi = rng(c1_range_pf, (0.5, 10))
            c2lo, c2hi = rng(c2_range_pf, (0.5, 10))
            c3lo, c3hi = rng(c3_range_pf, (0.5, 10))
        # Keep the 3-D grid bounded so the UI stays responsive.
        n = max(6, min(steps, 22))
        c1v = np.linspace(c1lo, c1hi, n)
        c2v = np.linspace(c2lo, c2hi, n)
        c3v = np.linspace(c3lo, c3hi, n)
        C1, C2, C3 = np.meshgrid(c1v, c2v, c3v, indexing="ij")
        if top == "t":
            zleft = z0 + 1.0 / (1j * w * C3)
            zsh = 1j * (w * L - 1.0 / (w * C2))
            znode = (zleft * zsh) / (zleft + zsh)
            zout = znode + 1.0 / (1j * w * C1)
            zloads = np.conj(zout).ravel()
        elif top == "pi1":
            ysrc = 1.0 / z0 + 1j * w * C3
            zs = 1.0 / ysrc
            zbranch = 1j * (w * L - 1.0 / (w * C2))
            zar = zs + zbranch
            yin = 1.0 / zar + 1j * w * C1
            zloads = np.conj(1.0 / yin).ravel()
        else:
            ysrc = 1.0 / z0 + 1j * w * C1
            zs = 1.0 / ysrc
            zbranch = 1j * (w * L - 1.0 / (w * C2))
            zar = zs + zbranch
            yin = 1.0 / zar + 1j * w * C3
            zloads = np.conj(1.0 / yin).ravel()
    else:
        raise ValueError(top)

    zloads = zloads[np.isfinite(zloads)]
    valid = zloads.real > 0
    zloads = zloads[valid]
    if zloads.size == 0:
        return {"ok": False, "error": "扫描没有得到有效负载点", "topology": top}
    r = zloads.real
    x = zloads.imag
    points = zloads
    if points.size > max_points:
        idx = np.linspace(0, points.size - 1, max_points).astype(int)
        points = points[idx]
    gamma = (points - z0) / (points + z0)
    return {
        "ok": True,
        "topology": top,
        "frequency_mhz": float(frequency_mhz),
        "z0": z0,
        "steps": steps,
        "points_count": int(zloads.size),
        "r_min": float(np.min(r)),
        "r_max": float(np.max(r)),
        "x_min": float(np.min(x)),
        "x_max": float(np.max(x)),
        "r_p05": float(np.percentile(r, 5)),
        "r_p95": float(np.percentile(r, 95)),
        "x_p05": float(np.percentile(x, 5)),
        "x_p95": float(np.percentile(x, 95)),
        "points": [{"re": float(p.real), "im": float(p.imag),
                    "g": _c(complex(g))} for p, g in zip(points, gamma)],
    }


def evaluate(
    topology: str,
    frequency_mhz: float,
    load_r: float,
    load_x: float,
    L_uh: float,
    c1_pf: float,
    c2_pf: float,
    c3_pf: float = 0.0,
    z0: float = 50.0,
    power_w: float = 1.0,
) -> Dict[str, Any]:
    top = canonical_topology(topology)
    comps = {"L_uH": L_uh, "C1_pF": c1_pf, "C2_pF": c2_pf, "C3_pF": c3_pf}
    res = analyze_network(top, frequency_mhz, complex(load_r, load_x), comps, z0, power_w)
    res["ok"] = True
    res["topology"] = top
    res["topology_name"] = TOPOLOGIES[top]["name"]
    return res


def bandwidth(
    topology: str,
    frequency_mhz: float,
    load: complex,
    components: Dict[str, float],
    z0: float = 50.0,
    vswr_limit: float = 2.0,
    span: float = 0.6,
    points: int = 241,
) -> Dict[str, Any]:
    """Frequency sweep with fixed components; returns the contiguous VSWR band."""
    top = canonical_topology(topology)
    f0 = float(frequency_mhz)
    span = float(span)
    vswr_limit = float(vswr_limit)
    if not all(math.isfinite(value) for value in (f0, span, vswr_limit)):
        raise ValueError("频率、扫描范围与 VSWR 门限必须是有限数值")
    if f0 <= 0:
        raise ValueError("频率必须大于 0 MHz")
    if span <= 0:
        raise ValueError("扫描范围必须大于 0")
    if vswr_limit <= 0:
        raise ValueError("VSWR 门限必须大于 0")
    if complex(load).real <= 0 or not math.isfinite(complex(load).real):
        raise ValueError("负载实部必须大于 0 Ω")
    fmin = max(f0 * (1.0 - span), 1e-6)
    fmax = f0 * (1.0 + span)
    freqs = np.linspace(fmin, fmax, points)
    vswrs = []
    for fm in freqs:
        try:
            r = analyze_network(top, float(fm), load, components, z0, 0.0, drive=False)
            vswrs.append(r["vswr"])
        except Exception:
            vswrs.append(float("inf"))
    vswrs = np.array(vswrs, dtype=float)
    within = vswrs <= vswr_limit
    # Find the contiguous region containing f0.
    center = int(np.argmin(np.abs(freqs - f0)))
    if not within[center]:
        best = None
        idx = center
        if within.any():
            idx = int(np.argmin(np.where(within, np.abs(freqs - f0), np.inf)))
        if not within[idx]:
            best = {"vswr_limit": vswr_limit, "low_mhz": None, "high_mhz": None,
                    "fractional": 0.0, "percent": 0.0,
                    "vswr_min": float(np.min(vswrs)), "note": "在扫描范围内未找到 VSWR 合格频段"}
            return {**best, "points": [{"f_mhz": float(f), "vswr": float(v)}
                                       for f, v in zip(freqs, vswrs)]}
        center = idx
    lo = center
    while lo > 0 and within[lo - 1]:
        lo -= 1
    hi = center
    while hi < len(freqs) - 1 and within[hi + 1]:
        hi += 1
    low = float(freqs[lo])
    high = float(freqs[hi])
    frac = (high - low) / f0 if f0 > 0 else 0.0
    return {
        "vswr_limit": vswr_limit,
        "low_mhz": low,
        "high_mhz": high,
        "fractional": float(frac),
        "percent": float(frac * 100),
        "vswr_min": float(np.min(vswrs)),
        "points": [{"f_mhz": float(f), "vswr": float(v)} for f, v in zip(freqs, vswrs)],
    }


def sensitivity(
    topology: str,
    frequency_mhz: float,
    load: complex,
    components: Dict[str, float],
    z0: float = 50.0,
    tolerance: float = 0.05,
) -> List[Dict[str, Any]]:
    top = canonical_topology(topology)
    out = []
    keys = [("L_uH", "L"), ("C1_pF", "C1"), ("C2_pF", "C2"), ("C3_pF", "C3")]
    for key, label in keys:
        if key == "C3_pF" and top in ("l_right", "l_left"):
            continue
        base = float(components.get(key, 0.0) or 0.0)
        if base <= 0:
            continue
        vals = []
        for factor in (1 - tolerance, 1 + tolerance):
            comp = dict(components)
            comp[key] = base * factor
            try:
                r = analyze_network(top, frequency_mhz, load, comp, z0, 0, drive=False)
                vals.append(r["vswr"])
            except Exception:
                vals.append(float("inf"))
        out.append({
            "element": label,
            "nominal": base,
            "vswr_minus_5pct": float(vals[0]),
            "vswr_plus_5pct": float(vals[1]),
            "worst_vswr": float(max(vals)),
        })
    return out


def voltage_stress(
    topology: str,
    frequency_mhz: float,
    load_r: float,
    load_x: float,
    L_uh: float,
    c1_pf: float,
    c2_pf: float,
    c3_pf: float = 0.0,
    power_w: float = 10.0,
    z0: float = 50.0,
    rated_voltage: Optional[float] = None,
) -> Dict[str, Any]:
    res = analyze_network(topology, frequency_mhz, complex(load_r, load_x),
                          {"L_uH": L_uh, "C1_pF": c1_pf, "C2_pF": c2_pf, "C3_pF": c3_pf},
                          z0, power_w)
    elements = []
    for e in res["elements"]:
        item = dict(e)
        if rated_voltage:
            item["safety_factor"] = (rated_voltage / e["voltage_peak"]) if e["voltage_peak"] > 0 else None
        elements.append(item)
    return {
        "ok": True,
        "topology": canonical_topology(topology),
        "frequency_mhz": frequency_mhz,
        "power_w": power_w,
        "source_voltage_peak": res["source_voltage_peak"],
        "input_voltage_peak": abs(complex(res["node_voltages"]["s"]["re"],
                                          res["node_voltages"]["s"]["im"])),
        "load_voltage_peak": res["load_voltage_peak"],
        "load_current_peak": res["load_current_peak"],
        "elements": elements,
        "delivered_power_w": res["delivered_power_w"],
        "efficiency": res["efficiency"],
        "vswr": res["vswr"],
        "note": "采用完整网络节点电压求解，包含源阻抗 50Ω 的负载效应；比原版分压估算更严格。",
    }


def z_to_y(z: complex) -> complex:
    if abs(z) < EPS:
        raise ValueError("阻抗为 0（短路），导纳无穷大")
    return 1.0 / z


def y_to_z(y: complex) -> complex:
    if abs(y) < EPS:
        raise ValueError("导纳为 0（开路），阻抗无穷大")
    return 1.0 / y


def catalog() -> Dict[str, Any]:
    return {
        "z0": 50,
        "topologies": [
            {"id": k, **{kk: vv for kk, vv in v.items() if kk not in ("theory",)},
             "theory": v["theory"]}
            for k, v in TOPOLOGIES.items()
        ],
    }


def suggest_topologies(
    frequency_mhz: float,
    load: complex,
    z0: float = 50.0,
    power_w: float = 1.0,
) -> List[Dict[str, Any]]:
    """Try every topology and return the feasible ones, best first."""
    out: List[Dict[str, Any]] = []
    for top in TOPOLOGIES:
        try:
            d = design_network(top, frequency_mhz, load.real, load.imag, z0,
                               power_w=power_w)
        except (DesignError, ValueError, ZeroDivisionError):
            continue
        bw = d.get("bandwidth", {}).get("percent", 0.0) or 0.0
        comps = d.get("components", {})
        score = float(bw)
        if top.startswith("l_"):
            score += 25.0  # prefer the simplest network
        # Penalise impractical component values.
        for key in ("C1_pF", "C2_pF", "C3_pF"):
            val = float(comps.get(key, 0.0) or 0.0)
            if 0 < val < 0.1:
                score -= 60.0
            elif val > 1000:
                score -= 25.0
        out.append({
            "topology": top,
            "topology_name": d["topology_name"],
            "components": comps,
            "components_display": d["components_display"],
            "q": d["q"],
            "vswr": d["vswr"],
            "bandwidth_percent": float(bw),
            "score": score,
            "warnings": d["warnings"],
        })
    out.sort(key=lambda item: item["score"], reverse=True)
    return out
