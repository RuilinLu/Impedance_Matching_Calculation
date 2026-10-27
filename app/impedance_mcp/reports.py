"""HTML / Markdown design-report generator (no external dependencies)."""

from __future__ import annotations

import datetime as _dt
import html
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

from . import config, engine

COLORS = ["#0ea5e9", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"]


def _e(text: Any) -> str:
    return html.escape(str(text), quote=True)


def _fmt(value: float, digits: int = 3) -> str:
    if value is None:
        return "—"
    if not math.isfinite(value):
        return "∞"
    return f"{value:.{digits}f}"


def _s11_text(v: float) -> str:
    return "< −60 dB（理想）" if v < -60 else f"{v:.2f} dB"


def _rl_text(v: float) -> str:
    return "> 60 dB（理想）" if v > 60 else f"{v:.2f} dB"


def _gamma(z: complex, z0: float) -> complex:
    return (z - z0) / (z + z0)


def _pt(g: complex, size: float = 520, pad: float = 42) -> Tuple[float, float]:
    r = (size - 2 * pad) / 2
    c = size / 2
    return (c + r * g.real, c - r * g.imag)


def smith_svg(steps: List[Dict[str, Any]], z0: float, size: int = 520) -> str:
    r = (size - 2 * 42) / 2
    c = size / 2
    parts = [
        f'<svg viewBox="0 0 {size} {size}" class="smith" xmlns="http://www.w3.org/2000/svg">',
        f'<defs><clipPath id="clip"><circle cx="{c}" cy="{c}" r="{r}"/></clipPath></defs>',
        f'<rect width="{size}" height="{size}" fill="#ffffff"/>',
        f'<circle cx="{c}" cy="{c}" r="{r}" fill="#fbfdff" stroke="#94a3b8" stroke-width="1.4"/>',
        '<g clip-path="url(#clip)" stroke="#dbe4ee" fill="none" stroke-width="0.8">',
    ]
    for rr in (0.0, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0):
        cx = c + r * rr / (1 + rr)
        rad = r / (1 + rr)
        parts.append(f'<circle cx="{cx:.2f}" cy="{c:.2f}" r="{rad:.2f}"/>')
    for xx in (0.2, 0.5, 1.0, 2.0, 5.0, 10.0):
        for sign in (1, -1):
            cy = c - sign * r / xx
            rad = r / xx
            parts.append(f'<circle cx="{c + r:.2f}" cy="{cy:.2f}" r="{rad:.2f}"/>')
    parts.append(f'<line x1="{c - r}" y1="{c}" x2="{c + r}" y2="{c}" stroke="#c7d2de"/>')
    parts.append('</g>')
    # axis labels
    for rr, label in ((0, "0"), (0.2, "0.2"), (0.5, "0.5"), (1, "1"), (2, "2"), (5, "5")):
        x = c + r * rr / (1 + rr)
        parts.append(f'<text x="{x:.1f}" y="{c + 16:.1f}" font-size="10" fill="#64748b" text-anchor="middle">{label}</text>')
    parts.append(f'<text x="{c}" y="{c - 8}" font-size="10" fill="#64748b" text-anchor="middle">Z0={z0:g}Ω</text>')
    parts.append(f'<circle cx="{c}" cy="{c}" r="3.2" fill="#0f172a"/>')
    # trajectory
    for i, s in enumerate(steps):
        pts = s.get("points_gamma") or []
        if not pts:
            continue
        coords = " ".join(f"{_pt(complex(p['re'], p['im']), size)[0]:.2f},"
                          f"{_pt(complex(p['re'], p['im']), size)[1]:.2f}" for p in pts)
        color = COLORS[i % len(COLORS)]
        parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2.6" '
                     f'stroke-linecap="round" stroke-linejoin="round"/>')
        end = complex(s["end"]["gamma"]["re"], s["end"]["gamma"]["im"])
        ex, ey = _pt(end, size)
        parts.append(f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="3.2" fill="{color}"/>')
    if steps:
        start = complex(steps[0]["start"]["gamma"]["re"], steps[0]["start"]["gamma"]["im"])
        sx, sy = _pt(start, size)
        parts.append(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="5.4" fill="#ef4444" stroke="#fff" stroke-width="1.4"/>')
        parts.append(f'<text x="{sx + 9:.1f}" y="{sy - 8:.1f}" font-size="11" fill="#b91c1c">负载</text>')
        end = complex(steps[-1]["end"]["gamma"]["re"], steps[-1]["end"]["gamma"]["im"])
        ex, ey = _pt(end, size)
        parts.append(f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="5.4" fill="#10b981" stroke="#fff" stroke-width="1.4"/>')
        parts.append(f'<text x="{ex + 9:.1f}" y="{ey - 8:.1f}" font-size="11" fill="#047857">匹配点</text>')
    # legend
    ly = 20
    for i, s in enumerate(steps):
        color = COLORS[i % len(COLORS)]
        parts.append(f'<rect x="18" y="{ly - 9}" width="10" height="10" rx="2" fill="{color}"/>')
        parts.append(f'<text x="34" y="{ly}" font-size="10.5" fill="#334155">{_e(s["label"])}</text>')
        ly += 16
    parts.append("</svg>")
    return "".join(parts)


def bandwidth_svg(bw: Dict[str, Any], width: int = 820, height: int = 240) -> str:
    pts = bw.get("points") or []
    if not pts:
        return ""
    f0 = [p["f_mhz"] for p in pts]
    v = [p["vswr"] for p in pts]
    fmin, fmax = min(f0), max(f0)
    vmax = max(3.0, min(10.0, max(v)))
    left, right, top, bottom = 64, width - 24, 18, height - 40

    def x(f):
        return left + (f - fmin) / (fmax - fmin) * (right - left)

    def y(vv):
        vv = min(vv, vmax)
        return bottom - (vv - 1.0) / (vmax - 1.0) * (bottom - top)

    path = " ".join(f"{x(f):.1f},{y(vv):.1f}" for f, vv in zip(f0, v))
    limit = bw.get("vswr_limit", 2.0)
    out = [f'<svg viewBox="0 0 {width} {height}" class="bwchart" xmlns="http://www.w3.org/2000/svg">',
           f'<rect width="{width}" height="{height}" fill="#fff"/>']
    # grid
    for vv in (1, 1.5, 2, 2.5, 3):
        if vv > vmax:
            continue
        yy = y(vv)
        out.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="#e2e8f0"/>')
        out.append(f'<text x="{left - 8}" y="{yy + 4:.1f}" font-size="10" fill="#64748b" text-anchor="end">{vv}</text>')
    if bw.get("low_mhz") and bw.get("high_mhz"):
        x1, x2 = x(bw["low_mhz"]), x(bw["high_mhz"])
        out.append(f'<rect x="{x1:.1f}" y="{top}" width="{max(0, x2 - x1):.1f}" height="{bottom - top}" fill="#22d3ee" opacity="0.13"/>')
    yy = y(limit)
    out.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="#ef4444" stroke-dasharray="5 4"/>')
    out.append(f'<text x="{right - 4}" y="{yy - 5:.1f}" font-size="10" fill="#b91c1c" text-anchor="end">VSWR {limit:g}</text>')
    out.append(f'<polyline points="{path}" fill="none" stroke="#0ea5e9" stroke-width="2.2"/>')
    out.append(f'<text x="{left}" y="{height - 10}" font-size="10" fill="#64748b">{fmin:.0f} MHz</text>')
    out.append(f'<text x="{right}" y="{height - 10}" font-size="10" fill="#64748b" text-anchor="end">{fmax:.0f} MHz</text>')
    out.append("</svg>")
    return "".join(out)


def topology_svg(top: str, comps: Dict[str, float]) -> str:
    labels = {
        "C1": f"C1\n{comps.get('C1_pF', 0):.3g}pF",
        "C2": f"C2\n{comps.get('C2_pF', 0):.3g}pF",
        "C3": f"C3\n{comps.get('C3_pF', 0):.3g}pF",
        "L": f"L\n{comps.get('L_uH', 0) * 1000:.3g}nH",
    }
    w, h = 820, 190
    out = [f'<svg viewBox="0 0 {w} {h}" class="topo" xmlns="http://www.w3.org/2000/svg">',
           f'<rect width="{w}" height="{h}" fill="#fff"/>']
    # source
    out.append('<circle cx="60" cy="80" r="18" fill="#e0f2fe" stroke="#0284c7" stroke-width="2"/>')
    out.append('<text x="60" y="85" font-size="12" fill="#0369a1" text-anchor="middle">50Ω</text>')
    out.append('<line x1="78" y1="80" x2="120" y2="80" stroke="#334155" stroke-width="2"/>')
    # load
    out.append(f'<line x1="700" y1="80" x2="742" y2="80" stroke="#334155" stroke-width="2"/>')
    out.append('<rect x="742" y="62" width="46" height="36" rx="6" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>')
    out.append('<text x="765" y="85" font-size="12" fill="#92400e" text-anchor="middle">ZL</text>')

    def series(x, text):
        out.append(f'<rect x="{x}" y="68" width="54" height="24" rx="4" fill="#f1f5f9" stroke="#475569" stroke-width="1.6"/>')
        out.append(f'<text x="{x + 27}" y="76" font-size="10" fill="#0f172a" text-anchor="middle">{_e(text.splitlines()[0])}</text>')
        out.append(f'<text x="{x + 27}" y="87" font-size="9" fill="#475569" text-anchor="middle">{_e(text.splitlines()[1]) if len(text.splitlines())>1 else ""}</text>')

    def shunt(x, text):
        out.append(f'<line x1="{x}" y1="80" x2="{x}" y2="128" stroke="#334155" stroke-width="1.8"/>')
        out.append(f'<rect x="{x - 24}" y="128" width="48" height="24" rx="4" fill="#ecfdf5" stroke="#059669" stroke-width="1.6"/>')
        out.append(f'<text x="{x}" y="136" font-size="9.5" fill="#065f46" text-anchor="middle">{_e(text.splitlines()[0])}</text>')
        out.append(f'<text x="{x}" y="146" font-size="8.5" fill="#047857" text-anchor="middle">{_e(text.splitlines()[1]) if len(text.splitlines())>1 else ""}</text>')
        out.append(f'<line x1="{x}" y1="152" x2="{x}" y2="166" stroke="#334155" stroke-width="1.8"/>')
        out.append(f'<line x1="{x - 12}" y1="166" x2="{x + 12}" y2="166" stroke="#334155" stroke-width="3"/>')

    if top == "l_right":
        shunt(180, labels["C1"]); out.append('<line x1="120" y1="80" x2="700" y2="80" stroke="#334155" stroke-width="2"/>')
        series(340, labels["L"]); series(470, labels["C2"])
    elif top == "l_left":
        out.append('<line x1="120" y1="80" x2="700" y2="80" stroke="#334155" stroke-width="2"/>')
        series(330, labels["L"]); series(440, labels["C2"]); shunt(640, labels["C1"])
    elif top == "t":
        series(180, labels["C3"]); out.append('<line x1="234" y1="80" x2="700" y2="80" stroke="#334155" stroke-width="2"/>')
        shunt(400, labels["L"] + "\n" + labels["C2"]); series(530, labels["C1"])
    elif top == "pi1":
        shunt(180, labels["C3"]); out.append('<line x1="120" y1="80" x2="700" y2="80" stroke="#334155" stroke-width="2"/>')
        series(330, labels["L"]); series(440, labels["C2"]); shunt(640, labels["C1"])
    elif top == "pi2":
        shunt(180, labels["C1"]); out.append('<line x1="120" y1="80" x2="700" y2="80" stroke="#334155" stroke-width="2"/>')
        series(330, labels["L"]); series(440, labels["C2"]); shunt(640, labels["C3"])
    out.append("</svg>")
    return "".join(out)


def markdown_report(d: Dict[str, Any], note: str = "") -> str:
    c = d["components"]
    bw = d["bandwidth"]
    lines = [
        "# 微波阻抗匹配设计报告",
        "",
        f"> 智配芯生 · ImpedanceMCP v{config.VERSION} ｜ 生成时间：{_dt.datetime.now():%Y-%m-%d %H:%M}",
        "",
        "## 1. 设计任务",
        "",
        f"- 工作频率：**{d['frequency_mhz']:g} MHz**",
        f"- 系统阻抗：**{d['z0']:g} Ω**",
        f"- 负载阻抗：**{d['load']['r']:g}{d['load']['x']:+g}j Ω**",
        f"- 选用拓扑：**{d['topology_name']}**（{d['topology_text']}）",
        "",
        "## 2. 元件值",
        "",
        "| 元件 | 数值 |",
        "|---|---|",
        f"| 电感 L | {c['L_uH'] * 1000:.4g} nH |",
        f"| 电容 C1 | {c['C1_pF']:.4g} pF |",
        f"| 电容 C2 | {c['C2_pF']:.4g} pF |",
    ]
    if engine.TOPOLOGIES[d["topology"]]["requires_C3"]:
        lines.append(f"| 电容 C3 | {c['C3_pF']:.4g} pF |")
    lines += [
        "",
        "## 3. 节点法复核",
        "",
        "| 指标 | 结果 |",
        "|---|---|",
        f"| 输入阻抗 Zin | {d['input_impedance_display']} Ω |",
        f"| 电压驻波比 VSWR | {d['vswr']:.6f} |",
        f"| S11 | {_s11_text(d['s11_db'])} |",
        f"| 回波损耗 | {_rl_text(d['return_loss_db'])} |",
        f"| 设计 Q | {d['q']:.3f} |",
        f"| VSWR<2 带宽 | {bw.get('low_mhz') or 0:.2f} – {bw.get('high_mhz') or 0:.2f} MHz"
        f"（{bw.get('percent', 0):.2f}%） |",
        "",
        "## 4. Smith 圆图步骤",
        "",
    ]
    for i, s in enumerate(d["steps"], 1):
        lines.append(f"{i}. **{s['label']}**（{s['kind']}）：{s['note']}")
    lines += ["", "## 5. ±5% 灵敏度", "", "| 元件 | 标称值 | -5% VSWR | +5% VSWR | 最差 |", "|---|---|---|---|---|"]
    for s in d.get("sensitivity", []):
        lines.append(f"| {s['element']} | {s['nominal']:.4g} | {s['vswr_minus_5pct']:.3f} | "
                     f"{s['vswr_plus_5pct']:.3f} | {s['worst_vswr']:.3f} |")
    lines += ["", "## 6. 设计公式", "", f"`{d.get('formulas', '')}`", "", "## 7. 风险提示", ""]
    if d.get("warnings"):
        lines += [f"- {w}" for w in d["warnings"]]
    else:
        lines.append("- 无显著风险；仍建议用实际元件模型复核。")
    if note:
        lines += ["", "## 8. 备注", "", note]
    lines += ["", "---", "", "开发者：Nova（诺瓦）、Echo（回声）、Iris（鸢尾）、Lumen（流明）",
              f"软件版本 v{config.VERSION} ｜ {config.RELEASE_DATE}"]
    return "\n".join(lines)


def html_report(d: Dict[str, Any], note: str = "") -> str:
    c = d["components"]
    bw = d["bandwidth"]
    rows = [
        ("电感 L", f"{c['L_uH'] * 1000:.4g} nH"),
        ("电容 C1", f"{c['C1_pF']:.4g} pF"),
        ("电容 C2", f"{c['C2_pF']:.4g} pF"),
    ]
    if engine.TOPOLOGIES[d["topology"]]["requires_C3"]:
        rows.append(("电容 C3", f"{c['C3_pF']:.4g} pF"))
    comp_rows = "".join(f"<tr><td>{_e(k)}</td><td class='v'>{_e(v)}</td></tr>" for k, v in rows)
    sens_rows = "".join(
        f"<tr><td>{_e(s['element'])}</td><td>{s['nominal']:.4g}</td>"
        f"<td>{s['vswr_minus_5pct']:.3f}</td><td>{s['vswr_plus_5pct']:.3f}</td>"
        f"<td class='{'bad' if s['worst_vswr'] > 2 else 'good'}'>{s['worst_vswr']:.3f}</td></tr>"
        for s in d.get("sensitivity", [])
    )
    warn = "".join(f"<li>{_e(w)}</li>" for w in d.get("warnings", [])) or "<li>无显著风险；仍建议用实际元件模型复核。</li>"
    steps = "".join(
        f"<li><b>{_e(s['label'])}</b><span class='tag'>{_e(s['kind'])}</span>"
        f"<p>{_e(s['note'])}</p></li>" for s in d["steps"]
    )
    bandwidth_html = bandwidth_svg(bw)
    smith = smith_svg(d["steps"], d["z0"])
    topo = topology_svg(d["topology"], c)
    note_html = f"<h2>8. 备注</h2><p>{_e(note)}</p>" if note else ""
    team = "、".join(m["name"] for m in config.TEAM)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>微波阻抗匹配设计报告 · {_e(d['topology_name'])}</title>
<style>
:root{{--ink:#0f172a;--muted:#64748b;--line:#e2e8f0;--brand:#0284c7;--bg:#f6f9fc}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:"Microsoft YaHei","Segoe UI",system-ui,sans-serif;line-height:1.75}}
.page{{max-width:980px;margin:28px auto;background:#fff;border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:0 12px 40px rgba(15,23,42,.08)}}
.hero{{padding:34px 44px 26px;background:linear-gradient(120deg,#071a2f,#0b3354 55%,#075985);color:#e8f6ff}}
.hero h1{{margin:0;font-size:30px;letter-spacing:.5px}}
.hero p{{margin:8px 0 0;color:#a9cbe4;font-size:13px}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:22px}}
.kpi{{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.16);border-radius:12px;padding:12px 14px}}
.kpi span{{display:block;font-size:11px;color:#9fc5df;letter-spacing:.4px}}
.kpi b{{font-size:20px;font-weight:600}}
section{{padding:8px 44px 4px}}
h2{{font-size:17px;margin:26px 0 10px;padding-left:10px;border-left:4px solid var(--brand)}}
p{{margin:6px 0;color:#334155;font-size:13.5px}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin:8px 0 4px}}
th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left}}
th{{background:#f1f6fb;color:#475569;font-weight:600}}
td.v{{font-family:Consolas,monospace;color:#075985}}
td.good{{color:#047857;font-weight:600}} td.bad{{color:#b91c1c;font-weight:600}}
.split{{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}}
.card{{border:1px solid var(--line);border-radius:12px;padding:14px;background:#fdfefe}}
.smith,.bwchart,.topo{{width:100%;height:auto;border-radius:10px}}
ol.steps{{padding-left:20px;margin:6px 0}}
ol.steps li{{margin:8px 0;font-size:13px}}
.tag{{display:inline-block;margin-left:8px;font-size:10.5px;color:#0e7490;background:#e0f2fe;border-radius:20px;padding:1px 8px}}
ol.steps p{{margin:2px 0 0;color:var(--muted)}}
ul.warn li{{font-size:12.5px;color:#92400e;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:7px 10px;margin:6px 0;list-style:none}}
.code{{font-family:Consolas,monospace;background:#0f172a;color:#e2e8f0;border-radius:10px;padding:14px;font-size:12.5px;overflow:auto}}
footer{{padding:20px 44px 30px;color:var(--muted);font-size:11.5px;border-top:1px solid var(--line);margin-top:22px}}
@media print{{body{{background:#fff}} .page{{box-shadow:none;border:0;margin:0;max-width:none}} .hero{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}}}
</style></head><body><div class="page">
<div class="hero">
<h1>微波阻抗匹配设计报告</h1>
<p>智配芯生 · ImpedanceMCP v{config.VERSION} ｜ {_dt.datetime.now():%Y-%m-%d %H:%M} ｜ {_e(d['topology_name'])}</p>
<div class="kpis">
<div class="kpi"><span>输入阻抗</span><b>{_e(d['input_impedance_display'])} Ω</b></div>
<div class="kpi"><span>VSWR</span><b>{d['vswr']:.4f}</b></div>
<div class="kpi"><span>S11</span><b>{_s11_text(d['s11_db'])}</b></div>
<div class="kpi"><span>VSWR&lt;2 带宽</span><b>{bw.get('percent', 0):.1f}%</b></div>
</div></div>
<section>
<h2>1. 设计任务</h2>
<p>工作频率 <b>{d['frequency_mhz']:g} MHz</b>，系统阻抗 <b>{d['z0']:g} Ω</b>，
负载阻抗 <b>{d['load']['r']:g}{d['load']['x']:+g}j Ω</b>。选用 <b>{_e(d['topology_name'])}</b>：
{_e(d['topology_text'])}。</p>
<div class="card">{topo}</div>
<h2>2. 元件值</h2>
<table><tr><th>元件</th><th>数值</th></tr>{comp_rows}</table>
<h2>3. 节点法复核</h2>
<table>
<tr><th>指标</th><th>结果</th><th>指标</th><th>结果</th></tr>
<tr><td>输入阻抗</td><td class="v">{_e(d['input_impedance_display'])} Ω</td><td>VSWR</td><td class="v">{d['vswr']:.6f}</td></tr>
<tr><td>S11</td><td class="v">{_s11_text(d['s11_db'])}</td><td>回波损耗</td><td class="v">{_rl_text(d['return_loss_db'])}</td></tr>
<tr><td>设计 Q</td><td class="v">{d['q']:.3f}</td><td>带宽（VSWR&lt;2）</td><td class="v">{bw.get('percent', 0):.2f}%</td></tr>
</table>
<p>带宽范围：{bw.get('low_mhz') or 0:.2f} – {bw.get('high_mhz') or 0:.2f} MHz。</p>
<div class="split">
<div class="card"><h3 style="margin:2px 0 6px;font-size:13px;color:#475569">Smith 圆图匹配轨迹</h3>{smith}</div>
<div class="card"><h3 style="margin:2px 0 6px;font-size:13px;color:#475569">VSWR 扫频曲线</h3>{bandwidth_html}
<h2 style="margin-top:18px">设计公式</h2><div class="code">{_e(d.get('formulas',''))}</div></div>
</div>
<h2>4. 匹配步骤</h2><ol class="steps">{steps}</ol>
<h2>5. ±5% 元件容差灵敏度</h2>
<table><tr><th>元件</th><th>标称值</th><th>-5% VSWR</th><th>+5% VSWR</th><th>最差</th></tr>{sens_rows}</table>
<h2>6. 风险提示</h2><ul class="warn">{warn}</ul>
{note_html}
</section>
<footer>开发者：{_e(team)}<br>
软件版本 v{config.VERSION} ｜ 更新日期 {config.RELEASE_DATE} ｜ 本报告由完整网络节点法自动生成</footer>
</div></body></html>"""


def generate(d: Dict[str, Any], fmt: str = "html", note: str = "") -> Path:
    config.ensure_dirs()
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_top = d["topology"]
    fmt = (fmt or "html").lower()
    if fmt in ("md", "markdown"):
        path = config.REPORT_DIR / f"impedance_report_{stamp}_{safe_top}.md"
        path.write_text(markdown_report(d, note), encoding="utf-8")
    else:
        path = config.REPORT_DIR / f"impedance_report_{stamp}_{safe_top}.html"
        path.write_text(html_report(d, note), encoding="utf-8")
    return path
