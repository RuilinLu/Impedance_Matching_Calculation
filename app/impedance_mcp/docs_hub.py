"""Four-domain documentation hub with full-text and AI-assisted search.

Categories
----------
features : the desktop application itself (every view, input and output)
code     : AST-generated reference for every module, function and variable
ai       : model providers, protocols, capabilities, pricing and usage
mcp      : MCP transports, tools, resources, prompts and client examples

The content is plain Markdown kept inside the package, so it is searchable
character by character and never requires generating a PDF.
"""

from __future__ import annotations

import difflib
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import code_docs

PACKAGE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = PACKAGE_DIR / "docs_content"

CATEGORIES: List[Dict[str, Any]] = [
    {
        "id": "features",
        "title_zh": "软件功能文档",
        "title_en": "Application Guide",
        "desc_zh": "每个界面、输入框、按钮、输出指标与 Smith 圆图学习流程",
        "desc_en": "Every view, input, button, output metric and Smith-chart workflow",
    },
    {
        "id": "code",
        "title_zh": "代码参考文档",
        "title_en": "Code Reference",
        "desc_zh": "所有 Python 模块、函数、参数、返回值、局部变量与前端函数",
        "desc_en": "All Python modules, functions, parameters, returns, locals and front-end functions",
    },
    {
        "id": "ai",
        "title_zh": "AI 大模型接口",
        "title_en": "AI Model Interface",
        "desc_zh": "20 家厂商、协议、能力矩阵、视觉、价格、缓存与用量统计",
        "desc_en": "20 providers, protocols, capability matrix, vision, pricing, cache and usage",
    },
    {
        "id": "mcp",
        "title_zh": "MCP 协议接口",
        "title_en": "MCP Protocol",
        "desc_zh": "stdio / HTTP / SSE、工具参数、资源、提示模板与客户端配置",
        "desc_en": "stdio / HTTP / SSE, tool schemas, resources, prompts and client setup",
    },
]

CATEGORY_MAP = {c["id"]: c for c in CATEGORIES}

_TERM_RE = re.compile(r"[a-zA-Z0-9_./+\-]{2,}|[\u4e00-\u9fff]{2,}")
_CACHE: Dict[str, Any] = {"stamp": None, "code": {}}


def _category(category: str) -> Optional[Dict[str, Any]]:
    return CATEGORY_MAP.get(str(category or "").strip())


def _code_stamp() -> float:
    stamp = 0.0
    roots = [PACKAGE_DIR, PACKAGE_DIR / "web"]
    for root in roots:
        if not root.exists():
            continue
        for path in root.glob("*.py" if root == PACKAGE_DIR else "*.js"):
            try:
                stamp = max(stamp, path.stat().st_mtime)
            except OSError:
                continue
    return stamp


def _mcp_tools_markdown(lang: str = "zh") -> str:
    """Generate the live tool reference so parameters never go stale."""
    try:
        from . import tools
    except Exception:
        return ""
    zh = lang != "en"
    lines = [
        "## 工具参考 / Live tool reference",
        "",
        ("下表由 `tools.TOOL_SPECS` 实时生成，与内置智能体和 MCP 客户端看到的 schema 完全一致。"
         if zh else
         "The table below is generated from `tools.TOOL_SPECS` and matches the schema seen by the agent and MCP clients."),
        "",
    ]
    for spec in tools.TOOL_SPECS:
        schema = spec.get("inputSchema") or {}
        props = schema.get("properties") or {}
        required = set(schema.get("required") or [])
        lines += [f"### `{spec['name']}`", "", spec.get("description", ""), ""]
        if props:
            lines += ["| 参数 | 类型 | 必填 | 默认/枚举 | 说明 |", "|---|---|---|---|---|"]
            for name, meta in props.items():
                meta = meta or {}
                typ = meta.get("type", "—")
                if typ == "array":
                    typ = "array"
                extra = meta.get("default", "")
                if meta.get("enum"):
                    extra = ", ".join(str(x) for x in meta["enum"])
                default = str(extra) if extra not in ("", None) else "—"
                lines.append("| `{}` | `{}` | {} | `{}` | {} |".format(
                    name, typ, "是" if name in required else "否",
                    default.replace("|", "\\|")[:60],
                    str(meta.get("description", "")).replace("|", "\\|")))
            lines.append("")
    return "\n".join(lines)


def get_doc(category: str, lang: str = "zh") -> Dict[str, Any]:
    cat = _category(category)
    if not cat:
        return {"ok": False, "message": f"未知文档分类：{category}"}
    lang = "en" if str(lang).lower().startswith("en") else "zh"
    if cat["id"] == "code":
        stamp = _code_stamp()
        key = f"{lang}:{stamp}"
        if key not in _CACHE["code"]:
            _CACHE["code"] = {key: code_docs.generate_markdown(lang)}
        text = _CACHE["code"][key]
    else:
        path = CONTENT_DIR / f"{cat['id']}.{lang}.md"
        if not path.exists():
            path = CONTENT_DIR / f"{cat['id']}.zh.md"
        text = path.read_text(encoding="utf-8") if path.exists() else (
            f"# {cat['title_zh']}\n\n文档尚未安装。"
        )
    if cat["id"] == "mcp":
        text = text.rstrip() + "\n\n" + _mcp_tools_markdown(lang)
    return {
        "ok": True,
        "id": cat["id"],
        "title": cat["title_zh"] if lang == "zh" else cat["title_en"],
        "description": cat["desc_zh"] if lang == "zh" else cat["desc_en"],
        "lang": lang,
        "markdown": text,
        "chars": len(text),
        "lines": text.count("\n") + 1,
    }


def list_docs(lang: str = "zh") -> Dict[str, Any]:
    lang = "en" if str(lang).lower().startswith("en") else "zh"
    items = []
    for cat in CATEGORIES:
        doc = get_doc(cat["id"], lang)
        items.append({
            "id": cat["id"],
            "title": doc.get("title", cat["title_zh"]),
            "description": doc.get("description", ""),
            "chars": doc.get("chars", 0),
            "lines": doc.get("lines", 0),
        })
    return {"ok": True, "categories": items, "lang": lang}


def _terms(query: str) -> List[str]:
    q = (query or "").strip()
    terms: List[str] = []
    for token in _TERM_RE.findall(q):
        token = token.strip("._-/")
        if len(token) >= 2:
            terms.append(token)
    if len(q) <= 80 and q not in terms:
        terms.insert(0, q)
    for token in list(terms):
        if re.fullmatch(r"[\u4e00-\u9fff]{4,}", token):
            terms.extend(token[i:i + 2] for i in range(len(token) - 1))
    out, seen = [], set()
    for t in terms:
        key = t.casefold()
        if key not in seen:
            seen.add(key)
            out.append(t)
    return out[:12]


def _blocks(markdown: str) -> List[Dict[str, Any]]:
    """Split Markdown into searchable blocks while keeping line numbers."""
    lines = markdown.splitlines()
    blocks: List[Dict[str, Any]] = []
    heading = ""
    current: List[str] = []
    start_line = 1
    in_code = False

    def flush(end_line: int) -> None:
        nonlocal current, start_line
        text = "\n".join(current).strip()
        if text:
            blocks.append({
                "id": f"b{len(blocks) + 1}",
                "line": start_line,
                "end_line": end_line,
                "heading": heading,
                "text": text,
            })
        current = []
        start_line = end_line + 1

    for index, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
        if not in_code and re.match(r"^#{1,6}\s+", line):
            flush(index - 1)
            heading = re.sub(r"^#{1,6}\s+", "", line).strip()
            current = [line]
            start_line = index
            continue
        if not in_code and not line.strip():
            flush(index)
            start_line = index + 1
            continue
        if not current:
            start_line = index
        current.append(line)
    flush(len(lines))
    return blocks


def _score(text: str, terms: List[str], heading: str = "") -> float:
    lower = text.casefold()
    head = heading.casefold()
    score = 0.0
    for index, term in enumerate(terms):
        t = term.casefold()
        if not t:
            continue
        count = lower.count(t)
        if count:
            score += count * (8.0 if index == 0 else 2.5)
        if t in head:
            score += 10.0
    return score


def _snippet(text: str, terms: List[str], radius: int = 140) -> str:
    plain = re.sub(r"\s+", " ", text or " ").strip()
    lower = plain.casefold()
    positions = [lower.find(t.casefold()) for t in terms if lower.find(t.casefold()) >= 0]
    start = max(0, (min(positions) if positions else 0) - radius)
    end = min(len(plain), start + radius * 2)
    snippet = plain[start:end]
    if not snippet:
        return snippet
    pattern = re.compile(
        "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True) if term),
        re.I)
    return pattern.sub(lambda match: f"[[{match.group(0)}]]", snippet)


def search_docs(query: str, category: Optional[str] = None,
                lang: str = "zh", fuzzy: bool = True,
                limit: int = 60) -> Dict[str, Any]:
    query = (query or "").strip()
    if not query:
        return {"ok": True, "query": query, "results": [], "count": 0}
    lang = "en" if str(lang).lower().startswith("en") else "zh"
    terms = _terms(query)
    categories = ([_category(category)] if category else CATEGORIES)
    categories = [c for c in categories if c]
    results = []
    for cat in categories:
        doc = get_doc(cat["id"], lang)
        markdown = doc.get("markdown", "")
        for block in _blocks(markdown):
            score = _score(block["text"], terms, block["heading"])
            if score <= 0 and fuzzy:
                ratio = difflib.SequenceMatcher(
                    None, query.casefold(), block["text"][:600].casefold()).ratio()
                if ratio >= 0.62:
                    score = ratio * 3
            if score > 0:
                results.append({
                    "category": cat["id"],
                    "category_title": cat["title_zh"] if lang == "zh" else cat["title_en"],
                    "block_id": block["id"],
                    "line": block["line"],
                    "heading": block["heading"],
                    "snippet": _snippet(block["text"], terms),
                    "score": round(score, 2),
                })
    results.sort(key=lambda x: x["score"], reverse=True)
    # Avoid filling the list with near-duplicate paragraphs from one section.
    chosen, per_heading = [], {}
    for item in results:
        key = (item["category"], item["heading"])
        if per_heading.get(key, 0) >= 4:
            continue
        per_heading[key] = per_heading.get(key, 0) + 1
        chosen.append(item)
        if len(chosen) >= limit:
            break
    return {"ok": True, "query": query, "terms": terms,
            "results": chosen, "count": len(chosen), "fuzzy": bool(fuzzy)}


def ai_search_docs(query: str, cfg: Dict[str, Any], category: Optional[str] = None,
                   lang: str = "zh", limit: int = 60) -> Dict[str, Any]:
    terms: List[str] = []
    note = ""
    try:
        from . import llm
        prompt = (
            "你是技术文档检索助手。把用户问题改写成 4-10 个中英文关键词/同义词，"
            "用于检索本软件的四个文档域：软件功能、代码参考、AI 模型接口、MCP 协议。"
            "只输出 JSON 数组。\n用户问题：" + query
        )
        resp = llm.chat(cfg, [
            {"role": "system", "content": "只输出 JSON 数组，不要解释。"},
            {"role": "user", "content": prompt},
        ], timeout=45)
        match = re.search(r"\[[\s\S]*\]", resp.get("content") or "")
        if match:
            terms = [str(x) for x in json.loads(match.group(0)) if str(x).strip()][:10]
        note = f"AI 扩展词：{'、'.join(terms)}" if terms else "AI 未返回扩展词。"
    except Exception as exc:  # noqa: BLE001
        note = f"AI 扩展不可用（{exc}），已使用本地模糊检索。"
    merged: Dict[tuple, Dict[str, Any]] = {}
    for term in [query] + terms:
        result = search_docs(term, category=category, lang=lang, fuzzy=True, limit=limit)
        for item in result.get("results", []):
            key = (item["category"], item["block_id"])
            if key not in merged:
                item["matched_term"] = term
                merged[key] = item
            else:
                merged[key]["score"] = max(merged[key]["score"], item["score"]) + 1
    results = sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:limit]
    return {"ok": True, "query": query, "terms": terms, "note": note,
            "results": results, "count": len(results)}
