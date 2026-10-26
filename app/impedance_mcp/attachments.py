"""Upload handling and text extraction for the AI chat."""

from __future__ import annotations

import base64
import binascii
import csv
import io
import json
import re
import uuid
import zipfile
from pathlib import Path
from typing import Any, Dict, Tuple

from . import config

MAX_BYTES = 25 * 1024 * 1024
MAX_CHARS = 60000

TEXT_SUFFIXES = {
    ".txt", ".md", ".markdown", ".csv", ".tsv", ".json", ".xml", ".yaml", ".yml",
    ".py", ".m", ".mlx", ".c", ".h", ".cpp", ".hpp", ".java", ".js", ".ts", ".css",
    ".html", ".htm", ".tex", ".log", ".ini", ".cfg", ".toml", ".rst", ".srt",
}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
OFFICE_SUFFIXES = {".pdf", ".docx", ".xlsx", ".xlsm", ".pptx", ".ipynb"}
ALLOWED = TEXT_SUFFIXES | IMAGE_SUFFIXES | OFFICE_SUFFIXES


def _decode_text(raw: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "gb18030", "gbk", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _strip_xml(xml: str) -> str:
    xml = re.sub(r"<w:tab[^>]*/>", "\t", xml)
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<[^>]+>", "", xml)
    xml = (xml.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
              .replace("&quot;", '"').replace("&apos;", "'"))
    xml = re.sub(r"[ \t]+\n", "\n", xml)
    xml = re.sub(r"\n{3,}", "\n\n", xml)
    return xml.strip()


def _pdf_text(path: Path) -> Tuple[str, str]:
    try:
        from pypdf import PdfReader
    except Exception:
        return "", "未安装 pypdf，无法读取 PDF 文本；请安装 pypdf 或改用 txt/md。"
    try:
        reader = PdfReader(str(path))
        pages = []
        for i, page in enumerate(reader.pages):
            if i >= 80:
                break
            pages.append(page.extract_text() or "")
        return "\n\n".join(pages).strip(), ""
    except Exception as exc:  # noqa: BLE001
        return "", f"PDF 解析失败：{exc}"


def _docx_text(path: Path) -> Tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
        return _strip_xml(xml), ""
    except Exception as exc:  # noqa: BLE001
        return "", f"DOCX 解析失败：{exc}"


def _xlsx_text(path: Path) -> Tuple[str, str]:
    try:
        import openpyxl
        wb = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
        chunks = []
        for ws in wb.worksheets[:8]:
            chunks.append(f"### 工作表：{ws.title}")
            for row_i, row in enumerate(ws.iter_rows(values_only=True)):
                if row_i >= 200:
                    break
                cells = [str(c) for c in row[:30] if c is not None]
                if cells:
                    chunks.append(" | ".join(cells))
        wb.close()
        return "\n".join(chunks), ""
    except Exception:
        pass
    try:
        with zipfile.ZipFile(path) as z:
            shared = []
            if "xl/sharedStrings.xml" in z.namelist():
                xml = z.read("xl/sharedStrings.xml").decode("utf-8", errors="ignore")
                shared = re.findall(r"<t[^>]*>(.*?)</t>", xml, re.S)
            rows = []
            for name in z.namelist():
                if not name.startswith("xl/worksheets/sheet"):
                    continue
                xml = z.read(name).decode("utf-8", errors="ignore")
                for row in re.findall(r"<row[^>]*>(.*?)</row>", xml, re.S)[:200]:
                    vals = []
                    for cell in re.findall(r"<c[^>]*?(?:t=\"s\")?[^>]*>(.*?)</c>", row, re.S):
                        v = re.search(r"<v>(.*?)</v>", cell)
                        if v:
                            idx = int(v.group(1))
                            if 0 <= idx < len(shared):
                                vals.append(shared[idx])
                            else:
                                vals.append(v.group(1))
                    if vals:
                        rows.append(" | ".join(vals))
            return "\n".join(rows), ""
    except Exception as exc:  # noqa: BLE001
        return "", f"XLSX 解析失败：{exc}"


def _pptx_text(path: Path) -> Tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as z:
            texts = []
            names = sorted(n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n))
            for name in names[:60]:
                xml = z.read(name).decode("utf-8", errors="ignore")
                parts = re.findall(r"<a:t>(.*?)</a:t>", xml, re.S)
                if parts:
                    texts.append(" ".join(parts))
        return "\n\n".join(texts), ""
    except Exception as exc:  # noqa: BLE001
        return "", f"PPTX 解析失败：{exc}"


def _ipynb_text(path: Path) -> Tuple[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        chunks = []
        for cell in data.get("cells", [])[:200]:
            src = cell.get("source", [])
            if isinstance(src, list):
                src = "".join(src)
            chunks.append(f"[{cell.get('cell_type','code')}] {src}")
        return "\n\n".join(chunks), ""
    except Exception as exc:  # noqa: BLE001
        return "", f"Notebook 解析失败：{exc}"


def extract(path: Path, original_name: str) -> Dict[str, Any]:
    suffix = path.suffix.lower()
    kind = "text"
    note = ""
    text = ""
    if suffix in TEXT_SUFFIXES:
        text = _decode_text(path.read_bytes())
    elif suffix == ".pdf":
        kind = "pdf"
        text, note = _pdf_text(path)
    elif suffix == ".docx":
        kind = "docx"
        text, note = _docx_text(path)
    elif suffix in (".xlsx", ".xlsm"):
        kind = "xlsx"
        text, note = _xlsx_text(path)
    elif suffix == ".pptx":
        kind = "pptx"
        text, note = _pptx_text(path)
    elif suffix == ".ipynb":
        kind = "notebook"
        text, note = _ipynb_text(path)
    elif suffix in IMAGE_SUFFIXES:
        kind = "image"
        note = "图片已保存。当前文本模型不读取图像内容，请用文字描述关键信息。"
        try:
            from PIL import Image
            with Image.open(path) as im:
                note += f"（{im.width}×{im.height}px）"
        except Exception:
            pass
    else:
        note = "不支持的文件类型。"

    truncated = len(text) > MAX_CHARS
    if truncated:
        text = text[:MAX_CHARS] + "\n\n…（内容过长已截断）"
    preview = re.sub(r"\s+", " ", text).strip()[:260]
    return {
        "kind": kind,
        "text": text.strip(),
        "chars": len(text),
        "truncated": truncated,
        "note": note,
        "preview": preview,
    }


def save_upload(filename: str, content_b64: str) -> Dict[str, Any]:
    config.ensure_dirs()
    original = Path(str(filename or "upload")).name
    suffix = Path(original).suffix.lower()
    if suffix not in ALLOWED:
        raise ValueError(f"不支持的文件类型：{suffix or '无扩展名'}")
    try:
        raw = base64.b64decode(content_b64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("文件内容不是有效的 Base64 数据") from exc
    if len(raw) > MAX_BYTES:
        raise ValueError(f"文件过大（{len(raw) / 1024 / 1024:.1f} MB），上限 25 MB")
    if not raw:
        raise ValueError("文件为空")
    safe = re.sub(r"[^\w\u4e00-\u9fff.\-]+", "_", original)[:80]
    stored = f"{uuid.uuid4().hex[:10]}_{safe}"
    path = config.UPLOAD_DIR / stored
    path.write_bytes(raw)
    info = extract(path, original)
    info.update({
        "ok": True,
        "id": path.name,
        "name": original,
        "size": len(raw),
        "path": str(path),
    })
    return info


def load_attachment(attachment_id: str, name: str = "") -> Dict[str, Any]:
    config.ensure_dirs()
    safe = Path(str(attachment_id)).name
    path = config.UPLOAD_DIR / safe
    if not path.exists():
        return {"ok": False, "name": name or safe, "text": "",
                "note": "附件不存在或已被清理。"}
    info = extract(path, name or safe)
    info.update({"ok": True, "id": safe, "name": name or safe,
                 "size": path.stat().st_size})
    return info


def attachment_context(items: list, max_total: int = 48000) -> Tuple[str, list]:
    """Build a text block for the model and a compact UI description."""
    blocks = []
    used = 0
    ui = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        info = item
        if not info.get("text") and info.get("id"):
            info = load_attachment(str(info["id"]), str(info.get("name", "")))
        text = info.get("text") or ""
        name = info.get("name") or "附件"
        note = info.get("note") or ""
        if text and used < max_total:
            remaining = max_total - used
            chunk = text[:remaining]
            blocks.append(f"### 附件：{name}\n{chunk}")
            used += len(chunk)
        elif note:
            blocks.append(f"### 附件：{name}\n（{note}）")
        ui.append({
            "id": info.get("id"),
            "name": name,
            "kind": info.get("kind"),
            "chars": info.get("chars", len(text)),
            "preview": info.get("preview", ""),
            "note": note,
            "truncated": info.get("truncated", False),
        })
    return "\n\n".join(blocks), ui
