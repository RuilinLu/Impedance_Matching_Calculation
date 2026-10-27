"""Textbook library: indexing, full-text search, OCR, page rendering and translation.

The library is independent from the AI provider: every PDF dropped into
``TextBook/`` (or ``data/library/books``) is indexed into a local SQLite
database.  Text-layer PDFs are searchable immediately; scanned books are
flagged and can be OCR'ed page by page (RapidOCR) or read visually by a
vision-capable model.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import os
import re
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import config

try:  # PyMuPDF >= 1.24 prefers the ``pymupdf`` import name.
    import pymupdf as fitz
except Exception:  # pragma: no cover - older installations
    try:
        import fitz  # type: ignore
    except Exception:  # pragma: no cover
        fitz = None  # type: ignore

OFFICE_SUFFIXES = {".docx", ".pptx", ".xlsx", ".xlsm", ".ipynb", ".doc", ".ppt", ".xls"}
SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md", ".markdown", ".tex", ".rst", ".csv"} | OFFICE_SUFFIXES
MAX_OCR_PIXELS = 9_000_000
DEFAULT_DPI = 150
MAX_DPI = 300

_LOCK = threading.RLock()
_INDEX_STATE: Dict[str, Any] = {
    "running": False,
    "phase": "idle",
    "total": 0,
    "done": 0,
    "current": "",
    "started_at": None,
    "finished_at": None,
    "error": "",
    "ocr_pages": 0,
}
_OCR_ENGINE = None
_OCR_LOCK = threading.Lock()


# ---------------------------------------------------------------------------
# Paths and database
# ---------------------------------------------------------------------------

def db_path() -> Path:
    return config.LIBRARY_DIR / "index.sqlite3"


def cache_dir() -> Path:
    return config.LIBRARY_DIR / "cache"


_DB_READY = {"path": "", "ok": False}


def _connect() -> sqlite3.Connection:
    config.ensure_dirs()
    config.LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    cache_dir().mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path()), timeout=30)
    conn.row_factory = sqlite3.Row
    # Do not switch journal_mode on every connection: while another thread or
    # process is writing, that PRAGMA can fail immediately with "database is
    # locked" even though the normal busy handler would wait.  WAL is enabled
    # once in init_db(); reads and writes then use a 30 s busy timeout.
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


@contextmanager
def _db():
    """Commit and close a connection, which keeps Windows temp files removable."""
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        try:
            conn.close()
        except Exception:
            pass


def init_db(force: bool = False) -> None:
    path = db_path()
    key = str(path)
    with _LOCK:
        if (not force and _DB_READY["ok"] and _DB_READY["path"] == key
                and path.exists()):
            return
        with _db() as conn:
            try:
                conn.execute("PRAGMA journal_mode=WAL")
            except sqlite3.OperationalError:
                # Another process may hold the database; normal busy timeouts
                # still apply and a later init can switch to WAL.
                pass
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS docs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    lang TEXT DEFAULT 'en',
                    pages INTEGER DEFAULT 0,
                    mtime REAL DEFAULT 0,
                    size INTEGER DEFAULT 0,
                    indexed_at TEXT DEFAULT '',
                    ocr_pages INTEGER DEFAULT 0,
                    needs_ocr INTEGER DEFAULT 0,
                    error TEXT DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS pages (
                    doc_id INTEGER NOT NULL,
                    page INTEGER NOT NULL,
                    text TEXT DEFAULT '',
                    source TEXT DEFAULT 'text',
                    boxes TEXT DEFAULT '',
                    PRIMARY KEY (doc_id, page)
                );
                CREATE TABLE IF NOT EXISTS translations (
                    doc_id INTEGER NOT NULL,
                    page INTEGER NOT NULL,
                    lang TEXT NOT NULL,
                    text TEXT NOT NULL,
                    model TEXT DEFAULT '',
                    created_at TEXT DEFAULT '',
                    PRIMARY KEY (doc_id, page, lang)
                );
                CREATE TABLE IF NOT EXISTS meta (
                    k TEXT PRIMARY KEY,
                    v TEXT NOT NULL
                );
                """
            )
            try:
                conn.execute(
                    "CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts "
                    "USING fts5(doc_id UNINDEXED, page UNINDEXED, text, tokenize='trigram')"
                )
                conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('fts','trigram')")
            except sqlite3.OperationalError:
                conn.execute(
                    "CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts "
                    "USING fts5(doc_id UNINDEXED, page UNINDEXED, text)"
                )
                conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('fts','unicode61')")
            conn.commit()
            if _meta(conn, "ocr_box_version") != "2":
                _repair_ocr_boxes(conn)
                _set_meta(conn, "ocr_box_version", "2")
                conn.commit()
        _DB_READY["path"] = key
        _DB_READY["ok"] = True


def _repair_ocr_boxes(conn: sqlite3.Connection) -> None:
    """Drop OCR pages whose boxes were normalized against PDF points.

    An earlier release candidate rendered at 220 dpi but divided by the point size, collapsing
    most horizontal coordinates to 1.0.  Those cached boxes cannot be
    repaired without the page image, so remove them and let OCR run again.
    """
    rows = conn.execute(
        "SELECT doc_id, page, boxes FROM pages WHERE source='ocr' AND boxes != ''"
    ).fetchall()
    stale = []
    for row in rows:
        try:
            boxes = json.loads(row["boxes"])
        except Exception:
            continue
        total = degenerate = 0
        for line in boxes if isinstance(boxes, list) else []:
            box = line.get("box") if isinstance(line, dict) else None
            xs = []
            for point in box or []:
                try:
                    xs.append(float(point[0]))
                except (TypeError, ValueError, IndexError):
                    continue
            if not xs:
                continue
            total += 1
            if max(xs) - min(xs) < 0.002:
                degenerate += 1
        if total and degenerate / total > 0.5:
            stale.append((int(row["doc_id"]), int(row["page"])))
    for doc_id, page in stale:
        conn.execute("DELETE FROM pages WHERE doc_id=? AND page=?", (doc_id, page))
        conn.execute("DELETE FROM pages_fts WHERE doc_id=? AND page=?", (doc_id, page))
    for doc_id in {item[0] for item in stale}:
        conn.execute(
            "UPDATE docs SET ocr_pages=(SELECT COUNT(*) FROM pages "
            "WHERE pages.doc_id=docs.id AND source='ocr'), "
            "needs_ocr=MAX(pages - (SELECT COUNT(*) FROM pages "
            "WHERE pages.doc_id=docs.id AND text != ''), 0) WHERE id=?",
            (doc_id,),
        )


def _meta(conn: sqlite3.Connection, key: str) -> str:
    row = conn.execute("SELECT v FROM meta WHERE k=?", (key,)).fetchone()
    return row["v"] if row else ""


def _set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES(?,?)", (key, value))


# ---------------------------------------------------------------------------
# Source discovery and indexing
# ---------------------------------------------------------------------------

def source_dirs() -> List[Path]:
    """Ordered textbook folders, resolved from the live configuration.

    Built-in entries (install-dir TextBook, data-root TextBook, app-managed
    books) are resolved dynamically so moving the installation cannot leave a
    stale absolute path behind.  User-added folders keep their priority order.
    """
    dirs = list(config.library_source_paths())
    # Honour the legacy in-process override used by older integrations/tests,
    # but never re-add a built-in folder that the user disabled in the UI.
    builtin_keys = set()
    for _kind, _label, resolver in config.BUILTIN_SOURCES:
        try:
            builtin_keys.add(os.path.normcase(str(resolver().resolve())))
        except Exception:
            continue
    configured = {os.path.normcase(str(Path(item).resolve())) for item in dirs}
    for legacy in getattr(config, "LIBRARY_SOURCE_DIRS", []):
        try:
            key = os.path.normcase(str(Path(legacy).resolve()))
        except Exception:
            continue
        if key in builtin_keys or key in configured:
            continue
        dirs.append(Path(legacy))
        configured.add(key)
    dirs.append(config.LIBRARY_DIR / "books")
    out: List[Path] = []
    seen = set()
    for item in dirs:
        try:
            path = Path(item)
        except Exception:
            continue
        key = os.path.normcase(str(path.resolve())) if path.exists() else os.path.normcase(str(path))
        if key in seen:
            continue
        seen.add(key)
        if path.exists() and path.is_dir():
            out.append(path)
    return out


def _iter_sources() -> Iterable[Path]:
    for root in source_dirs():
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.name.startswith(".") or path.name.startswith("~$"):
                continue
            if path.suffix.lower() in SUPPORTED_SUFFIXES:
                yield path


def _clean_title(path: Path) -> str:
    title = path.stem
    title = re.sub(r"\s*\(z-library[^)]*\)", "", title, flags=re.I)
    title = re.sub(r"\s*\(1lib[^)]*\)", "", title, flags=re.I)
    title = re.sub(r"\s*\(z-lib[^)]*\)", "", title, flags=re.I)
    title = re.sub(r"[_]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()[:180] or path.name


def _detect_lang(text: str) -> str:
    sample = (text or "")[:4000]
    if not sample:
        return "unknown"
    cjk = len(re.findall(r"[\u4e00-\u9fff]", sample))
    latin = len(re.findall(r"[A-Za-z]", sample))
    if cjk >= 20 and cjk >= latin * 0.08:
        return "zh"
    if latin >= 20:
        return "en"
    return "unknown"


def _normalize_text(text: str) -> str:
    text = (text or "").replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _open_document(path: Path):
    if path.suffix.lower() == ".pdf":
        if fitz is None:
            raise RuntimeError("未安装 PyMuPDF，无法读取 PDF")
        return fitz.open(str(path))
    return None


def _read_text_document(path: Path) -> List[str]:
    raw = path.read_bytes()
    text = ""
    for enc in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    text = _normalize_text(text)
    size = 3500
    return [text[i:i + size] for i in range(0, max(1, len(text)), size)]


def _fts_delete(conn: sqlite3.Connection, doc_id: int) -> None:
    conn.execute("DELETE FROM pages_fts WHERE doc_id=?", (doc_id,))


def _fts_upsert(conn: sqlite3.Connection, doc_id: int, page: int, text: str) -> None:
    conn.execute("DELETE FROM pages_fts WHERE doc_id=? AND page=?", (doc_id, page))
    if text and text.strip():
        conn.execute(
            "INSERT INTO pages_fts(doc_id, page, text) VALUES(?,?,?)",
            (doc_id, page, text),
        )


def _index_document(conn: sqlite3.Connection, path: Path, ocr_first_pages: int = 2) -> int:
    stat = path.stat()
    existing = conn.execute("SELECT * FROM docs WHERE path=?", (str(path),)).fetchone()
    if existing and abs(existing["mtime"] - stat.st_mtime) < 1 and existing["size"] == stat.st_size:
        return int(existing["id"])

    title = _clean_title(path)
    page_count = 0
    needs_ocr = 0
    lang = "unknown"
    pages: List[Tuple[int, str, str, str]] = []

    if path.suffix.lower() == ".pdf":
        doc = _open_document(path)
        if doc is None:
            raise RuntimeError("无法打开 PDF")
        try:
            page_count = len(doc)
            meta = doc.metadata or {}
            meta_title = str(meta.get("title") or "").strip()
            if (meta_title and len(meta_title) > 3
                    and not re.search(r"\.(dvi|tex|indd|qxd|pdf)$", meta_title, re.I)
                    and meta_title.lower() not in ("untitled", "title", "document")):
                title = meta_title[:180]
            for index in range(page_count):
                page = doc[index]
                text = _normalize_text(page.get_text("text") or "")
                source = "text"
                if len(text) < 40:
                    needs_ocr += 1
                    source = "none"
                    text = ""
                pages.append((index + 1, text, source, ""))
                if index == 0 and text:
                    lang = _detect_lang(text)
            if lang == "unknown":
                for _no, text, _src, _box in pages[:8]:
                    if text:
                        lang = _detect_lang(text)
                        break
        finally:
            doc.close()
    else:
        suffix = path.suffix.lower()
        if suffix in OFFICE_SUFFIXES:
            from . import attachments
            info = attachments.extract(path, path.name)
            full_text = _normalize_text(info.get("text") or "")
        else:
            full_text = "\n\n".join(_read_text_document(path))
        size = 3500
        texts = [full_text[i:i + size] for i in range(0, max(1, len(full_text)), size)] or [""]
        page_count = len(texts)
        pages = [(i + 1, _normalize_text(t), "text", "") for i, t in enumerate(texts)]
        lang = _detect_lang(full_text[:6000])
        title = _clean_title(path)

    now = datetime.now().isoformat(timespec="seconds")
    with _LOCK:
        if existing:
            doc_id = int(existing["id"])
            conn.execute("DELETE FROM pages WHERE doc_id=?", (doc_id,))
            _fts_delete(conn, doc_id)
            conn.execute(
                "UPDATE docs SET title=?,lang=?,pages=?,mtime=?,size=?,indexed_at=?,"
                "ocr_pages=?,needs_ocr=?,error='' WHERE id=?",
                (title, lang, page_count, stat.st_mtime, stat.st_size, now,
                 0, needs_ocr, doc_id),
            )
        else:
            cur = conn.execute(
                "INSERT INTO docs(path,title,lang,pages,mtime,size,indexed_at,ocr_pages,needs_ocr)"
                " VALUES(?,?,?,?,?,?,?,0,?)",
                (str(path), title, lang, page_count, stat.st_mtime, stat.st_size, now, needs_ocr),
            )
            doc_id = int(cur.lastrowid)
        conn.executemany(
            "INSERT OR REPLACE INTO pages(doc_id,page,text,source,boxes) VALUES(?,?,?,?,?)",
            [(doc_id, p, t, s, b) for p, t, s, b in pages],
        )
        for page_no, text, _source, _boxes in pages:
            if text:
                _fts_upsert(conn, doc_id, page_no, text)
        conn.commit()

    if needs_ocr and ocr_first_pages > 0:
        candidates = [p for p, t, _s, _b in pages if not t][:ocr_first_pages]
        for page_no in candidates:
            try:
                ocr_page(doc_id, page_no, force=False)
            except Exception:
                break
    return doc_id


def sync_index(force: bool = False, ocr_first_pages: int = 2,
               limit: Optional[int] = None) -> Dict[str, Any]:
    """Synchronise ``docs``/``pages`` with the files on disk."""
    init_db()
    with _LOCK:
        _INDEX_STATE.update({
            "running": True, "phase": "scanning", "done": 0, "total": 0,
            "current": "", "started_at": datetime.now().isoformat(timespec="seconds"),
            "finished_at": None, "error": "", "ocr_pages": 0,
        })
    try:
        sources = list(_iter_sources())
        if limit:
            sources = sources[:limit]
        with _LOCK:
            _INDEX_STATE["total"] = len(sources)
        with _db() as conn:
            known = {row["path"]: row for row in conn.execute("SELECT * FROM docs")}
            live = {str(p) for p in sources}
            for path in sources:
                if force and str(path) in known:
                    old_id = int(known[str(path)]["id"])
                    conn.execute("DELETE FROM docs WHERE id=?", (old_id,))
                    _fts_delete(conn, old_id)
                    conn.execute("DELETE FROM pages WHERE doc_id=?", (old_id,))
                    conn.commit()
                with _LOCK:
                    _INDEX_STATE.update({"phase": "indexing", "current": path.name})
                try:
                    _index_document(conn, path, ocr_first_pages=ocr_first_pages)
                except Exception as exc:  # noqa: BLE001
                    with _LOCK:
                        _INDEX_STATE["error"] = f"{path.name}: {exc}"
                    if str(path) in known:
                        conn.execute(
                            "UPDATE docs SET error=? WHERE id=?",
                            (str(exc)[:500], known[str(path)]["id"]),
                        )
                        conn.commit()
                with _LOCK:
                    _INDEX_STATE["done"] += 1
            for path_str, row in known.items():
                if path_str not in live:
                    old_id = int(row["id"])
                    conn.execute("DELETE FROM docs WHERE id=?", (old_id,))
                    conn.execute("DELETE FROM pages WHERE doc_id=?", (old_id,))
                    conn.execute("DELETE FROM translations WHERE doc_id=?", (old_id,))
                    _fts_delete(conn, old_id)
            conn.commit()
        with _LOCK:
            _INDEX_STATE.update({
                "phase": "ready", "running": False, "current": "",
                "finished_at": datetime.now().isoformat(timespec="seconds"),
            })
    except Exception as exc:  # noqa: BLE001
        with _LOCK:
            _INDEX_STATE.update({
                "phase": "error", "running": False, "error": str(exc),
                "finished_at": datetime.now().isoformat(timespec="seconds"),
            })
        raise
    return status()


def start_index(force: bool = False, ocr_first_pages: int = 2) -> Dict[str, Any]:
    init_db()
    with _LOCK:
        if _INDEX_STATE.get("running"):
            return status()
    thread = threading.Thread(
        target=sync_index,
        kwargs={"force": force, "ocr_first_pages": ocr_first_pages},
        name="library-index",
        daemon=True,
    )
    thread.start()
    return status()


def status() -> Dict[str, Any]:
    init_db()
    with _LOCK:
        state = dict(_INDEX_STATE)
    with _db() as conn:
        docs = conn.execute("SELECT COUNT(*) c FROM docs").fetchone()["c"]
        pages = conn.execute("SELECT COUNT(*) c FROM pages WHERE text != ''").fetchone()["c"]
        total_pages = conn.execute("SELECT COALESCE(SUM(pages),0) c FROM docs").fetchone()["c"]
        needs_ocr = conn.execute("SELECT COALESCE(SUM(needs_ocr),0) c FROM docs").fetchone()["c"]
        ocr_pages = conn.execute(
            "SELECT COUNT(*) c FROM pages WHERE source='ocr'"
        ).fetchone()["c"]
        translations = conn.execute("SELECT COUNT(*) c FROM translations").fetchone()["c"]
        fts = _meta(conn, "fts")
    state.update({
        "ok": True,
        "docs": int(docs),
        "indexed_pages": int(pages),
        "total_pages": int(total_pages),
        "needs_ocr": int(needs_ocr),
        "ocr_pages": int(ocr_pages),
        "translations": int(translations),
        "fts": fts,
        "source_dirs": [str(p) for p in source_dirs()],
        "library_sources": config.resolve_library_sources(),
        "current_dir": next((str(p) for p in source_dirs()), ""),
        "install_dir": str(config.INSTALL_DIR),
        "data_dir": str(config.PROJECT_ROOT),
    })
    return state


# ---------------------------------------------------------------------------
# OCR
# ---------------------------------------------------------------------------

def _ocr_engine():
    global _OCR_ENGINE
    with _OCR_LOCK:
        if _OCR_ENGINE is None:
            from rapidocr_onnxruntime import RapidOCR  # type: ignore
            _OCR_ENGINE = RapidOCR()
    return _OCR_ENGINE


def _page_numpy(doc, page_no: int, dpi: int = 220):
    import numpy as np
    page = doc[page_no - 1]
    scale = min(dpi / 72.0,
                math.sqrt(MAX_OCR_PIXELS / max(1.0, page.rect.width * page.rect.height)))
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n > 3:
        arr = arr[:, :, :3]
    return arr


def _normalize_box(box: Any, width: float, height: float) -> List[List[float]]:
    pts = []
    for point in box or []:
        try:
            x, y = float(point[0]), float(point[1])
        except (TypeError, ValueError, IndexError):
            continue
        pts.append([max(0.0, min(1.0, x / width)), max(0.0, min(1.0, y / height))])
    return pts


def ocr_page(doc_id: int, page_no: int, force: bool = False) -> Dict[str, Any]:
    config.ensure_dirs()
    init_db()
    with _db() as conn:
        doc = conn.execute("SELECT * FROM docs WHERE id=?", (doc_id,)).fetchone()
        if not doc:
            return {"ok": False, "message": "文档不存在"}
        if not force:
            row = conn.execute(
                "SELECT * FROM pages WHERE doc_id=? AND page=?", (doc_id, page_no)
            ).fetchone()
            if row and row["source"] == "ocr" and row["text"]:
                return {"ok": True, "text": row["text"], "cached": True,
                        "boxes": json.loads(row["boxes"] or "[]")}
    path = Path(doc["path"])
    if path.suffix.lower() != ".pdf":
        return {"ok": False, "message": "只有 PDF 页面需要 OCR"}
    if fitz is None:
        return {"ok": False, "message": "未安装 PyMuPDF"}
    try:
        engine = _ocr_engine()
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "message": f"本地 OCR 引擎不可用：{exc}",
            "hint": "安装 rapidocr_onnxruntime 后即可离线 OCR；也可以使用支持视觉的模型读图。",
        }
    pdf = fitz.open(str(path))
    try:
        if page_no < 1 or page_no > len(pdf):
            return {"ok": False, "message": "页码超出范围"}
        page = pdf[page_no - 1]
        arr = _page_numpy(pdf, page_no)
        result, _elapse = engine(arr)
        lines: List[Dict[str, Any]] = []
        texts: List[str] = []
        # OCR boxes come back in rendered-pixel coordinates.  Normalize by the
        # pixmap size, not by the PDF point size (220 dpi is ~3x larger).
        height = float(arr.shape[0]) or 1.0
        width = float(arr.shape[1]) or 1.0
        for item in result or []:
            try:
                box, text, score = item[0], str(item[1]), float(item[2])
            except (TypeError, ValueError, IndexError):
                continue
            text = text.strip()
            if not text:
                continue
            texts.append(text)
            lines.append({
                "text": text,
                "score": round(score, 3),
                "box": _normalize_box(box, width, height),
            })
        text = _normalize_text("\n".join(texts))
    finally:
        pdf.close()
    with _db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO pages(doc_id,page,text,source,boxes) VALUES(?,?,?,?,?)",
            (doc_id, page_no, text, "ocr", json.dumps(lines, ensure_ascii=False)),
        )
        _fts_upsert(conn, doc_id, page_no, text)
        conn.execute(
            "UPDATE docs SET ocr_pages=(SELECT COUNT(*) FROM pages WHERE doc_id=? AND source='ocr') WHERE id=?",
            (doc_id, doc_id),
        )
        conn.commit()
    with _LOCK:
        _INDEX_STATE["ocr_pages"] = int(_INDEX_STATE.get("ocr_pages", 0)) + 1
    return {"ok": True, "text": text, "lines": lines, "cached": False,
            "language": _detect_lang(text)}


def ocr_document(doc_id: int, start: int = 1, end: Optional[int] = None,
                 max_pages: int = 40) -> Dict[str, Any]:
    """OCR a page range in the background and return progress immediately."""
    init_db()
    with _db() as conn:
        doc = conn.execute("SELECT * FROM docs WHERE id=?", (doc_id,)).fetchone()
        if not doc:
            return {"ok": False, "message": "文档不存在"}
        total = int(doc["pages"])
    start = max(1, int(start))
    end = min(int(end or total), total)
    if end < start:
        return {"ok": False, "message": "页码范围无效"}
    pages = list(range(start, min(end, start + max_pages - 1) + 1))

    def worker() -> None:
        for page_no in pages:
            try:
                ocr_page(doc_id, page_no)
            except Exception:
                continue

    threading.Thread(target=worker, name=f"ocr-{doc_id}", daemon=True).start()
    return {"ok": True, "queued": len(pages), "start": start, "end": pages[-1],
            "message": f"已开始 OCR：第 {start}–{pages[-1]} 页（后台运行）。"}


# ---------------------------------------------------------------------------
# Document metadata
# ---------------------------------------------------------------------------

def doc_list() -> List[Dict[str, Any]]:
    init_db()
    with _db() as conn:
        rows = conn.execute(
            "SELECT id,path,title,lang,pages,size,indexed_at,ocr_pages,needs_ocr,error"
            " FROM docs ORDER BY title COLLATE NOCASE"
        ).fetchall()
    out = []
    for row in rows:
        out.append({
            "id": int(row["id"]),
            "title": row["title"],
            "filename": Path(row["path"]).name,
            "lang": row["lang"],
            "pages": int(row["pages"]),
            "size": int(row["size"]),
            "indexed_at": row["indexed_at"],
            "ocr_pages": int(row["ocr_pages"] or 0),
            "needs_ocr": int(row["needs_ocr"] or 0),
            "error": row["error"] or "",
        })
    return out


def doc_info(doc_id: int) -> Dict[str, Any]:
    init_db()
    with _db() as conn:
        row = conn.execute("SELECT * FROM docs WHERE id=?", (doc_id,)).fetchone()
        if not row:
            return {"ok": False, "message": "文档不存在"}
        toc: List[Dict[str, Any]] = []
    path = Path(row["path"])
    if path.suffix.lower() == ".pdf" and fitz is not None and path.exists():
        try:
            pdf = fitz.open(str(path))
            try:
                for level, title, page_no in pdf.get_toc(simple=True)[:400]:
                    toc.append({"level": int(level), "title": str(title),
                                "page": max(1, int(page_no))})
            finally:
                pdf.close()
        except Exception:
            toc = []
    return {
        "ok": True,
        "id": int(row["id"]),
        "title": row["title"],
        "filename": path.name,
        "lang": row["lang"],
        "pages": int(row["pages"]),
        "size": int(row["size"]),
        "ocr_pages": int(row["ocr_pages"] or 0),
        "needs_ocr": int(row["needs_ocr"] or 0),
        "indexed_at": row["indexed_at"],
        "toc": toc,
    }


def page_info(doc_id: int, page_no: int, lang: str = "zh") -> Dict[str, Any]:
    init_db()
    with _db() as conn:
        doc = conn.execute("SELECT * FROM docs WHERE id=?", (doc_id,)).fetchone()
        if not doc:
            return {"ok": False, "message": "文档不存在"}
        row = conn.execute(
            "SELECT * FROM pages WHERE doc_id=? AND page=?", (doc_id, page_no)
        ).fetchone()
        page_text = (row["text"] if row else "") or ""
        page_lang = _detect_lang(page_text) or doc["lang"] or "unknown"
        target_lang = "zh" if page_lang != "zh" else "en"
        trans = conn.execute(
            "SELECT * FROM translations WHERE doc_id=? AND page=? AND lang=?",
            (doc_id, page_no, target_lang),
        ).fetchone()
        trans_any = conn.execute(
            "SELECT * FROM translations WHERE doc_id=? AND page=? ORDER BY created_at DESC LIMIT 1",
            (doc_id, page_no),
        ).fetchone()
    boxes: List[Dict[str, Any]] = []
    if row and row["boxes"]:
        try:
            boxes = json.loads(row["boxes"])
        except Exception:
            boxes = []
    translation = trans or trans_any
    return {
        "ok": True,
        "doc_id": int(doc_id),
        "page": int(page_no),
        "pages": int(doc["pages"]),
        "title": doc["title"],
        "lang": page_lang,
        "text": page_text,
        "source": (row["source"] if row else "none") or "none",
        "needs_ocr": bool(row is None or row["source"] == "none"),
        "boxes": boxes,
        "translation": ({
            "lang": translation["lang"],
            "text": translation["text"],
            "model": translation["model"],
            "created_at": translation["created_at"],
        } if translation else None),
    }


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"[a-zA-Z0-9_./+\-]{2,}|[\u4e00-\u9fff]{2,}")


def _query_terms(query: str) -> List[str]:
    q = (query or "").strip()[:400]
    if not q:
        return []
    terms: List[str] = []
    for token in _WORD_RE.findall(q):
        token = token.strip("._-/")[:80]
        if len(token) >= 2:
            terms.append(token)
    if len(q) <= 80 and q not in terms:
        terms.insert(0, q)
    for token in list(terms):
        if re.fullmatch(r"[\u4e00-\u9fff]{4,}", token):
            terms.extend(token[i:i + 2] for i in range(len(token) - 1))
    out: List[str] = []
    seen = set()
    for t in terms:
        key = t.casefold()
        if key not in seen:
            seen.add(key)
            out.append(t)
    return out[:12]


def _score_text(text: str, terms: List[str], title: str = "") -> float:
    lower = (text or "").casefold()
    title_l = (title or "").casefold()
    score = 0.0
    for index, term in enumerate(terms):
        t = term.casefold()
        if not t:
            continue
        count = lower.count(t)
        if count:
            score += count * (6.0 if index == 0 else 2.0)
        if t in title_l:
            score += 8.0
    return score


def _snippet(text: str, terms: List[str], radius: int = 150) -> Tuple[str, int]:
    plain = re.sub(r"\s+", " ", text or " ").strip()
    lower = plain.casefold()
    positions = []
    for term in terms:
        pos = lower.find(term.casefold())
        if pos >= 0:
            positions.append(pos)
    start = max(0, (min(positions) if positions else 0) - radius)
    end = min(len(plain), start + radius * 2)
    snippet = plain[start:end]
    if not snippet:
        return snippet, start
    pattern = re.compile(
        "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True) if term),
        re.I)
    marked = pattern.sub(lambda match: f"[[{match.group(0)}]]", snippet)
    return marked, start


def _fuzzy_terms(conn: sqlite3.Connection, terms: List[str]) -> List[str]:
    """Correct common ASCII typos using a small sampled vocabulary."""
    ascii_terms = [t for t in terms if re.fullmatch(r"[A-Za-z][A-Za-z0-9_+./\-]{3,}", t)]
    if not ascii_terms:
        return []
    import difflib
    sample_rows = conn.execute(
        "SELECT text FROM pages WHERE text != '' ORDER BY RANDOM() LIMIT 120"
    ).fetchall()
    vocab = set()
    for row in sample_rows:
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_+./\-]{2,}", row["text"] or ""):
            vocab.add(word)
            if len(vocab) > 20000:
                break
    out = []
    for term in ascii_terms:
        matches = difflib.get_close_matches(term, list(vocab), n=2, cutoff=0.78)
        out.extend(m for m in matches if m.casefold() != term.casefold())
    return list(dict.fromkeys(out))[:6]


def _ocr_rects(boxes: List[Dict[str, Any]], terms: List[str]) -> List[List[float]]:
    rects = []
    for line in boxes:
        text = str(line.get("text") or "").casefold()
        if any(term.casefold() in text for term in terms):
            box = line.get("box") or []
            xs = [p[0] for p in box if isinstance(p, (list, tuple)) and len(p) >= 2]
            ys = [p[1] for p in box if isinstance(p, (list, tuple)) and len(p) >= 2]
            if xs and ys:
                rects.append([min(xs), min(ys), max(xs), max(ys)])
    return rects


def _text_rects(doc_id: int, page_no: int, terms: List[str]) -> List[List[float]]:
    init_db()
    with _db() as conn:
        doc = conn.execute(
            "SELECT path FROM docs WHERE id=?", (int(doc_id),)
        ).fetchone()
    if not doc:
        return []
    path = Path(doc["path"])
    if path.suffix.lower() != ".pdf" or fitz is None:
        return []
    try:
        pdf = fitz.open(str(path))
    except Exception:
        return []
    rects: List[List[float]] = []
    try:
        if page_no < 1 or page_no > len(pdf):
            return []
        page = pdf[page_no - 1]
        width = float(page.rect.width) or 1.0
        height = float(page.rect.height) or 1.0
        for term in terms[:6]:
            try:
                hits = page.search_for(term, quads=False)[:12]
            except Exception:
                hits = []
            for rect in hits:
                rects.append([
                    max(0.0, float(rect.x0) / width),
                    max(0.0, float(rect.y0) / height),
                    min(1.0, float(rect.x1) / width),
                    min(1.0, float(rect.y1) / height),
                ])
    finally:
        pdf.close()
    merged: List[List[float]] = []
    for rect in rects:
        for item in merged:
            if not (rect[2] < item[0] or rect[0] > item[2]
                    or rect[3] < item[1] or rect[1] > item[3]):
                item[0] = min(item[0], rect[0])
                item[1] = min(item[1], rect[1])
                item[2] = max(item[2], rect[2])
                item[3] = max(item[3], rect[3])
                break
        else:
            merged.append(list(rect))
    return merged[:24]


def _all_pages(conn: sqlite3.Connection,
               doc_id: Optional[int]) -> List[sqlite3.Row]:
    """Load indexed page text once; ranking is done in Python.

    Keeping the SQL statement free of user-derived fragments also keeps the
    query safe for arbitrary textbook search input.
    """
    rows = conn.execute(
        "SELECT d.id AS doc_id, d.title, d.lang, p.page, p.text, p.source, p.boxes "
        "FROM pages p JOIN docs d ON d.id=p.doc_id WHERE p.text != ''"
    ).fetchall()
    if doc_id is not None:
        wanted = int(doc_id)
        rows = [row for row in rows if int(row["doc_id"]) == wanted]
    return rows


def search(query: str, doc_id: Optional[int] = None, limit: int = 24,
           fuzzy: bool = True, with_rects: bool = True) -> Dict[str, Any]:
    init_db()
    query = (query or "").strip()
    if not query:
        return {"ok": True, "query": query, "results": [], "terms": [],
                "count": 0, "message": "请输入关键词"}
    terms = _query_terms(query)
    with _db() as conn:
        if fuzzy:
            for term in _fuzzy_terms(conn, terms):
                if term.casefold() not in {t.casefold() for t in terms}:
                    terms.append(term)
        rows = _all_pages(conn, doc_id)
        scored = []
        for row in rows:
            score = _score_text(row["text"], terms, row["title"])
            if score <= 0:
                continue
            scored.append((score, row))
        scored.sort(key=lambda x: x[0], reverse=True)
        per_doc: Dict[int, int] = {}
        chosen = []
        for score, row in scored:
            did = int(row["doc_id"])
            if per_doc.get(did, 0) >= 4:
                continue
            per_doc[did] = per_doc.get(did, 0) + 1
            chosen.append((score, row))
            if len(chosen) >= limit:
                break
        results = []
        for score, row in chosen:
            snippet, offset = _snippet(row["text"], terms)
            boxes = []
            if row["boxes"]:
                try:
                    boxes = json.loads(row["boxes"])
                except Exception:
                    boxes = []
            rects = _ocr_rects(boxes, terms) if boxes else []
            if not rects and with_rects and row["source"] == "text":
                rects = _text_rects(int(row["doc_id"]), int(row["page"]), terms)
            results.append({
                "doc_id": int(row["doc_id"]),
                "title": row["title"],
                "page": int(row["page"]),
                "lang": row["lang"],
                "source": row["source"],
                "score": round(score, 2),
                "snippet": snippet,
                "offset": int(offset),
                "rects": rects,
            })
    return {"ok": True, "query": query, "terms": terms,
            "results": results, "count": len(results),
            "fuzzy": bool(fuzzy)}


def ai_search(query: str, cfg: Dict[str, Any], doc_id: Optional[int] = None,
              lang: str = "zh", limit: int = 24) -> Dict[str, Any]:
    """Expand a natural-language question into search terms with the LLM."""
    terms: List[str] = []
    note = ""
    try:
        from . import llm
        prompt = (
            "你是电磁场、微波技术、天线与 Smith 圆图教材的检索助手。"
            "把用户的问题改写成 4-10 个适合在教材全文中检索的关键词/同义词，"
            "中英文都给出。只输出 JSON 数组，例如 [\"Smith chart\",\"史密斯圆图\",\"反射系数\"]。"
            f"\n用户问题：{query}"
        )
        resp = llm.chat(cfg, [
            {"role": "system", "content": "只输出 JSON，不要解释。"},
            {"role": "user", "content": prompt},
        ], timeout=45)
        raw = (resp.get("content") or "").strip()
        match = re.search(r"\[[\s\S]*\]", raw)
        if match:
            data = json.loads(match.group(0))
            terms = [str(x) for x in data if str(x).strip()][:10]
        note = f"AI 扩展词：{'、'.join(terms)}" if terms else "AI 未返回扩展词，已使用本地模糊检索。"
    except Exception as exc:  # noqa: BLE001
        note = f"AI 扩展不可用（{exc}），已使用本地模糊检索。"

    merged: Dict[Tuple[int, int], Dict[str, Any]] = {}
    for term in [query] + terms:
        try:
            result = search(term, doc_id=doc_id, limit=limit, fuzzy=True)
        except Exception:
            continue
        for item in result.get("results", []):
            key = (item["doc_id"], item["page"])
            if key not in merged:
                item["matched_term"] = term
                merged[key] = item
            else:
                merged[key]["score"] = max(merged[key]["score"], item["score"]) + 1
    results = sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:limit]
    return {"ok": True, "query": query, "terms": terms, "note": note,
            "results": results, "count": len(results)}


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _doc_path(doc_id: int) -> Optional[Path]:
    init_db()
    with _db() as conn:
        row = conn.execute(
            "SELECT path FROM docs WHERE id=?", (int(doc_id),)
        ).fetchone()
    return Path(row["path"]) if row else None


def _cache_key(path: Path, page_no: int, dpi: int, suffix: str = "") -> str:
    stat = path.stat()
    raw = f"{path}|{stat.st_mtime_ns}|{stat.st_size}|{page_no}|{dpi}|{suffix}"
    return hashlib.sha256(raw.encode("utf-8", "ignore")).hexdigest()[:32]


def render_page(doc_id: int, page_no: int, zoom: float = 1.0) -> bytes:
    config.ensure_dirs()
    path = _doc_path(doc_id)
    if not path or not path.exists():
        raise ValueError("文档不存在")
    if path.suffix.lower() != ".pdf" or fitz is None:
        raise ValueError("该文档不是 PDF")
    dpi = int(max(72, min(MAX_DPI, DEFAULT_DPI * max(0.35, min(3.0, float(zoom))))))
    key = _cache_key(path, page_no, dpi)
    target = cache_dir() / f"{key}.png"
    if target.exists():
        return target.read_bytes()
    pdf = fitz.open(str(path))
    try:
        if page_no < 1 or page_no > len(pdf):
            raise ValueError("页码超出范围")
        page = pdf[page_no - 1]
        scale = dpi / 72.0
        max_side = max(page.rect.width, page.rect.height) * scale
        if max_side > 4200:
            scale *= 4200 / max_side
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        data = pix.tobytes("png")
    finally:
        pdf.close()
    target.write_bytes(data)
    return data


def crop_page(doc_id: int, page_no: int, rects: List[List[float]],
              margin: float = 0.06, dpi: int = 220) -> bytes:
    path = _doc_path(doc_id)
    if not path or not path.exists() or path.suffix.lower() != ".pdf" or fitz is None:
        raise ValueError("文档不可用")
    pdf = fitz.open(str(path))
    try:
        if page_no < 1 or page_no > len(pdf):
            raise ValueError("页码超出范围")
        page = pdf[page_no - 1]
        width, height = float(page.rect.width), float(page.rect.height)
        if rects:
            x0 = min(r[0] for r in rects) * width
            y0 = min(r[1] for r in rects) * height
            x1 = max(r[2] for r in rects) * width
            y1 = max(r[3] for r in rects) * height
        else:
            x0, y0, x1, y1 = 0, 0, width, height
        pad_x, pad_y = (x1 - x0) * margin, (y1 - y0) * margin
        clip = fitz.Rect(max(0, x0 - pad_x), max(0, y0 - pad_y),
                         min(width, x1 + pad_x), min(height, y1 + pad_y))
        if clip.is_empty:
            clip = page.rect
        zoom = min(3.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
        return pix.tobytes("png")
    finally:
        pdf.close()


def page_image_base64(doc_id: int, page_no: int, dpi: int = 160) -> Optional[Dict[str, str]]:
    path = _doc_path(doc_id)
    if not path or path.suffix.lower() != ".pdf" or fitz is None:
        return None
    pdf = fitz.open(str(path))
    try:
        if page_no < 1 or page_no > len(pdf):
            return None
        page = pdf[page_no - 1]
        scale = dpi / 72.0
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        data = pix.tobytes("png")
        return {"mime": "image/png", "base64": base64.b64encode(data).decode("ascii")}
    finally:
        pdf.close()


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------

_TRANSLATION_SYSTEM = {
    "zh": (
        "你是电磁场与微波技术领域的学术翻译。把教材原文翻译成规范、准确的简体中文。"
        "专业术语采用国内学术界通用译法，首次出现时在括号中保留英文原词；"
        "公式、编号、图号、单位与变量符号保持原样；不要增删内容，不要解释。"
    ),
    "en": (
        "You are an academic translator in electromagnetics and microwave engineering. "
        "Translate the textbook passage into precise technical English. Keep formulas, "
        "figure numbers, units and variable symbols unchanged. Do not add explanations."
    ),
}


def translate_page(doc_id: int, page_no: int, cfg: Dict[str, Any],
                   target_lang: Optional[str] = None) -> Dict[str, Any]:
    init_db()
    info = page_info(doc_id, page_no)
    if not info.get("ok"):
        return info
    text = info.get("text") or ""
    if len(text.strip()) < 20:
        return {
            "ok": False,
            "message": "当前页没有可翻译的文字层，请先 OCR 或使用视觉模型读图。",
            "hint": "点击「OCR 本页」，然后在设置中选择支持图像理解的模型。",
        }
    source_lang = _detect_lang(text)
    if source_lang == "unknown":
        source_lang = info.get("lang") or "unknown"
    target = target_lang or ("zh" if source_lang != "zh" else "en")
    with _db() as conn:
        row = conn.execute(
            "SELECT * FROM translations WHERE doc_id=? AND page=? AND lang=?",
            (doc_id, page_no, target),
        ).fetchone()
    if row:
        return {"ok": True, "text": row["text"], "lang": target,
                "model": row["model"], "cached": True,
                "created_at": row["created_at"]}

    from . import llm
    # Thinking models can spend a small output budget entirely on reasoning.
    # Give translation its own generous limit instead of inheriting a chat
    # setting that may be as low as 2k tokens.
    llm_cfg = dict(cfg)
    llm_cfg["llm"] = dict(cfg.get("llm") or {})
    try:
        configured = int(llm_cfg["llm"].get("max_tokens") or 0)
    except (TypeError, ValueError):
        configured = 0
    llm_cfg["llm"]["max_tokens"] = max(configured, 16384)
    chunk = text[:14000]
    prompt = (
        f"请把下面这页教材原文翻译成{'简体中文' if target == 'zh' else '英文'}。"
        f"只输出译文。\n\n{chunk}"
    )
    resp = llm.chat(llm_cfg, [
        {"role": "system", "content": _TRANSLATION_SYSTEM.get(target, _TRANSLATION_SYSTEM["zh"])},
        {"role": "user", "content": prompt},
    ], timeout=120)
    translated = (resp.get("content") or "").strip()
    used_short = False
    if not translated:
        # Thinking models occasionally return an empty final message.  Retry
        # once with an explicit "output only the translation" instruction.
        retry_prompt = (
            "上一条请求没有返回可见译文。请忽略任何思考过程，直接输出完整译文，"
            "不要解释、不要重复原文。\n\n" + chunk
        )
        resp = llm.chat(llm_cfg, [
            {"role": "system", "content": _TRANSLATION_SYSTEM.get(target, _TRANSLATION_SYSTEM["zh"])},
            {"role": "user", "content": retry_prompt},
        ], timeout=120)
        translated = (resp.get("content") or "").strip()
    if not translated:
        # Last resort: a shorter chunk leaves room for both reasoning and the
        # visible translation on providers with small per-request budgets.
        used_short = True
        short = text[:6000]
        resp = llm.chat(llm_cfg, [
            {"role": "system", "content": _TRANSLATION_SYSTEM.get(target, _TRANSLATION_SYSTEM["zh"])},
            {"role": "user", "content": (
                "只输出译文，不要任何思考、解释或原文。\n\n" + short)},
        ], timeout=120)
        translated = (resp.get("content") or "").strip()
    if not translated:
        return {"ok": False, "message": "模型没有返回译文",
                "hint": "已自动提高输出上限并重试三次；请稍后重试，或在设置中换用非思考模型。"}
    model = str(resp.get("model") or "")
    created = datetime.now().isoformat(timespec="seconds")
    with _db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO translations(doc_id,page,lang,text,model,created_at)"
            " VALUES(?,?,?,?,?,?)",
            (doc_id, page_no, target, translated, model, created),
        )
        conn.commit()
    return {"ok": True, "text": translated, "lang": target, "model": model,
            "cached": False, "created_at": created,
            "truncated": len(text) > 14000 or used_short}


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

def add_book(filename: str, content_b64: str) -> Dict[str, Any]:
    import binascii
    import uuid
    original = Path(str(filename or "book.pdf")).name
    suffix = Path(original).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(f"教材库支持 PDF / TXT / Markdown / TeX / DOCX / PPTX / XLSX / IPYNB，收到：{suffix or '无扩展名'}")
    try:
        raw = base64.b64decode(content_b64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("文件内容不是有效的 Base64 数据") from exc
    if not raw:
        raise ValueError("文件为空")
    if len(raw) > 400 * 1024 * 1024:
        raise ValueError("单个教材文件不能超过 400 MB")
    target_dir = config.LIBRARY_DIR / "books"
    target_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w\u4e00-\u9fff.\-]+", "_", original)[:100]
    # Keep the user-visible filename intact by giving each upload its own
    # folder; a UUID prefix in the filename leaked into titles and citations.
    book_dir = target_dir / uuid.uuid4().hex[:8]
    book_dir.mkdir(parents=True, exist_ok=True)
    target = book_dir / safe
    target.write_bytes(raw)
    init_db()
    with _db() as conn:
        _index_document(conn, target, ocr_first_pages=1)
    return {"ok": True, "name": original, "path": str(target),
            "message": f"已加入教材库：{original}"}

