"""Build the HTML/PDF documentation set.

Usage:
    python docs/build_docs.py

Requirements:
    pip install markdown
    Google Chrome (or Edge) for PDF printing.
"""

from __future__ import annotations

import base64
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"
TEAM = "卢瑞林、卢柯吉、林芷伊、张昀蕾"
DATE = "2026-10-26"
VERSION = "v4.0.0"

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

CSS = r"""
:root {
  --ink: #172033;
  --muted: #5b6b82;
  --line: #dbe4ef;
  --brand: #0369a1;
  --brand-2: #0891b2;
  --bg: #ffffff;
  --soft: #f5f9fd;
}
@page { size: A4; margin: 17mm 15mm 18mm 15mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  margin: 0; color: var(--ink); background: var(--bg);
  font-family: "Microsoft YaHei", "Segoe UI", "Noto Sans SC", system-ui, sans-serif;
  font-size: 10.5pt; line-height: 1.75;
}
a { color: var(--brand); text-decoration: none; }
.cover {
  min-height: 297mm; display: flex; flex-direction: column; justify-content: center;
  padding: 42mm 22mm 26mm; margin: -17mm -15mm 0 -15mm;
  background: linear-gradient(135deg, #061a2e 0%, #083b5c 55%, #075985 100%);
  color: #eaf8ff; position: relative; overflow: hidden;
  page-break-after: always;
}
.cover::after {
  content: ""; position: absolute; right: -60mm; top: -40mm; width: 160mm; height: 160mm;
  border-radius: 50%; border: 1px solid rgba(34,211,238,.25);
  box-shadow: 0 0 0 18mm rgba(34,211,238,.05), 0 0 0 36mm rgba(34,211,238,.03);
}
.cover .badge {
  display: inline-block; width: fit-content; padding: 4px 12px; border-radius: 99px;
  border: 1px solid rgba(34,211,238,.4); color: #a5f3fc; font-size: 9pt; letter-spacing: .5px;
}
.cover h1 { font-size: 34pt; line-height: 1.25; margin: 18mm 0 6mm; letter-spacing: 1px; }
.cover h2 { font-size: 15pt; font-weight: 400; color: #bae6fd; margin: 0 0 24mm; }
.cover .meta { font-size: 10pt; line-height: 2; color: #cbe9f7; }
.cover .meta b { color: #fff; font-weight: 600; }
.cover .rule { width: 34mm; height: 3px; background: #22d3ee; margin: 8mm 0; }
.cover .foot { position: absolute; bottom: 20mm; left: 22mm; right: 22mm; font-size: 8.5pt; color: #9fc9df; border-top: 1px solid rgba(255,255,255,.15); padding-top: 4mm; }
.toc { page-break-after: always; padding-top: 4mm; }
.toc h2 { font-size: 18pt; color: var(--ink); border: 0; margin: 0 0 8mm; padding: 0; }
.toc ul { list-style: none; padding-left: 0; margin: 0; }
.toc ul ul { padding-left: 7mm; }
.toc li { margin: 0.35mm 0; font-size: 8.6pt; line-height: 1.28; }
.toc > ul > li { margin-top: 0.8mm; }
.toc a { color: #334155; }
.toc > ul > li > a { color: var(--brand); font-weight: 600; }
.content h1 {
  font-size: 21pt; color: #0b2a44; margin: 0 0 7mm; padding-bottom: 3mm;
  border-bottom: 2px solid #dbeafe; page-break-before: always;
}
.content h1:first-child { page-break-before: avoid; }
.content h2 {
  font-size: 14.5pt; color: #0b3a5a; margin: 8mm 0 3mm; padding-left: 3mm;
  border-left: 4px solid var(--brand-2); page-break-after: avoid;
}
.content h3 { font-size: 12pt; color: #0f4c6e; margin: 5.5mm 0 2mm; page-break-after: avoid; }
.content h4 { font-size: 10.8pt; color: #155e75; margin: 4mm 0 1.5mm; }
.content p { margin: 2mm 0; }
.content img {
  display: block; max-width: 100%; height: auto; margin: 3mm auto 4mm;
  border: 1px solid var(--line); border-radius: 3mm;
  page-break-inside: avoid;
}
.content table {
  width: 100%; border-collapse: collapse; margin: 3mm 0 4mm; font-size: 9pt;
  page-break-inside: avoid;
}
.content th, .content td { border: 1px solid var(--line); padding: 1.8mm 2.2mm; vertical-align: top; }
.content th { background: #eef6fc; color: #0b3a5a; text-align: left; font-weight: 600; }
.content tr:nth-child(even) td { background: #fbfdff; }
.content code {
  font-family: "Cascadia Code", Consolas, monospace; font-size: 9pt;
  background: #eef6fc; color: #0e7490; padding: .3mm 1.2mm; border-radius: 1mm;
}
.content pre {
  background: #07111f; color: #dbeafe; border-radius: 2.5mm; padding: 3.2mm 4mm;
  font-size: 8.4pt; line-height: 1.55; overflow-x: auto; white-space: pre-wrap;
  word-break: break-word; page-break-inside: avoid; margin: 3mm 0 4mm;
}
.content pre code { background: none; color: inherit; padding: 0; font-size: inherit; }
.content blockquote {
  margin: 3mm 0; padding: 2.5mm 4mm; border-left: 3px solid var(--brand-2);
  background: #f0f9ff; color: #334155; page-break-inside: avoid;
}
.content ul, .content ol { margin: 2mm 0 2mm 5mm; padding-left: 4mm; }
.content li { margin: .8mm 0; }
.content hr { border: 0; border-top: 1px solid var(--line); margin: 6mm 0; }
.content strong { color: #0b2a44; }
.content .doc-end {
  margin-top: 10mm; padding-top: 3mm; border-top: 1px solid var(--line);
  color: var(--muted); font-size: 8.5pt; text-align: center;
}
@media screen {
  body { background: #eef3f9; }
  .cover, .toc, .content { max-width: 190mm; margin: 0 auto; }
  .cover { margin-top: 0; }
  .content { background: #fff; padding: 12mm 15mm; box-shadow: 0 8px 30px rgba(15,23,42,.08); margin-bottom: 20mm; }
  .toc { background: #fff; padding: 12mm 15mm; box-shadow: 0 8px 30px rgba(15,23,42,.08); margin-bottom: 8mm; }
}
"""


def embed_images(html: str) -> str:
    def repl(match: re.Match) -> str:
        src = match.group(1)
        if src.startswith("assets/"):
            path = DOCS / src
            if path.exists():
                data = base64.b64encode(path.read_bytes()).decode("ascii")
                return f'src="data:image/png;base64,{data}"'
        return match.group(0)
    return re.sub(r'src="([^"]+)"', repl, html)


def render(md_path: Path, title: str, subtitle: str) -> tuple[str, str]:
    text = md_path.read_text(encoding="utf-8")
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                           extension_configs={"toc": {"toc_depth": "1-3"}})
    body = md.convert(text)
    body = embed_images(body)
    toc = md.toc
    cover = f"""
    <section class="cover">
      <span class="badge">上海交通大学集成电路学院 · AI 教与学活动周</span>
      <h1>{title}</h1>
      <h2>{subtitle}</h2>
      <div class="rule"></div>
      <div class="meta">
        <div><b>版本</b>　{VERSION}　｜　<b>更新日期</b>　{DATE}</div>
        <div><b>开发者</b>　{TEAM}</div>
        <div><b>项目</b>　智配芯生 · ImpedanceMCP 微波阻抗匹配智能计算与仿真软件</div>
      </div>
      <div class="foot">本文件由 docs/build_docs.py 自动生成 · 可直接打印为 A4 PDF</div>
    </section>
    """
    html = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{title} · 智配芯生 ImpedanceMCP</title>
<style>{CSS}</style></head>
<body>
{cover}
<section class="toc"><h2>目录</h2>{toc}</section>
<main class="content">
{body}
<div class="doc-end">智配芯生 · ImpedanceMCP {VERSION} ｜ {DATE} ｜ 开发者：{TEAM}<br>
上海交通大学集成电路学院（信息与电子工程学院）</div>
</main>
</body></html>"""
    return html, toc


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    return None


def print_pdf(chrome: str, html_path: Path, pdf_path: Path) -> bool:
    with tempfile.TemporaryDirectory(prefix="imp_docs_chrome_") as tmp:
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            "--no-pdf-header-footer",
            "--allow-file-access-from-files",
            "--virtual-time-budget=2500",
            f"--user-data-dir={tmp}",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90,
                                  encoding="utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            print(f"[PDF] failed: {exc}")
            return False
        if not pdf_path.exists() or pdf_path.stat().st_size < 10_000:
            print(f"[PDF] failed: {(proc.stderr or proc.stdout)[-400:]}")
            return False
        print(f"[PDF] {pdf_path.name}  {pdf_path.stat().st_size / 1024:.0f} KB")
        return True


def build_index(docs: list[dict]) -> None:
    cards = "".join(
        f'<a class="card" href="{d["slug"]}.html"><span class="kicker">{d["kicker"]}</span>'
        f'<h3>{d["title"]}</h3><p>{d["desc"]}</p><span class="more">打开文档 →</span></a>'
        for d in docs
    )
    html = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>智配芯生 · ImpedanceMCP 文档中心</title>
<style>
body{{margin:0;background:#07111f;color:#e6eefc;font-family:"Microsoft YaHei","Segoe UI",system-ui,sans-serif}}
.wrap{{max-width:1040px;margin:0 auto;padding:48px 24px 60px}}
.hero{{display:flex;gap:18px;align-items:center;margin-bottom:10px}}
.mark{{width:64px;height:64px;border-radius:18px;display:grid;place-items:center;background:linear-gradient(135deg,#22d3ee,#2dd4bf);color:#03151c;font-size:28px;font-weight:700}}
h1{{margin:0;font-size:28px}} .sub{{margin:6px 0 0;color:#8ba0bd;font-size:13px}}
.badge{{display:inline-block;margin-top:14px;padding:4px 10px;border:1px solid rgba(34,211,238,.3);border-radius:99px;color:#67e8f9;font-size:11px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:28px}}
.card{{display:block;padding:18px 18px 16px;border:1px solid rgba(148,163,184,.16);border-radius:16px;background:linear-gradient(160deg,rgba(17,30,51,.9),rgba(10,19,33,.88));color:inherit;text-decoration:none;transition:.18s}}
.card:hover{{border-color:rgba(34,211,238,.4);transform:translateY(-2px)}}
.kicker{{font-size:10px;letter-spacing:1.4px;color:#22d3ee;text-transform:uppercase}}
.card h3{{margin:8px 0 6px;font-size:17px}} .card p{{margin:0;color:#8ba0bd;font-size:12px;line-height:1.7}}
.more{{display:inline-block;margin-top:12px;color:#67e8f9;font-size:11px}}
.shot{{margin-top:26px;border:1px solid rgba(148,163,184,.16);border-radius:16px;overflow:hidden}}
.shot img{{display:block;width:100%}}
.foot{{margin-top:24px;color:#647892;font-size:11px;line-height:1.8}}
@media(max-width:760px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><div class="wrap">
<div class="hero"><div class="mark">⌁</div><div><h1>智配芯生 · ImpedanceMCP</h1>
<p class="sub">微波阻抗匹配智能计算与仿真软件 · {VERSION} · {DATE}</p></div></div>
<span class="badge">MCP · DeepSeek · MATLAB R2025b · Python 内核</span>
<div class="grid">{cards}
<a class="card" href="../README.md"><span class="kicker">Project</span><h3>README</h3><p>安装、启动、MCP 配置、工具清单与团队信息。</p><span class="more">查看仓库说明 →</span></a>
</div>
<div class="shot"><img src="assets/screenshot_design.png" alt="软件界面"></div>
<div class="foot">开发者：{TEAM}<br>上海交通大学集成电路学院（信息与电子工程学院）· “智绘芯生，AI 赋能” AI 教与学活动周</div>
</div></body></html>"""
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    print("[HTML] index.html")


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    specs = [
        {"slug": "用户手册", "md": "用户手册.md", "title": "用户手册",
         "subtitle": "安装、启动、界面、设计、分析、MCP 与常见问题",
         "kicker": "User Guide", "desc": "从安装到 AI 对话、五种拓扑、圆图、耐压与报告。"},
        {"slug": "技术白皮书", "md": "技术白皮书.md", "title": "技术白皮书",
         "subtitle": "架构、计算模型、节点法、MCP 协议与验证",
         "kicker": "White Paper", "desc": "五种拓扑公式、节点法推导、正确性验证与安全设计。"},
        {"slug": "比赛说明文档", "md": "比赛说明文档.md", "title": "比赛说明文档",
         "subtitle": "赛道一 · AI 智能体 · 创作背景、创新点、操作指南与团队",
         "kicker": "Competition", "desc": "5 分钟演示路线、创新点、技术实现与团队分工。"},
        {"slug": "软件架构说明", "md": "软件架构说明.md", "title": "软件架构说明",
         "subtitle": "V4.0 目录结构、模块职责、数据流与测试",
         "kicker": "Architecture", "desc": "从 V3 App Designer 到 V4 MCP 外壳的完整结构。"},
    ]
    built = []
    chrome = find_chrome()
    for spec in specs:
        md_path = DOCS / spec["md"]
        if not md_path.exists():
            print(f"[SKIP] {md_path}")
            continue
        html, _toc = render(md_path, spec["title"], spec["subtitle"])
        html_path = DOCS / f"{spec['slug']}.html"
        html_path.write_text(html, encoding="utf-8")
        print(f"[HTML] {html_path.name}  {len(html) / 1024:.0f} KB")
        built.append(spec)
        if chrome:
            print_pdf(chrome, html_path, DOCS / f"{spec['slug']}.pdf")
    build_index(built)

    # Copy updated docs into the original release/document locations.
    copies = [
        ("用户手册.pdf", ROOT / "APP_Release_Release_Version" / "ReadMe" / "Readme_Next_Software_Instroduction.pdf"),
        ("比赛说明文档.pdf", ROOT / "APP_Release_Release_Version" / "Reference" / "My_APP_Introduction.pdf"),
        ("软件架构说明.html", ROOT / "APP_Release_Release_Version" / "Backup" / "Software_Structure_V4_0.html"),
        ("用户手册.html", ROOT / "APP_Release_Release_Version" / "ReadMe" / "Readme_Next_Software_Instroduction.html"),
        ("比赛说明文档.html", ROOT / "APP_Release_Release_Version" / "Reference" / "My_APP_Introduction.html"),
    ]
    for src_name, dst in copies:
        src = DOCS / src_name
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"[COPY] {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
