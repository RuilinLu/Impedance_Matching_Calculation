"""Tool registry shared by the MCP server and the local AI agent."""

from __future__ import annotations

import json
import math
import re
import urllib.parse
from typing import Any, Dict, List, Optional

from . import code_docs, config, docs_hub, engine, knowledge, library

TOPOLOGY_ENUM = ["auto", "l_right", "l_left", "t", "pi1", "pi2"]
FIXED_TOPOLOGY_ENUM = ["l_right", "l_left", "t", "pi1", "pi2"]


def _num(x: Any) -> float:
    return float(x)


def _round(x: float, n: int = 6) -> float:
    if not math.isfinite(x):
        return x
    return round(float(x), n)


def _comp_summary(d: Dict[str, Any]) -> str:
    c = d.get("components_display", {})
    parts = [f"L={c.get('L')}"]
    for key in ("C1", "C2", "C3"):
        if c.get(key) and c.get(key) != "—":
            parts.append(f"{key}={c[key]}")
    return "，".join(parts)


def _db_text(value: float) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    if v < -60:
        return "< -60 dB（理想匹配）"
    return f"{v:.2f} dB"


def _summary_design(d: Dict[str, Any]) -> str:
    bw = d.get("bandwidth", {}) or {}
    bw_txt = f"{bw.get('percent', 0):.1f}%" if bw.get("percent") is not None else "—"
    return (
        f"{d.get('topology_name', d.get('topology'))}：在 {d['frequency_mhz']:g} MHz 将 "
        f"{d['load']['r']:g}{d['load']['x']:+g}j Ω 匹配到 {d['z0']:g} Ω。"
        f"{_comp_summary(d)}；Zin={d['input_impedance_display']} Ω，"
        f"VSWR={d['vswr']:.6f}，S11={_db_text(d['s11_db'])}，"
        f"VSWR<2 带宽约 {bw_txt}，设计 Q≈{d['q']:.2f}。"
    )


def _compact_design(d: Dict[str, Any], include_steps: bool = True) -> Dict[str, Any]:
    out = {
        "ok": d.get("ok", True),
        "topology": d.get("topology"),
        "topology_name": d.get("topology_name"),
        "requested_topology": d.get("requested_topology"),
        "topology_text": d.get("topology_text"),
        "frequency_mhz": d.get("frequency_mhz"),
        "z0": d.get("z0"),
        "load": d.get("load"),
        "components": {k: _round(v, 6) for k, v in d.get("components", {}).items()},
        "components_display": d.get("components_display"),
        "q": _round(d.get("q", 0), 4),
        "input_impedance": d.get("input_impedance"),
        "input_impedance_display": d.get("input_impedance_display"),
        "vswr": _round(d.get("vswr", 0), 6),
        "s11_db": _round(max(d.get("s11_db", 0), -60), 3),
        "s11_db_display": _db_text(d.get("s11_db", 0)),
        "return_loss_db": _round(min(d.get("return_loss_db", 0), 60), 3),
        "bandwidth": {
            k: d.get("bandwidth", {}).get(k)
            for k in ("vswr_limit", "low_mhz", "high_mhz", "fractional", "percent", "vswr_min")
        },
        "sensitivity": d.get("sensitivity", []),
        "warnings": d.get("warnings", []),
        "formulas": d.get("formulas"),
        "summary": _summary_design(d),
    }
    if include_steps:
        out["steps"] = [
            {
                "label": s["label"],
                "element": s["element"],
                "kind": s["kind"],
                "note": s["note"],
                "start_impedance": s["start"],
                "end_impedance": s["end"],
            }
            for s in d.get("steps", [])
        ]
    if d.get("alternatives"):
        out["alternatives"] = [
            {k: a.get(k) for k in ("topology", "topology_name", "components_display",
                                   "q", "vswr", "bandwidth_percent", "score")}
            for a in d["alternatives"]
        ]
    if d.get("selection_reason"):
        out["selection_reason"] = d["selection_reason"]
    return out


def _ok(data: Dict[str, Any], summary: str) -> Dict[str, Any]:
    data = dict(data)
    data["ok"] = True
    data["summary"] = summary
    return data


def _err(exc: Exception) -> Dict[str, Any]:
    if isinstance(exc, engine.DesignError):
        return {
            "ok": False,
            "error_code": exc.code,
            "message": exc.message,
            "hint": exc.hint,
            "summary": f"计算失败：{exc.message}" + (f" 建议：{exc.hint}" if exc.hint else ""),
        }
    return {
        "ok": False,
        "error_code": "internal_error",
        "message": str(exc),
        "hint": "请检查输入参数是否为正数且单位正确（MHz、Ω、µH、pF）。",
        "summary": f"计算失败：{exc}",
    }


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def design_matching_network(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        d = engine.design_network(
            topology=args.get("topology", "auto"),
            frequency_mhz=_num(args["frequency_mhz"]),
            load_r=_num(args["load_r"]),
            load_x=_num(args.get("load_x", 0.0)),
            z0=_num(args.get("z0", 50.0)),
            L_uh=None if args.get("L_uh") in (None, "", 0) else _num(args["L_uh"]),
            c3_pf=None if args.get("c3_pf") in (None, "", 0) else _num(args["c3_pf"]),
            power_w=_num(args.get("power_w", 1.0)),
        )
        return _ok(_compact_design(d), _summary_design(d))
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def scan_matching_range(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        r = engine.scan_matchable_range(
            topology=args["topology"],
            frequency_mhz=_num(args["frequency_mhz"]),
            z0=_num(args.get("z0", 50.0)),
            L_uh=_num(args["L_uh"]),
            c1_range_pf=args.get("c1_range_pf"),
            c2_range_pf=args.get("c2_range_pf"),
            c3_range_pf=args.get("c3_range_pf"),
            steps=int(args.get("steps", 50)),
        )
        if not r.get("ok"):
            return r
        out = {k: v for k, v in r.items() if k != "points"}
        out["points_count"] = r.get("points_count")
        if args.get("include_points"):
            out["points"] = r.get("points", [])[:1200]
        out["summary"] = (
            f"{engine.TOPOLOGIES.get(r['topology'], {}).get('name', r['topology'])} 正向扫描："
            f"R {r['r_min']:.2f}–{r['r_max']:.2f} Ω，X {r['x_min']:.2f}–{r['x_max']:.2f} Ω，"
            f"共 {r['points_count']} 个有效点。"
        )
        return out
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def evaluate_network(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        r = engine.evaluate(
            topology=args["topology"],
            frequency_mhz=_num(args["frequency_mhz"]),
            load_r=_num(args["load_r"]),
            load_x=_num(args.get("load_x", 0.0)),
            L_uh=_num(args.get("L_uh", 0.0)),
            c1_pf=_num(args.get("C1_pF", 0.0)),
            c2_pf=_num(args.get("C2_pF", 0.0)),
            c3_pf=_num(args.get("C3_pF", 0.0)),
            z0=_num(args.get("z0", 50.0)),
            power_w=_num(args.get("power_w", 1.0)),
        )
        r["summary"] = (
            f"网络复核：Zin={engine.fmt_complex(complex(r['input_impedance']['re'], r['input_impedance']['im']))} Ω，"
            f"VSWR={r['vswr']:.4f}，S11={_db_text(r['s11_db'])}，"
            f"负载获得功率 {r['delivered_power_w']:.3f} W。"
        )
        return r
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def convert_impedance_admittance(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        mode = str(args.get("mode", "z2y")).lower()
        if mode in ("z2y", "z->y", "impedance_to_admittance"):
            z = complex(_num(args["real"]), _num(args.get("imag", 0.0)))
            y = engine.z_to_y(z)
            return {
                "ok": True,
                "mode": "z2y",
                "input": {"z": [z.real, z.imag]},
                "result": {"y": [y.real, y.imag]},
                "display": f"Y = {engine.fmt_complex(y)} S",
                "summary": f"Z={engine.fmt_complex(z)} Ω → Y={engine.fmt_complex(y)} S",
            }
        y = complex(_num(args["real"]), _num(args.get("imag", 0.0)))
        z = engine.y_to_z(y)
        return {
            "ok": True,
            "mode": "y2z",
            "input": {"y": [y.real, y.imag]},
            "result": {"z": [z.real, z.imag]},
            "display": f"Z = {engine.fmt_complex(z)} Ω",
            "summary": f"Y={engine.fmt_complex(y)} S → Z={engine.fmt_complex(z)} Ω",
        }
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def compute_voltage_stress(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        r = engine.voltage_stress(
            topology=args["topology"],
            frequency_mhz=_num(args["frequency_mhz"]),
            load_r=_num(args["load_r"]),
            load_x=_num(args.get("load_x", 0.0)),
            L_uh=_num(args["L_uh"]),
            c1_pf=_num(args["C1_pF"]),
            c2_pf=_num(args["C2_pF"]),
            c3_pf=_num(args.get("C3_pF", 0.0)),
            power_w=_num(args.get("power_w", 10.0)),
            z0=_num(args.get("z0", 50.0)),
            rated_voltage=None if args.get("rated_voltage") in (None, "", 0)
            else _num(args["rated_voltage"]),
        )
        worst = max(r["elements"], key=lambda e: e["voltage_peak"]) if r["elements"] else None
        r["summary"] = (
            f"{r['power_w']:g} W 输入时，输入峰值电压 {r['input_voltage_peak']:.2f} V"
            f"（源开路 {r['source_voltage_peak']:.2f} V），"
            + (f"最高元件峰值电压出现在 {worst['name']}：{worst['voltage_peak']:.2f} V。" if worst else "")
        )
        return r
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def analyze_bandwidth(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        comps = {
            "L_uH": _num(args["L_uh"]),
            "C1_pF": _num(args["C1_pF"]),
            "C2_pF": _num(args["C2_pF"]),
            "C3_pF": _num(args.get("C3_pF", 0.0)),
        }
        r = engine.bandwidth(
            args["topology"], _num(args["frequency_mhz"]),
            complex(_num(args["load_r"]), _num(args.get("load_x", 0.0))),
            comps, _num(args.get("z0", 50.0)),
            vswr_limit=_num(args.get("vswr_limit", 2.0)),
            span=_num(args.get("span", 0.6)),
        )
        r["ok"] = True
        limit = r.get("vswr_limit", args.get("vswr_limit", 2.0))
        r["summary"] = (
            f"VSWR<{limit:g} 的频段："
            + (f"{r['low_mhz']:.3f}–{r['high_mhz']:.3f} MHz（{r['percent']:.2f}%）"
               if r.get("low_mhz") else "未找到")
        )
        r.pop("points", None)
        return r
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def compare_topologies(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        res = engine.suggest_topologies(
            _num(args["frequency_mhz"]),
            complex(_num(args["load_r"]), _num(args.get("load_x", 0.0))),
            _num(args.get("z0", 50.0)),
        )
        if not res:
            return {
                "ok": False,
                "summary": "五种固定电容拓扑均无法匹配该负载，请改用其他频率或含串联电感的拓扑。",
                "alternatives": [],
            }
        best = res[0]
        return {
            "ok": True,
            "alternatives": res,
            "summary": (
                f"可行拓扑 {len(res)} 种，推荐 {best['topology_name']}："
                f"{best['components_display']}，带宽约 {best['bandwidth_percent']:.1f}%。"
            ),
        }
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def get_topology_guide(args: Dict[str, Any]) -> Dict[str, Any]:
    top = args.get("topology")
    if top:
        try:
            key = engine.canonical_topology(top)
        except Exception as exc:  # noqa: BLE001
            return _err(exc)
        info = dict(engine.TOPOLOGIES[key])
        info["id"] = key
        return {"ok": True, "topology": info,
                "summary": f"{info['name']}：{info['topology_text']}。{info['theory']}"}
    return {"ok": True, **engine.catalog(),
            "summary": "共支持 5 种拓扑：L型（右/左）、T型、π型Ⅰ/Ⅱ，另有 auto 自动选型。"}


def get_smith_trajectory(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        d = engine.design_network(
            args.get("topology", "auto"), _num(args["frequency_mhz"]),
            _num(args["load_r"]), _num(args.get("load_x", 0.0)),
            _num(args.get("z0", 50.0)),
            L_uh=None if args.get("L_uh") in (None, "", 0) else _num(args["L_uh"]),
            c3_pf=None if args.get("c3_pf") in (None, "", 0) else _num(args["c3_pf"]),
        )
        steps = []
        for s in d["steps"]:
            pts = list(s.get("points_gamma", []))
            if len(pts) > 60:
                idx = [round(i * (len(pts) - 1) / 59) for i in range(60)]
                pts = [pts[i] for i in idx]
            steps.append({
                "label": s["label"], "element": s["element"], "kind": s["kind"],
                "note": s["note"], "points_gamma": pts,
            })
        zl = complex(d["load"]["r"], d["load"]["x"])
        g = (zl - d["z0"]) / (zl + d["z0"])
        return {
            "ok": True,
            "topology": d["topology"],
            "topology_name": d["topology_name"],
            "frequency_mhz": d["frequency_mhz"],
            "z0": d["z0"],
            "load_gamma": {"re": g.real, "im": g.imag},
            "steps": steps,
            "summary": f"{d['topology_name']} 的 Smith 圆图轨迹共 {len(steps)} 段。",
        }
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def search_knowledge(args: Dict[str, Any]) -> Dict[str, Any]:
    r = knowledge.search(str(args.get("query", "")), int(args.get("limit", 4)))
    if r["results"]:
        r["summary"] = "；".join(item["title"] for item in r["results"])
    return r


def validate_design(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        r = engine.evaluate(
            args["topology"], _num(args["frequency_mhz"]),
            _num(args["load_r"]), _num(args.get("load_x", 0.0)),
            _num(args["L_uh"]), _num(args["C1_pF"]), _num(args["C2_pF"]),
            _num(args.get("C3_pF", 0.0)), _num(args.get("z0", 50.0)),
            _num(args.get("power_w", 1.0)),
        )
        issues = []
        if r["vswr"] > 1.5:
            issues.append(f"VSWR={r['vswr']:.2f} 偏高（目标 <1.5）")
        comps = r["components"]
        for key, label in (("C1_pF", "C1"), ("C2_pF", "C2"), ("C3_pF", "C3")):
            v = comps.get(key, 0)
            if v and v < 0.1:
                issues.append(f"{label}={v:.3g} pF 过小，寄生参数可能主导")
            if v > 1000:
                issues.append(f"{label}={v:.3g} pF 过大，需确认自谐振频率")
        if comps["L_uH"] and comps["L_uH"] < 0.001:
            issues.append("L<1 nH，PCB 走线电感不可忽略")
        verdict = "通过" if not issues else "存在风险"
        return {
            "ok": True,
            "verdict": verdict,
            "issues": issues,
            "vswr": r["vswr"],
            "s11_db": r["s11_db"],
            "input_impedance": r["input_impedance"],
            "summary": f"校验结论：{verdict}。" + ("；".join(issues) if issues else "该设计在数值上完全匹配。"),
        }
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def export_design_report(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from . import reports
        d = engine.design_network(
            args.get("topology", "auto"), _num(args["frequency_mhz"]),
            _num(args["load_r"]), _num(args.get("load_x", 0.0)),
            _num(args.get("z0", 50.0)),
            L_uh=None if args.get("L_uh") in (None, "", 0) else _num(args["L_uh"]),
            c3_pf=None if args.get("c3_pf") in (None, "", 0) else _num(args["c3_pf"]),
            power_w=_num(args.get("power_w", 1.0)),
        )
        fmt = str(args.get("format", "html")).lower()
        path = reports.generate(d, fmt=fmt, note=str(args.get("note", "")))
        return {
            "ok": True,
            "path": str(path),
            "format": fmt,
            "summary": f"报告已生成：{path}",
        }
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def _citation(item: Dict[str, Any], snippet: str = "") -> Dict[str, Any]:
    doc_id = int(item.get("doc_id") or 0)
    page = int(item.get("page") or 1)
    rects = item.get("rects") or []
    crop_url = ""
    if rects:
        encoded = urllib.parse.quote(
            json.dumps(rects, ensure_ascii=False, separators=(",", ":")), safe="")
        crop_url = f"/api/library/crop?doc={doc_id}&page={page}&rects={encoded}"
    return {
        "kind": "textbook",
        "doc_id": doc_id,
        "page": page,
        "title": item.get("title") or "",
        "snippet": snippet or item.get("snippet", ""),
        "rects": rects,
        "page_url": f"/api/library/page?doc={doc_id}&page={page}&zoom=1.0",
        "thumb_url": f"/api/library/page?doc={doc_id}&page={page}&zoom=0.55",
        "crop_url": crop_url,
    }


def search_textbooks(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        query = str(args.get("query") or "")
        result = library.search(
            query,
            doc_id=int(args["doc_id"]) if args.get("doc_id") else None,
            limit=int(args.get("limit", 12)),
            fuzzy=bool(args.get("fuzzy", True)),
            with_rects=bool(args.get("with_rects", True)),
        )
        if not result.get("ok"):
            return result
        citations = [_citation(item) for item in result.get("results", [])[:8]]
        result["citations"] = citations
        result["summary"] = (
            f"教材检索“{query}”命中 {result.get('count', 0)} 页；"
            + "；".join(f"{c['title']} 第 {c['page']} 页" for c in citations[:3])
            if citations else f"教材检索“{query}”没有命中。"
        )
        return result
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def read_textbook_page(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        doc_id = int(args["doc_id"])
        page = int(args["page"])
        info = library.page_info(doc_id, page, str(args.get("lang", "zh")))
        if not info.get("ok"):
            return info
        info["page_url"] = f"/api/library/page?doc={doc_id}&page={page}&zoom=1.0"
        info["thumb_url"] = f"/api/library/page?doc={doc_id}&page={page}&zoom=0.55"
        info["citations"] = [{
            "kind": "textbook", "doc_id": doc_id, "page": page,
            "title": info.get("title", ""), "snippet": (info.get("text") or "")[:300],
            "rects": [], "page_url": info["page_url"], "thumb_url": info["thumb_url"],
        }]
        if not (info.get("text") or "").strip():
            image = library.page_image_base64(doc_id, page, dpi=150)
            if image and args.get("include_image", True):
                info["_vision_image"] = {
                    "mime": image["mime"], "base64": image["base64"],
                    "name": f"{info.get('title', 'textbook')} p.{page}",
                    "doc_id": doc_id, "page": page,
                }
                info["summary"] = (
                    f"第 {page} 页没有文字层，已附上页面截图，可由支持视觉的模型阅读。"
                )
            else:
                info["summary"] = f"第 {page} 页没有文字层；请 OCR 或使用视觉模型。"
        else:
            info["summary"] = (
                f"{info.get('title')} 第 {page} 页：{re.sub(r'\\s+', ' ', info.get('text', ''))[:180]}…"
            )
        return info
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def translate_textbook_page(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        cfg = config.load_config()
        result = library.translate_page(
            int(args["doc_id"]), int(args["page"]), cfg,
            target_lang=args.get("target_lang") or None,
        )
        if result.get("ok"):
            result["summary"] = (
                f"第 {args['page']} 页已翻译为 {result.get('lang')}（{'缓存' if result.get('cached') else '新译'}）。"
            )
        return result
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def search_docs(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        query = str(args.get("query") or "")
        category = args.get("category") or None
        lang = str(args.get("lang", "zh"))
        result = docs_hub.search_docs(
            query, category=category, lang=lang,
            fuzzy=bool(args.get("fuzzy", True)),
            limit=int(args.get("limit", 30)),
        )
        if not result.get("ok"):
            return result
        result["citations"] = [{
            "kind": "documentation",
            "category": item["category"],
            "block_id": item["block_id"],
            "line": item["line"],
            "title": item["category_title"],
            "snippet": item["snippet"],
        } for item in result.get("results", [])[:8]]
        result["summary"] = (
            f"文档检索“{query}”命中 {result.get('count', 0)} 个段落。"
            if result.get("count") else f"文档检索“{query}”没有命中。"
        )
        return result
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def get_code_reference(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        module = str(args.get("module") or "").strip()
        function = str(args.get("function") or "").strip()
        if not module:
            modules = []
            for candidate in sorted(code_docs.PACKAGE_DIR.glob("*.py")):
                try:
                    modules.append(code_docs._module_info(candidate)["name"])
                except Exception:
                    modules.append(candidate.stem)
            return {
                "ok": True,
                "modules": modules,
                "summary": "请提供 module 参数；可用模块见 modules 列表。",
            }
        path = code_docs.PACKAGE_DIR / f"{module}.py"
        if not path.exists():
            return {"ok": False, "message": f"模块不存在：{module}", "summary": "模块不存在"}
        info = code_docs._module_info(path)
        items = []
        for fn in info["functions"]:
            if function and fn.name != function:
                continue
            signature = f"{fn.name}({', '.join(code_docs._signature_parts(fn))})"
            if getattr(fn, "returns", None) is not None:
                signature += " -> " + code_docs._annotation(fn.returns)
            items.append({
                "name": fn.name,
                "signature": signature,
                "line": fn.lineno,
                "doc": code_docs._docstring(fn),
                "parameters": [
                    {"name": row[0], "type": row[1], "default": row[2],
                     "kind": row[3], "description": row[4]}
                    for row in code_docs._function_rows(module, fn)
                ],
                "locals": code_docs._local_vars(fn),
            })
        return {
            "ok": True,
            "module": module,
            "doc": info["doc"],
            "constants": [
                {"name": name, "line": line, "value": value}
                for name, line, value in info["constants"]
            ],
            "functions": items,
            "summary": f"{module}：{len(items)} 个函数匹配。",
        }
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def get_library_status(args: Dict[str, Any]) -> Dict[str, Any]:
    state = library.status()
    docs = library.doc_list()
    state["documents"] = docs
    state["summary"] = (
        f"教材库：{state.get('docs', 0)} 本，{state.get('indexed_pages', 0)} 页有文字，"
        f"{state.get('ocr_pages', 0)} 页已 OCR，{state.get('needs_ocr', 0)} 页待 OCR。"
    )
    return state



def get_system_status(args: Dict[str, Any]) -> Dict[str, Any]:
    s = config.status()
    s["ok"] = True
    s["summary"] = (
        f"版本 {s['version']}；LLM {'已配置' if s['llm']['configured'] else '未配置'}；"
        f"MCP {s.get('mcp', {}).get('transport', 'stdio')}；"
        f"教材目录 {len(s.get('library_dirs', []))} 个。"
    )
    return s


def list_presets(args: Dict[str, Any]) -> Dict[str, Any]:
    presets = [
        {"name": "2.4 GHz Wi-Fi 低阻", "frequency_mhz": 2400, "load_r": 20, "load_x": 5,
         "topology": "auto"},
        {"name": "2.4 GHz 高阻", "frequency_mhz": 2400, "load_r": 100, "load_x": -30,
         "topology": "auto"},
        {"name": "433 MHz 短距无线", "frequency_mhz": 433, "load_r": 15, "load_x": 0,
         "topology": "l_right"},
        {"name": "915 MHz UHF RFID", "frequency_mhz": 915, "load_r": 80, "load_x": 20,
         "topology": "auto"},
        {"name": "1.8 GHz 功放负载", "frequency_mhz": 1800, "load_r": 12, "load_x": -8,
         "topology": "auto"},
        {"name": "5.8 GHz WLAN", "frequency_mhz": 5800, "load_r": 35, "load_x": 12,
         "topology": "auto"},
    ]
    return {"ok": True, "presets": presets,
            "summary": "提供 6 个常用频段与负载的演示预设。"}


HANDLERS = {
    "design_matching_network": design_matching_network,
    "scan_matching_range": scan_matching_range,
    "evaluate_network": evaluate_network,
    "convert_impedance_admittance": convert_impedance_admittance,
    "compute_voltage_stress": compute_voltage_stress,
    "analyze_bandwidth": analyze_bandwidth,
    "compare_topologies": compare_topologies,
    "get_topology_guide": get_topology_guide,
    "get_smith_trajectory": get_smith_trajectory,
    "search_knowledge": search_knowledge,
    "validate_design": validate_design,
    "export_design_report": export_design_report,
    "get_system_status": get_system_status,
    "list_presets": list_presets,
    "search_textbooks": search_textbooks,
    "read_textbook_page": read_textbook_page,
    "translate_textbook_page": translate_textbook_page,
    "search_docs": search_docs,
    "get_code_reference": get_code_reference,
    "get_library_status": get_library_status,
}


TOOL_SPECS: List[Dict[str, Any]] = [
    {
        "name": "design_matching_network",
        "description": (
            "设计微波阻抗匹配网络并返回元件值。输入频率(MHz)、负载实部/虚部(Ω)、拓扑。"
            "topology=auto 会自动比较 5 种拓扑并选优。L_uh、c3_pf 省略时自动选择实用值。"
            "返回 L(nH/µH)、C1/C2/C3(pF)、Zin、VSWR、S11、带宽、Q 值和设计步骤。"
            "适用于：为某个负载求匹配电容/电感、检查 L/T/π 网络是否可行。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "topology": {"type": "string", "enum": TOPOLOGY_ENUM,
                             "description": "拓扑；auto 表示自动选型"},
                "frequency_mhz": {"type": "number", "description": "工作频率，MHz"},
                "load_r": {"type": "number", "description": "负载电阻实部，Ω，必须>0"},
                "load_x": {"type": "number", "description": "负载电抗虚部，Ω，默认0"},
                "z0": {"type": "number", "description": "系统阻抗，Ω，默认50"},
                "L_uh": {"type": "number", "description": "固定电感，µH；省略则自动选取"},
                "c3_pf": {"type": "number", "description": "固定电容 C3，pF；T/π 型可省略"},
                "power_w": {"type": "number", "description": "用于效率/耐压估算的功率，W，默认1"},
            },
            "required": ["frequency_mhz", "load_r"],
        },
    },
    {
        "name": "scan_matching_range",
        "description": (
            "正向扫描：固定 L（以及可选 C3 范围），遍历可调电容范围，返回该拓扑能匹配的"
            "负载阻抗范围 Rmin/Rmax/Xmin/Xmax 与采样点。用于回答“这个网络能匹配哪些负载”。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "topology": {"type": "string", "enum": FIXED_TOPOLOGY_ENUM},
                "frequency_mhz": {"type": "number"},
                "L_uh": {"type": "number"},
                "z0": {"type": "number", "default": 50},
                "c1_range_pf": {"type": "array", "items": {"type": "number"},
                                "minItems": 2, "maxItems": 2},
                "c2_range_pf": {"type": "array", "items": {"type": "number"},
                                "minItems": 2, "maxItems": 2},
                "c3_range_pf": {"type": "array", "items": {"type": "number"},
                                "minItems": 2, "maxItems": 2},
                "steps": {"type": "integer", "minimum": 5, "maximum": 90, "default": 40},
                "include_points": {"type": "boolean", "default": False,
                                   "description": "是否返回圆图采样点（可能较大）"},
            },
            "required": ["topology", "frequency_mhz", "L_uh"],
        },
    },
    {
        "name": "evaluate_network",
        "description": (
            "用完整网络节点法复核给定元件值：返回 Zin、VSWR、S11、回波损耗、各节点电压、"
            "各元件峰值电压/电流、负载获得功率与效率。用于验证设计或分析失配。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "topology": {"type": "string", "enum": FIXED_TOPOLOGY_ENUM},
                "frequency_mhz": {"type": "number"},
                "load_r": {"type": "number"},
                "load_x": {"type": "number", "default": 0},
                "L_uh": {"type": "number"},
                "C1_pF": {"type": "number"},
                "C2_pF": {"type": "number"},
                "C3_pF": {"type": "number", "default": 0},
                "z0": {"type": "number", "default": 50},
                "power_w": {"type": "number", "default": 1},
            },
            "required": ["topology", "frequency_mhz", "load_r", "L_uh", "C1_pF", "C2_pF"],
        },
    },
    {
        "name": "convert_impedance_admittance",
        "description": "阻抗↔导纳换算。mode=z2y 时输入 real/imag 为 Z；mode=y2z 时输入为 Y。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mode": {"type": "string", "enum": ["z2y", "y2z"], "default": "z2y"},
                "real": {"type": "number"},
                "imag": {"type": "number", "default": 0},
            },
            "required": ["mode", "real"],
        },
    },
    {
        "name": "compute_voltage_stress",
        "description": (
            "计算匹配网络各元件的耐压/电流应力。输入功率(power_w)、频率、负载与元件值，"
            "返回源/负载/各元件峰值电压、RMS、峰值电流及可选额定电压安全系数。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "topology": {"type": "string", "enum": FIXED_TOPOLOGY_ENUM},
                "frequency_mhz": {"type": "number"},
                "load_r": {"type": "number"},
                "load_x": {"type": "number", "default": 0},
                "L_uh": {"type": "number"},
                "C1_pF": {"type": "number"},
                "C2_pF": {"type": "number"},
                "C3_pF": {"type": "number", "default": 0},
                "power_w": {"type": "number", "default": 10},
                "z0": {"type": "number", "default": 50},
                "rated_voltage": {"type": "number", "description": "元件额定电压峰值，V"},
            },
            "required": ["topology", "frequency_mhz", "load_r", "L_uh", "C1_pF", "C2_pF"],
        },
    },
    {
        "name": "analyze_bandwidth",
        "description": "固定元件值扫频，返回 VSWR 合格频段、分数带宽与 VSWR 曲线采样。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topology": {"type": "string", "enum": FIXED_TOPOLOGY_ENUM},
                "frequency_mhz": {"type": "number"},
                "load_r": {"type": "number"},
                "load_x": {"type": "number", "default": 0},
                "L_uh": {"type": "number"},
                "C1_pF": {"type": "number"},
                "C2_pF": {"type": "number"},
                "C3_pF": {"type": "number", "default": 0},
                "z0": {"type": "number", "default": 50},
                "vswr_limit": {"type": "number", "default": 2.0},
                "span": {"type": "number", "default": 0.6,
                         "description": "扫频范围 ±span×f0"},
            },
            "required": ["topology", "frequency_mhz", "load_r", "L_uh", "C1_pF", "C2_pF"],
        },
    },
    {
        "name": "compare_topologies",
        "description": "对给定频率与负载自动比较 5 种拓扑，返回可行方案、元件值、带宽、Q 与推荐排序。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "frequency_mhz": {"type": "number"},
                "load_r": {"type": "number"},
                "load_x": {"type": "number", "default": 0},
                "z0": {"type": "number", "default": 50},
            },
            "required": ["frequency_mhz", "load_r"],
        },
    },
    {
        "name": "get_topology_guide",
        "description": "查询 5 种匹配拓扑的原理、适用条件、电路结构、公式与元件清单。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topology": {"type": "string", "enum": FIXED_TOPOLOGY_ENUM},
            },
        },
    },
    {
        "name": "get_smith_trajectory",
        "description": "返回设计后 Smith 圆图轨迹（反射系数采样点），用于绘图或检查每段元件移动方向。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topology": {"type": "string", "enum": TOPOLOGY_ENUM, "default": "auto"},
                "frequency_mhz": {"type": "number"},
                "load_r": {"type": "number"},
                "load_x": {"type": "number", "default": 0},
                "z0": {"type": "number", "default": 50},
                "L_uh": {"type": "number"},
                "c3_pf": {"type": "number"},
            },
            "required": ["frequency_mhz", "load_r"],
        },
    },
    {
        "name": "search_knowledge",
        "description": "检索本地微波匹配知识库（圆图、L/T/π 网络、Q 与带宽、寄生、耐压、选型等）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 8, "default": 4},
            },
            "required": ["query"],
        },
    },
    {
        "name": "validate_design",
        "description": "工程校验：检查 VSWR、元件值是否过小/过大、是否可实现，并给出风险清单与结论。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topology": {"type": "string", "enum": FIXED_TOPOLOGY_ENUM},
                "frequency_mhz": {"type": "number"},
                "load_r": {"type": "number"},
                "load_x": {"type": "number", "default": 0},
                "L_uh": {"type": "number"},
                "C1_pF": {"type": "number"},
                "C2_pF": {"type": "number"},
                "C3_pF": {"type": "number", "default": 0},
                "z0": {"type": "number", "default": 50},
                "power_w": {"type": "number", "default": 1},
            },
            "required": ["topology", "frequency_mhz", "load_r", "L_uh", "C1_pF", "C2_pF"],
        },
    },
    {
        "name": "export_design_report",
        "description": "完成设计并导出 Markdown 或 HTML 报告（含参数、元件表、验证、圆图轨迹、灵敏度）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topology": {"type": "string", "enum": TOPOLOGY_ENUM, "default": "auto"},
                "frequency_mhz": {"type": "number"},
                "load_r": {"type": "number"},
                "load_x": {"type": "number", "default": 0},
                "z0": {"type": "number", "default": 50},
                "L_uh": {"type": "number"},
                "c3_pf": {"type": "number"},
                "power_w": {"type": "number", "default": 1},
                "format": {"type": "string", "enum": ["html", "md"], "default": "html"},
                "note": {"type": "string"},
            },
            "required": ["frequency_mhz", "load_r"],
        },
    },
    {
        "name": "search_textbooks",
        "description": (
            "在本地教材库中全文/模糊搜索（PDF、OCR 结果、TXT/Markdown）。返回书名、页码、"
            "命中片段、页面高亮矩形与缩略图 URL。支持中文、英文、代码与公式片段。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "doc_id": {"type": "integer", "description": "限定某本教材，省略表示全库"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 40, "default": 12},
                "fuzzy": {"type": "boolean", "default": True},
                "with_rects": {"type": "boolean", "default": True,
                               "description": "是否返回页面高亮矩形"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_textbook_page",
        "description": (
            "读取教材指定页的文字层或 OCR 文本，并返回页码、缩略图与引用信息。"
            "扫描页没有文字时，可返回页面截图供支持视觉的模型阅读。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "integer"},
                "page": {"type": "integer", "minimum": 1},
                "lang": {"type": "string", "enum": ["zh", "en"], "default": "zh"},
                "include_image": {"type": "boolean", "default": True,
                                  "description": "无文字层时是否附页面截图"},
            },
            "required": ["doc_id", "page"],
        },
    },
    {
        "name": "translate_textbook_page",
        "description": "把教材某页翻译为学术中文或英文；译文按页缓存，避免重复计费。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "integer"},
                "page": {"type": "integer", "minimum": 1},
                "target_lang": {"type": "string", "enum": ["zh", "en"]},
            },
            "required": ["doc_id", "page"],
        },
    },
    {
        "name": "search_docs",
        "description": (
            "检索软件内置的四类文档：features 软件功能、code 代码参考、ai 模型接口、"
            "mcp 协议接口。返回分类、段落、行号与高亮片段。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "category": {"type": "string", "enum": ["features", "code", "ai", "mcp"]},
                "lang": {"type": "string", "enum": ["zh", "en"], "default": "zh"},
                "fuzzy": {"type": "boolean", "default": True},
                "limit": {"type": "integer", "minimum": 1, "maximum": 80, "default": 30},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_code_reference",
        "description": (
            "返回由源码 AST 生成的代码参考：模块说明、模块常量、函数的完整签名、"
            "参数类型/默认值/作用、返回类型、异常与局部变量。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "module": {"type": "string", "description": "模块名，如 engine、llm、library"},
                "function": {"type": "string", "description": "可选：只看某个函数"},
            },
        },
    },
    {
        "name": "get_library_status",
        "description": "查询教材库索引状态：书籍数量、已索引页、OCR 页、待 OCR 页与文件列表。",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_system_status",
        "description": "查询软件版本、LLM 配置、MCP 运行状态与教材目录。",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_presets",
        "description": "列出常用频段/负载演示预设（Wi-Fi、433MHz、UHF RFID、WLAN 等）。",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


TOOL_MAP = {t["name"]: t for t in TOOL_SPECS}


def call_tool(name: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    fn = HANDLERS.get(name)
    if not fn:
        return {"ok": False, "error_code": "unknown_tool",
                "message": f"未知工具 {name}", "summary": f"未知工具 {name}"}
    try:
        return fn(args or {})
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def openai_tools() -> List[Dict[str, Any]]:
    return [{"type": "function",
             "function": {"name": t["name"], "description": t["description"],
                          "parameters": t["inputSchema"]}}
            for t in TOOL_SPECS]
