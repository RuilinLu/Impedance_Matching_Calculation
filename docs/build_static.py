"""Build the offline HTML manuals shipped with the installer.

Run from the project root:
    python docs/build_static.py
"""

from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

import markdown  # noqa: E402

from impedance_mcp import docs_hub  # noqa: E402

DOCS = Path(__file__).resolve().parent
ASSETS = DOCS / "assets"
VENDOR_SRC = ROOT / "app" / "impedance_mcp" / "web" / "vendor" / "mathjax"
VENDOR_DST = DOCS / "vendor" / "mathjax"

CATEGORIES = [
    ("features", "软件功能文档", "每个界面、输入框、按钮、输出指标与 Smith 圆图学习流程"),
    ("code", "代码参考文档", "模块、函数、参数、返回值、局部变量与前端函数"),
    ("ai", "AI 大模型接口", "厂商、协议、能力矩阵、视觉、价格、缓存与用量"),
    ("mcp", "MCP 协议接口", "stdio / HTTP / SSE、工具 schema、资源与提示模板"),
]

CSS = """
:root{--bg:#060b14;--panel:#0d1829;--line:#22324a;--text:#e8f0fc;--muted:#8ba0bd;--cyan:#22d3ee;--green:#34d399;--amber:#fbbf24}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(900px 600px at 20% -10%,#0e2a3a55,transparent),var(--bg);color:var(--text);font:14px/1.75 "Microsoft YaHei","Segoe UI",system-ui,sans-serif}
a{color:var(--cyan);text-decoration:none}a:hover{text-decoration:underline}
.layout{display:grid;grid-template-columns:250px minmax(0,1fr);min-height:100vh}
aside{position:sticky;top:0;height:100vh;overflow:auto;padding:22px 16px;border-right:1px solid var(--line);background:#08111fdd}
.brand{display:flex;gap:10px;align-items:center;margin-bottom:18px}.brand b{font-size:14px}.brand small{display:block;color:var(--muted);font-size:10px}
nav a{display:block;padding:8px 10px;border:1px solid transparent;border-radius:8px;color:var(--muted);font-size:12px;margin:3px 0}
nav a:hover,nav a.active{color:var(--cyan);border-color:#22d3ee44;background:#22d3ee0d}
main{max-width:1050px;padding:34px 42px 80px;min-width:0}
h1{font-size:27px;margin:0 0 10px}h2{font-size:20px;margin:26px 0 10px;border-bottom:1px solid var(--line);padding-bottom:5px}
h3{font-size:15px;margin:20px 0 7px;color:#d9f6ff}h4,h5{font-size:13px;color:var(--cyan);margin:16px 0 6px}
p,li{color:#c3d2e8;font-size:13px}blockquote{margin:12px 0;padding:10px 14px;border-left:3px solid var(--cyan);background:#22d3ee0a;color:var(--muted)}
code{background:#22d3ee12;color:#a5f3fc;padding:1px 4px;border-radius:4px;font-family:Consolas,monospace;font-size:12px}
pre{background:#060e1a;border:1px solid var(--line);border-radius:9px;padding:12px;overflow:auto}pre code{background:none;padding:0;color:#b9d7ee}
table{width:100%;border-collapse:collapse;margin:12px 0;font-size:12px}th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}th{background:#22d3ee10}
hr{border:0;border-top:1px solid var(--line);margin:24px 0}
.top{display:flex;gap:10px;align-items:center;justify-content:space-between;margin-bottom:18px;flex-wrap:wrap}
.tag{font-size:10px;border:1px solid #22d3ee44;color:var(--cyan);padding:2px 8px;border-radius:999px}
.lead{color:var(--muted);font-size:12px}.footer{margin-top:50px;border-top:1px solid var(--line);padding-top:12px;color:#647892;font-size:11px}
.card{display:block;border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:8px 0;background:#0d1829aa}
.card b{display:block;color:var(--text)}.card small{display:block;color:var(--muted);font-size:11px;margin-top:2px}
img{max-width:100%;border-radius:10px;border:1px solid var(--line);margin:8px 0;background:#fff}
mjx-container{max-width:100%;overflow-x:auto}
@media(max-width:900px){.layout{display:block}aside{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}main{padding:22px 18px 60px}}
"""

TEMPLATE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Impedance Matching AI</title>
<link rel="stylesheet" href="manual.css">
<script>
window.MathJax={{tex:{{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]]}},svg:{{fontCache:"global"}},
options:{{skipHtmlTags:["script","noscript","style","textarea","pre","code"]}}}};
</script>
<script src="vendor/mathjax/tex-svg-full.js"></script>
</head><body><div class="layout"><aside>
<div class="brand"><div><b>Impedance Matching AI</b><small>离线说明书 · v4.4.1</small></div></div>
<nav>{nav}</nav></aside><main>
<div class="top"><span class="tag">离线文档</span><a href="index.html">← 返回文档首页</a></div>
{content}
<div class="footer">Impedance Matching AI v4.4.0 · 教材与用户数据保存在本机，不上传。MathJax 3.2.2 (Apache-2.0)。</div>
</main></div></body></html>
"""


def _nav(current: str) -> str:
    items = ['<a class="{}" href="index.html">文档首页</a>'.format(
        "active" if current == "index" else "")]
    labels = {
        "features.zh": "软件功能文档",
        "code.zh": "代码参考文档",
        "ai.zh": "AI 大模型接口",
        "mcp.zh": "MCP 协议接口",
        "features.en": "Application Guide (EN)",
        "code.en": "Code Reference (EN)",
        "ai.en": "AI Interface (EN)",
        "mcp.en": "MCP Protocol (EN)",
        "教材库说明": "教材库与数据库",
        "安装与卸载说明": "安装与卸载",
    }
    for key, label in labels.items():
        items.append('<a class="{}" href="{}.html">{}</a>'.format(
            "active" if current == key else "", key, html.escape(label)))
    return "\n".join(items)


def _protect_code_and_math(text: str) -> tuple:
    code_items = []
    math_items = []

    def stash_code(raw: str, block: bool) -> str:
        code_items.append((raw, block))
        return f"MJXCODE{len(code_items) - 1}"

    def stash_math(raw: str, display: bool) -> str:
        math_items.append((raw, display))
        return f"MJXMATH{len(math_items) - 1}"

    text = re.sub(r"```[^\n]*\n([\s\S]*?)```", lambda m: stash_code(m.group(1), True), text)
    text = re.sub(r"`([^`\n]+)`", lambda m: stash_code(m.group(1), False), text)
    text = re.sub(r"\$\$([\s\S]+?)\$\$", lambda m: stash_math(f"\\[{m.group(1)}\\]", True), text)
    text = re.sub(r"\\\[([\s\S]+?)\\\]", lambda m: stash_math(f"\\[{m.group(1)}\\]", True), text)
    text = re.sub(r"\\\(([\s\S]+?)\\\)", lambda m: stash_math(f"\\({m.group(1)}\\)", False), text)
    text = re.sub(
        r"\\begin\{(equation|align|aligned|gather|gathered|multline|split|matrix|pmatrix|bmatrix|vmatrix|cases|array)\*?\}[\s\S]+?\\end\{\1\*?\}",
        lambda m: stash_math(f"\\[{m.group(0)}\\]", True), text)
    text = re.sub(r"\$([^$\n]+?)\$", lambda m: stash_math(f"\\({m.group(1)}\\)", False), text)
    return text, code_items, math_items


def _restore_code_and_math(body: str, code_items: list, math_items: list) -> str:
    def restore_code(match):
        index = int(match.group(1))
        if index >= len(code_items):
            return ""
        raw, block = code_items[index]
        code = html.escape(raw.strip("\n"))
        return f"<pre><code>{code}</code></pre>" if block else f"<code>{code}</code>"

    def restore_math(match):
        index = int(match.group(1))
        if index >= len(math_items):
            return ""
        raw, display = math_items[index]
        safe = html.escape(raw, quote=False)
        return f'<span class="math-display">{safe}</span>' if display else f'<span class="math-inline">{safe}</span>'

    body = re.sub(r"MJXCODE(\d+)", restore_code, body)
    body = re.sub(r"MJXMATH(\d+)", restore_math, body)
    return body


def _render_page(slug: str, title: str, markdown_text: str) -> Path:
    text, code_items, math_items = _protect_code_and_math(markdown_text)
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    body = _restore_code_and_math(body, code_items, math_items)
    target = DOCS / f"{slug}.html"
    target.write_text(
        TEMPLATE.format(title=html.escape(title), nav=_nav(slug), content=body),
        encoding="utf-8",
    )
    return target


def _copy_mathjax() -> None:
    VENDOR_DST.mkdir(parents=True, exist_ok=True)
    for name in ("tex-svg-full.js", "LICENSE"):
        source = VENDOR_SRC / name
        if source.exists():
            shutil.copy2(source, VENDOR_DST / name)


def _index() -> Path:
    cards = []
    for category, title, desc in CATEGORIES:
        cards.append(
            f'<a class="card" href="{category}.zh.html"><b>{html.escape(title)}</b>'
            f'<small>{html.escape(desc)}</small></a>'
            f'<a class="card" href="{category}.en.html"><b>{html.escape(title)} (English)</b>'
            f'<small>English edition</small></a>'
        )
    cards.append('<a class="card" href="教材库说明.html"><b>教材库与数据库</b>'
                 '<small>如何添加教材、OCR、数据库位置与备份</small></a>')
    cards.append('<a class="card" href="安装与卸载说明.html"><b>安装与卸载</b>'
                 '<small>安装路径、快捷方式、彻底卸载与数据清理</small></a>')
    images = ""
    if ASSETS.exists():
        for name, caption in (
            ("screenshot_design.png", "匹配设计"),
            ("screenshot_scan.png", "圆图分析"),
            ("screenshot_stress.png", "耐压分析"),
            ("screenshot_library.png", "教材库"),
            ("screenshot_docs.png", "文档中心"),
            ("screenshot_settings.png", "模型设置"),
            ("screenshot_agent.png", "AI 智能体"),
        ):
            if (ASSETS / name).exists():
                images += f'<figure><img src="assets/{name}" alt="{caption}"><figcaption>{caption}</figcaption></figure>'
    content = f"""
<h1>Impedance Matching AI 离线说明书</h1>
<p class="lead">v4.4.1 · 微波阻抗匹配、Smith 圆图、教材检索与 MCP 服务</p>
<blockquote>本软件是独立开源项目，不绑定任何平台或活动。所有计算、绘图、教材索引与 MCP 服务都在本机完成；只有 AI 对话会把当前问题与用户主动选择的附件发送给用户配置的模型服务商。</blockquote>
<h2>文档分类</h2>
{''.join(cards)}
<h2>界面截图</h2>
{images or '<p class="lead">截图将在安装包中提供；源码运行时可在软件内查看。</p>'}
<h2>快速开始</h2>
<ol>
<li>双击 <code>ImpedanceMatchingAI.exe</code> 打开软件。</li>
<li>在“设置 → 模型服务”中选择厂商、填写自己的 API Key；不配置模型也可使用全部本地计算。</li>
<li>在“教材库”点击“添加教材”，或把 PDF/DOCX/PPTX 放进 <code>TextBook/</code>。</li>
<li>在“文档中心”全文搜索本说明书，或使用右侧浮动 AI 边看边问。</li>
</ol>
"""
    target = DOCS / "index.html"
    target.write_text(
        TEMPLATE.format(title="文档首页", nav=_nav("index"), content=content),
        encoding="utf-8",
    )
    return target


def _library_help() -> Path:
    content = """
<h1>教材库与数据库</h1>
<p class="lead">教材库是本机的 SQLite 全文索引；教材文件不会上传。</p>
<h2>把教材放进哪里</h2>
<ul>
<li>安装目录或项目目录的 <code>TextBook/</code>；</li>
<li>用户数据目录 <code>%LOCALAPPDATA%\\ImpedanceMatchingAI\\TextBook\\</code>；</li>
<li><code>%LOCALAPPDATA%\\ImpedanceMatchingAI\\data\\library\\books\\</code>；</li>
<li>或直接在软件内点击“添加教材”。</li>
</ul>
<h2>路径管理</h2>
<p>教材库左侧“路径管理”会显示程序安装目录、用户数据目录与当前教材库。列表按从上到下的优先级扫描，可启用/停用、上移、下移、删除，也可添加任意本机文件夹。程序目录 <code>TextBook</code> 按安装位置动态解析，移动安装目录后自动生效。保存后会后台重建索引；不存在的目录会标记并跳过。教材库与阅读器之间还可左右拖动，阅读器与原文/翻译之间可上下拖动。</p>
<h2>数据库位置</h2>
<p>索引数据库：<code>%LOCALAPPDATA%\\ImpedanceMatchingAI\\data\\library\\index.sqlite3</code></p>
<p>页面缓存：<code>%LOCALAPPDATA%\\ImpedanceMatchingAI\\data\\library\\cache\\</code></p>
<p>安装程序会通过 <code>--init-data</code> 自动创建数据库、<code>books/</code>、<code>TextBook/</code> 与说明文件；首次打开教材库也会自动建立索引。</p>
<h2>支持格式</h2>
<p>PDF、TXT、Markdown、TeX、DOCX、PPTX、XLSX、IPYNB；旧版 .doc/.ppt/.xls 会尽量提取可读文本。扫描版 PDF 使用本地 RapidOCR，逐页或按页码范围识别。</p>
<h2>搜索与引用</h2>
<p>支持中文/英文全文搜索、模糊搜索、AI 语义扩展、页码定位、命中矩形、页面缩放与学术翻译。AI 引用会带书名、页码和命中区域截图。</p>
<h2>备份</h2>
<p>直接备份 <code>index.sqlite3</code> 即可保留索引、OCR 结果与翻译缓存；教材原件请另行备份。</p>
"""
    return _render_page("教材库说明", "教材库与数据库", content)


def _install_help() -> Path:
    content = """
<h1>安装与卸载</h1>
<h2>安装</h2>
<ol>
<li>运行 <code>Impedance_Matching_AI_v4.4.1_Setup.exe</code>。</li>
<li>选择安装目录（默认 <code>%LOCALAPPDATA%\\Programs\\Impedance Matching AI</code>）。程序、MCP 服务与 <code>TextBook/</code> 会跟随所选目录。</li>
<li>安装程序会安装原生窗口、MCP 服务、离线说明书与 MathJax，并创建桌面/开始菜单快捷方式。</li>
<li>首次启动会创建用户数据目录（<code>%LOCALAPPDATA%\\ImpedanceMatchingAI</code>）与教材数据库。</li>
</ol>
<h2>移动安装位置</h2>
<p>程序目录中的 <code>TextBook</code> 会按当前安装位置动态解析，移动程序后无需手改路径。可把旧教材复制到新目录的 <code>TextBook</code>，或在“教材库 → 路径管理”中添加旧目录并调整优先级。若使用自定义数据目录，可在程序目录放置 <code>data_root.txt</code>，写入数据目录的绝对路径。</p>
<h2>目录结构</h2>
<pre>Impedance Matching AI/
  ImpedanceMatchingAI.exe         主程序（原生 WebView2 窗口）
  ImpedanceMatchingAI_MCP.exe     MCP stdio / HTTP 服务
  docs/                            离线说明书（HTML + 截图 + MathJax）
  TextBook/                        随安装目录变化的教材入口（可选）
  data_root.txt                    可选：自定义用户数据目录
%LOCALAPPDATA%/ImpedanceMatchingAI/
  data/                            配置、教材索引、上传、报告、更新缓存
  TextBook/                        保留/迁移的教材
  webview/                         WebView2 缓存</pre>
<h2>卸载</h2>
<p>开始菜单或桌面“一键卸载 Impedance Matching AI”会：</p>
<ul>
<li>关闭正在运行的主程序与 MCP 进程；</li>
<li>删除程序文件、快捷方式、注册表项与 MCP 客户端配置；</li>
<li><b>询问是否保留个人数据</b>：选择“是”保留 API Key、界面设置、教材索引、上传/报告、翻译缓存与教材搜索路径，重装后可直接复用；选择“否”彻底删除 <code>%LOCALAPPDATA%\\ImpedanceMatchingAI</code> 下的数据。</li>
<li>保留模式下，程序目录 <code>TextBook</code> 中的文件会先复制到用户数据目录，再删除程序目录；自定义教材搜索目录永远不会被卸载程序删除。</li>
<li>不会删除共享的 Microsoft Edge WebView2 Runtime。</li>
</ul>
<h2>系统要求</h2>
<p>Windows 10/11 x64；Microsoft Edge WebView2 Runtime（安装程序会自动检测/安装）。</p>
"""
    return _render_page("安装与卸载说明", "安装与卸载", content)


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    (DOCS / "manual.css").write_text(CSS, encoding="utf-8")
    _copy_mathjax()
    for category, title, _desc in CATEGORIES:
        for lang in ("zh", "en"):
            doc = docs_hub.get_doc(category, lang)
            _render_page(f"{category}.{lang}", doc["title"], doc["markdown"])
    _library_help()
    _install_help()
    _index()
    print(f"Built static manuals in {DOCS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
