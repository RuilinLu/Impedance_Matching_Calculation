"""Generate the code-reference documentation from the live source tree.

The reference is produced with :mod:`ast`, so it cannot drift away from the
implementation: every module, class, function, parameter, default value and
module-level constant is listed with its source line.  Local variable names and
the call graph are included for navigation, while the function docstrings and
curated hints explain the physical meaning.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PACKAGE_DIR = Path(__file__).resolve().parent
# PyInstaller stores compiled modules in a PYZ archive, so the .py source is
# bundled separately under app_src/ for the generated code reference.
if getattr(sys, "frozen", False):
    _BUNDLED_SRC = Path(getattr(sys, "_MEIPASS", "")) / "app_src" / "impedance_mcp"
    if (_BUNDLED_SRC / "engine.py").exists():
        PACKAGE_DIR = _BUNDLED_SRC
APP_DIR = PACKAGE_DIR.parent
WEB_DIR = PACKAGE_DIR / "web"

MODULE_HINTS = {
    "engine": "微波网络计算内核：五种拓扑的解析设计、ABCD/节点法复核、扫描、带宽、灵敏度、耐压与拓扑比较。",
    "tools": "工具注册表：把计算内核包装成统一的 JSON 工具，供内置智能体与 MCP 客户端共同调用。",
    "agent": "内置 AI 智能体的工具调用循环、流式事件、系统提示词与结果裁剪。",
    "llm": "OpenAI 兼容 / Anthropic Messages 客户端，负责 URL 规范化、鉴权、重试、视觉消息与用量解析。",
    "providers": "模型厂商目录：内置 20 家厂商、能力/价格元数据、在线更新、AI 校对更新与回滚。",
    "usage": "Token、缓存命中、上下文占用与费用统计；按峰谷价格计算每次/累计成本。",
    "library": "教材库：PDF 索引、全文/模糊搜索、OCR、页面渲染、引用截图与学术翻译。",
    "docs_hub": "四类文档中心（功能、代码、AI 接口、MCP 协议）的全文检索与 AI 语义检索。",
    "attachments": "任意类型附件的接收、文本抽取、图片/扫描页视觉输入与剪贴板内容处理。",
    "mcp_server": "MCP stdio / Streamable HTTP / legacy SSE 服务器，暴露工具、资源与提示模板。",
    "web_server": "本地 HTTP API 与静态资源服务，负责设计、扫描、教材、文档、模型配置与 SSE 聊天。",
    "desktop": "原生 WebView2 桌面窗口与本地服务生命周期管理。",
    "config": "路径、版本、默认配置、密钥隐藏与 MCP 启动命令。",
    "reports": "HTML / Markdown 设计报告生成。",
    "knowledge": "内置微波匹配知识库与本地关键词检索。",
    "cleanup": "卸载与残留数据清理。",
    "configure_mcp": "把 MCP 启动配置写入常见客户端。",
    "launcher": "统一命令行入口：桌面窗口、浏览器模式、MCP、清理与客户端配置。",
    "run_app": "开发期桌面入口。",
    "run_mcp": "开发期 MCP stdio 入口。",
}

CONSTANT_HINTS = {
    "TOPOLOGIES": "五种匹配拓扑的元数据：名称、电路文字、理论说明与公式。",
    "TOPOLOGY_ENUM": "工具参数允许的拓扑枚举（含 auto）。",
    "FIXED_TOPOLOGY_ENUM": "固定拓扑枚举（不含 auto）。",
    "SYSTEM_PROMPT": "内置智能体的系统提示词：能力边界、工具使用规则、单位与安全约束。",
    "TOOL_LABELS": "工具名称到中文显示名的映射。",
    "PROTOCOL_VERSIONS": "MCP 服务器支持的协议版本集合。",
    "DEFAULT_PROTOCOL": "默认协商的 MCP 协议版本。",
    "MAX_BODY": "本地 HTTP 请求体上限。",
    "SUPPORTED_SUFFIXES": "教材库可索引的文件后缀。",
    "VERSION": "软件语义版本。",
    "RELEASE_DATE": "当前发布日。",
    "TEAM": "开发者名单与分工。",
    "LIBRARY_SOURCE_DIRS": "教材搜索目录（仓库 TextBook 与用户数据目录）。",
}

PARAM_HINTS: Dict[Tuple[str, str], Dict[str, str]] = {
    ("engine", "design_network"): {
        "topology": "自动选型或 l_right / l_left / t / pi1 / pi2。",
        "frequency_mhz": "工作频率，单位 MHz。",
        "load_r": "负载电阻实部 R_L，单位 Ω，必须为正。",
        "load_x": "负载电抗虚部 X_L，单位 Ω；容性为负。",
        "z0": "系统参考阻抗，默认 50 Ω。",
        "L_uh": "固定串联电感，单位 µH；None 时由拓扑与频率自动选取。",
        "c3_pf": "固定电容 C3，单位 pF；仅 T/π 型使用。",
        "power_w": "用于效率与耐压估算的输入功率，单位 W。",
    },
    ("engine", "analyze_network"): {
        "topology": "固定拓扑。",
        "frequency_mhz": "工作频率，MHz。",
        "load": "复负载阻抗，Ω。",
        "components": "包含 L_uH、C1_pF、C2_pF、C3_pF 的元件字典。",
        "z0": "参考阻抗，Ω。",
        "power_w": "输入功率，W。",
    },
    ("engine", "scan_matchable_range"): {
        "topology": "固定拓扑。",
        "frequency_mhz": "工作频率，MHz。",
        "z0": "参考阻抗，Ω。",
        "L_uh": "固定电感，µH。",
        "c1_range_pf": "C1 扫描范围 [min,max]，pF。",
        "c2_range_pf": "C2 扫描范围 [min,max]，pF。",
        "c3_range_pf": "C3 扫描范围 [min,max]，pF。",
        "steps": "每个维度的网格步数；三维拓扑会自动限制到 22。",
        "max_points": "返回圆图采样点的上限。",
    },
    ("engine", "evaluate"): {
        "topology": "固定拓扑。",
        "power_w": "用于计算元件电压/电流的输入功率，W。",
    },
    ("engine", "bandwidth"): {
        "vswr_limit": "带宽判据，默认 VSWR<2。",
        "span": "扫频范围 ±span×f0。",
    },
    ("engine", "voltage_stress"): {
        "rated_voltage": "元件额定峰值电压，用于安全系数；None 表示不计算。",
    },
    ("tools", "call_tool"): {
        "name": "工具名，必须存在于 HANDLERS。",
        "args": "工具参数字典，按 TOOL_SPECS 的 inputSchema 校验。",
    },
    ("llm", "chat"): {
        "cfg": "完整配置字典，读取 cfg['llm']。",
        "messages": "OpenAI 风格消息数组，可包含视觉 content 块。",
        "tools": "OpenAI function-calling 工具定义数组。",
        "tool_choice": "工具选择策略，默认 auto。",
        "timeout": "单次 HTTP 超时，秒。",
    },
    ("library", "search"): {
        "query": "用户输入的关键词或自然语言短语。",
        "doc_id": "限定某本教材；None 表示全部教材。",
        "limit": "返回结果页数上限。",
        "fuzzy": "是否启用 ASCII 拼写纠错与中文二字扩展。",
        "with_rects": "是否返回页面高亮矩形（用于定位引用）。",
    },
    ("library", "translate_page"): {
        "target_lang": "zh 或 en；None 时按原文语言自动选择。",
    },
    ("docs_hub", "search_docs"): {
        "query": "要检索的词或短语。",
        "category": "features / code / ai / mcp；None 表示全部。",
        "lang": "zh 或 en。",
        "fuzzy": "是否启用 difflib 模糊匹配。",
    },
}


def _annotation(node: Optional[ast.AST]) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _value_repr(node: Optional[ast.AST], limit: int = 90) -> str:
    if node is None:
        return ""
    try:
        text = ast.unparse(node)
    except Exception:
        text = "..."
    text = re.sub(r"\s+", " ", text)
    if len(text) > limit:
        text = text[:limit] + "…"
    return text


def _docstring(node: Any) -> str:
    doc = ast.get_docstring(node) or ""
    return doc.strip()


def _local_vars(func: ast.AST) -> List[str]:
    names: List[str] = []
    args = set()
    if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for a in func.args.args + func.args.posonlyargs + func.args.kwonlyargs:
            args.add(a.arg)
        if func.args.vararg:
            args.add(func.args.vararg.arg)
        if func.args.kwarg:
            args.add(func.args.kwarg.arg)
    for node in ast.walk(func):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id not in args and node.id not in names and not node.id.startswith("_"):
                names.append(node.id)
    return names[:24]


def _raises(node: ast.AST) -> List[str]:
    out = []
    for child in ast.walk(node):
        if isinstance(child, ast.Raise) and child.exc is not None:
            exc = child.exc
            if isinstance(exc, ast.Call):
                name = _annotation(exc.func)
            else:
                name = _annotation(exc)
            if name and name not in out:
                out.append(name)
    return out[:8]


def _function_rows(module: str, fn: ast.AST) -> List[Tuple[str, str, str, str, str]]:
    rows = []
    defaults: Dict[str, str] = {}
    args = list(getattr(fn.args, "posonlyargs", [])) + list(fn.args.args)
    for arg, default in zip(args[len(args) - len(fn.args.defaults):], fn.args.defaults):
        defaults[arg.arg] = _value_repr(default, 40)
    for arg, default in zip(fn.args.kwonlyargs, fn.args.kw_defaults):
        if default is not None:
            defaults[arg.arg] = _value_repr(default, 40)
    hints = PARAM_HINTS.get((module, fn.name), {})
    ordered = args + list(fn.args.kwonlyargs)
    if fn.args.vararg:
        ordered.append(fn.args.vararg)
    if fn.args.kwarg:
        ordered.append(fn.args.kwarg)
    for arg in ordered:
        name = arg.arg
        kind = "位置/关键字"
        if arg in getattr(fn.args, "posonlyargs", []):
            kind = "仅位置"
        elif arg in fn.args.kwonlyargs:
            kind = "仅关键字"
        elif fn.args.vararg is arg:
            kind = "可变位置"
        elif fn.args.kwarg is arg:
            kind = "可变关键字"
        rows.append((name, _annotation(arg.annotation) or "—",
                     defaults.get(name, "—"), kind, hints.get(name, "")))
    return rows


def _render_function(module: str, fn: ast.AST, prefix: str = "") -> List[str]:
    name = f"{prefix}{fn.name}"
    signature = f"{name}({', '.join(_signature_parts(fn))})"
    if getattr(fn, "returns", None) is not None:
        signature += " -> " + _annotation(fn.returns)
    lines = [f"##### `{module}.{name}`", "", "```python", signature, "```", ""]
    params = _function_rows(module, fn)
    if params:
        lines += ["| 参数 | 类型 | 默认值 | 传入方式 | 作用 |", "|---|---|---|---|---|"]
        for row in params:
            lines.append("| `{}` | `{}` | `{}` | {} | {} |".format(*row))
        lines.append("")
    returns = _annotation(getattr(fn, "returns", None))
    if returns:
        lines += [f"**返回**：`{returns}`", ""]
    raises = _raises(fn)
    if raises:
        lines += [f"**可能抛出**：{', '.join('`'+r+'`' for r in raises)}", ""]
    doc = _docstring(fn)
    if doc:
        lines += ["**说明**：", "", *doc.splitlines(), ""]
    locals_ = _local_vars(fn)
    if locals_:
        lines += ["**局部变量**：" + "、".join(f"`{x}`" for x in locals_), ""]
    lines += [f"**源码**：`{Path(fn.__dict__.get('_filename', '')).name}` 第 {getattr(fn, 'lineno', 0)} 行", ""]
    return lines


def _signature_parts(fn: ast.AST) -> List[str]:
    parts: List[str] = []
    defaults = [None] * (len(fn.args.args) - len(fn.args.defaults)) + list(fn.args.defaults)
    for arg, default in zip(fn.args.args, defaults):
        text = arg.arg
        if arg.annotation is not None:
            text += ": " + _annotation(arg.annotation)
        if default is not None:
            text += " = " + _value_repr(default, 36)
        parts.append(text)
    if fn.args.vararg:
        parts.append("*" + fn.args.vararg.arg)
    elif fn.args.kwonlyargs:
        parts.append("*")
    for arg, default in zip(fn.args.kwonlyargs, fn.args.kw_defaults):
        text = arg.arg
        if arg.annotation is not None:
            text += ": " + _annotation(arg.annotation)
        if default is not None:
            text += " = " + _value_repr(default, 36)
        parts.append(text)
    if fn.args.kwarg:
        parts.append("**" + fn.args.kwarg.arg)
    return parts


def _module_info(path: Path) -> Dict[str, Any]:
    source = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source, filename=str(path))
    info: Dict[str, Any] = {
        "name": path.stem,
        "path": str(path.relative_to(APP_DIR)),
        "lines": len(source.splitlines()),
        "doc": _docstring(tree),
        "constants": [],
        "functions": [],
        "classes": [],
    }
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            info["functions"].append(node)
        elif isinstance(node, ast.ClassDef):
            info["classes"].append(node)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    info["constants"].append((target.id, node.lineno, _value_repr(node.value)))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            info["constants"].append((node.target.id, node.lineno, _value_repr(node.value)))
    return info


def _js_inventory() -> List[Dict[str, Any]]:
    out = []
    for path in sorted(WEB_DIR.glob("*.js")):
        source = path.read_text(encoding="utf-8", errors="replace")
        declared = re.findall(
            r"^  (?:async\s+)?function\s+([A-Za-z_$][\w$]*)", source, re.M)
        declared += re.findall(
            r"^  (?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(",
            source, re.M)
        methods = re.findall(
            r"^    (?:async\s+)?([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{",
            source, re.M)
        ignore = {"if", "for", "while", "switch", "catch", "function", "return"}
        names = sorted({name for name in declared + methods
                        if name and name not in ignore})
        consts = sorted(set(re.findall(
            r"^  (?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=", source, re.M)))
        api = sorted(set(re.findall(r"window\.([A-Za-z_$][\w$]*)\s*=", source)))
        out.append({"file": path.name, "lines": len(source.splitlines()),
                    "functions": names, "constants": consts, "exports": api})
    return out


def generate_markdown(lang: str = "zh") -> str:
    modules = []
    for path in sorted(PACKAGE_DIR.glob("*.py")):
        if path.name.startswith("_") and path.name != "__init__.py":
            continue
        try:
            modules.append(_module_info(path))
        except Exception:
            continue
    modules.sort(key=lambda m: (m["name"] not in MODULE_HINTS, m["name"]))

    lines = [
        "# 代码参考手册 / Code Reference",
        "",
        "> 本文由源码 AST 自动生成：函数签名、参数、默认值、返回类型、异常、局部变量与模块常量均来自当前代码。"
        " 修改代码后重新打开本页即可获得最新版本。",
        "",
        "## 模块总览",
        "",
        "| 模块 | 文件 | 行数 | 函数/类 | 作用 |",
        "|---|---|---|---|---|",
    ]
    for mod in modules:
        count = len(mod["functions"]) + len(mod["classes"])
        lines.append("| `{}` | `{}` | {} | {} | {} |".format(
            mod["name"], mod["path"], mod["lines"], count,
            MODULE_HINTS.get(mod["name"], (mod["doc"] or "—").split("\n")[0][:80])))

    lines += [
        "",
        "## 调用示例",
        "",
        "```python",
        "from impedance_mcp import engine, tools, library, docs_hub, llm, config",
        "",
        "# 1) 解析设计：2.4 GHz，20+j5 Ω → 50 Ω",
        "design = engine.design_network('auto', 2400, 20, 5, 50)",
        "print(design['topology_name'], design['components'], design['vswr'])",
        "",
        "# 2) 通过统一工具接口调用（内置智能体与 MCP 共用）",
        "result = tools.call_tool('design_matching_network', {",
        "    'frequency_mhz': 2400, 'load_r': 20, 'load_x': 5, 'topology': 'auto'})",
        "",
        "# 3) 教材全文搜索与页面定位",
        "hits = library.search('Smith chart', limit=5)",
        "page = library.page_info(hits['results'][0]['doc_id'], hits['results'][0]['page'])",
        "",
        "# 4) 文档中心检索",
        "docs = docs_hub.search_docs('MCP tools', category='mcp')",
        "",
        "# 5) 直接调用模型（需在设置中配置服务商与 Key）",
        "cfg = config.load_config()",
        "reply = llm.chat(cfg, [{'role': 'user', 'content': '解释 VSWR 与回波损耗的关系'}])",
        "```",
        "",
        "## Python 模块详情",
        "",
    ]

    for mod in modules:
        lines += [f"### `{mod['name']}`", "",
                  f"- 文件：`{mod['path']}`",
                  f"- 行数：{mod['lines']}",
                  f"- 作用：{MODULE_HINTS.get(mod['name'], '—')}"]
        if mod["doc"]:
            lines += ["", mod["doc"]]
        if mod["constants"]:
            lines += ["", "#### 模块常量与变量", "",
                      "| 名称 | 行 | 当前值/表达式 | 说明 |", "|---|---|---|---|"]
            for name, lineno, value in mod["constants"]:
                lines.append("| `{}` | {} | `{}` | {} |".format(
                    name, lineno, value.replace("|", "\\|")[:80],
                    CONSTANT_HINTS.get(name, "模块级配置/常量")))
        if mod["functions"]:
            lines += ["", "#### 函数"]
            for fn in mod["functions"]:
                fn.__dict__["_filename"] = mod["path"]
                lines += _render_function(mod["name"], fn)
        for cls in mod["classes"]:
            lines += [f"#### 类 `{cls.name}`", ""]
            doc = _docstring(cls)
            if doc:
                lines += [doc, ""]
            lines += ["| 成员 | 类型 | 行 |", "|---|---|---|"]
            for item in cls.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    lines.append(f"| `{item.name}` | 方法 | {item.lineno} |")
            for item in cls.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    lines += [""]
                    lines += _render_function(mod["name"], item, prefix=cls.name + ".")
        lines.append("")

    lines += ["## 前端模块清单 / Front-end modules", "",
              "| 文件 | 行数 | 函数 | 常量 | 导出 |", "|---|---|---|---|---|"]
    for item in _js_inventory():
        lines.append("| `{}` | {} | {} | {} | {} |".format(
            item["file"], item["lines"],
            ", ".join(f"`{x}`" for x in item["functions"][:18]) or "—",
            ", ".join(f"`{x}`" for x in item["constants"][:12]) or "—",
            ", ".join(f"`{x}`" for x in item["exports"]) or "—"))
    lines += [
        "",
        "> 前端函数的局部变量位于源码中；本表列出所有函数、模块常量与 `window` 导出，便于按名字定位。",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_markdown())
