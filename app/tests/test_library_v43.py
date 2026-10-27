"""Textbook library tests: indexing, search, rendering, OCR and translation cache."""

from __future__ import annotations

import base64
import sys
import tempfile
import unittest
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from impedance_mcp import config, library  # noqa: E402

try:
    import pymupdf as fitz
except Exception:  # pragma: no cover
    fitz = None


@unittest.skipIf(fitz is None, "PyMuPDF is not installed")
class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_library = config.LIBRARY_DIR
        self.old_sources = config.LIBRARY_SOURCE_DIRS
        self.old_source_paths = config.library_source_paths
        config.LIBRARY_DIR = self.root / "library"
        config.LIBRARY_SOURCE_DIRS = [self.root / "books"]
        config.library_source_paths = lambda cfg=None: [self.root / "books"]
        config.LIBRARY_SOURCE_DIRS[0].mkdir(parents=True, exist_ok=True)
        library._INDEX_STATE.update({"running": False, "phase": "idle", "total": 0,
                                     "done": 0, "current": "", "error": ""})
        self.pdf = config.LIBRARY_SOURCE_DIRS[0] / "test-book.pdf"
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 100), "Smith chart impedance matching", fontsize=18)
        page.insert_text((72, 140), "reflection coefficient and VSWR", fontsize=14)
        page2 = doc.new_page()
        page2.insert_text((72, 100),
                          "Second page about transmission lines, reflection and matching networks",
                          fontsize=16)
        doc.save(str(self.pdf))
        doc.close()

    def tearDown(self):
        config.LIBRARY_DIR = self.old_library
        config.LIBRARY_SOURCE_DIRS = self.old_sources
        config.library_source_paths = self.old_source_paths
        self.tmp.cleanup()

    def test_index_search_render(self):
        status = library.sync_index(ocr_first_pages=0)
        self.assertEqual(status["docs"], 1)
        self.assertGreaterEqual(status["indexed_pages"], 2)
        result = library.search("Smith chart", limit=4)
        self.assertTrue(result["ok"])
        self.assertGreaterEqual(result["count"], 1)
        item = result["results"][0]
        self.assertEqual(item["page"], 1)
        self.assertTrue(item["snippet"])
        self.assertGreaterEqual(len(item["rects"]), 1)
        info = library.page_info(item["doc_id"], 1)
        self.assertIn("Smith chart", info["text"])
        png = library.render_page(item["doc_id"], 1, 1.0)
        self.assertTrue(png.startswith(b"\x89PNG"))
        crop = library.crop_page(item["doc_id"], 1, item["rects"])
        self.assertTrue(crop.startswith(b"\x89PNG"))

    def test_fuzzy_and_ai_fallback(self):
        library.sync_index(ocr_first_pages=0)
        result = library.search("Smiht chart", fuzzy=True, limit=4)
        self.assertTrue(result["ok"])
        ai = library.ai_search("圆图反射系数", {"llm": {}}, limit=4)
        self.assertTrue(ai["ok"])
        self.assertIn("AI", ai["note"])
        self.assertIn("results", ai)

    def test_ocr_scanned_page(self):
        scanned = config.LIBRARY_SOURCE_DIRS[0] / "scan.pdf"
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 100), "Smith chart impedance matching", fontsize=20)
        pix = page.get_pixmap(dpi=150)
        png = pix.tobytes("png")
        doc.close()
        scan = fitz.open()
        target = scan.new_page(width=612, height=792)
        target.insert_image(target.rect, stream=png)
        scan.save(str(scanned))
        scan.close()
        library.sync_index(ocr_first_pages=0)
        docs = library.doc_list()
        scan_doc = next(item for item in docs if item["filename"] == "scan.pdf")
        result = library.ocr_page(scan_doc["id"], 1, force=True)
        self.assertTrue(result["ok"], result)
        self.assertIn("Smith", result["text"])
        widths = []
        for line in result.get("lines") or []:
            xs = [point[0] for point in line.get("box") or []]
            if xs:
                widths.append(max(xs) - min(xs))
        self.assertTrue(widths, "OCR returned no boxes")
        # Boxes are normalized against the rendered pixmap, not PDF points.
        self.assertGreater(min(widths), 0.002)
        self.assertLessEqual(max(widths), 1.0)
        search = library.search("Smith chart", limit=4)
        self.assertTrue(any(item["source"] == "ocr" for item in search["results"]))

    def test_text_upload(self):
        result = library.add_book("note.md", base64.b64encode(
            b"# Smith chart notes\nImpedance matching example").decode())
        self.assertTrue(result["ok"])
        library.sync_index(ocr_first_pages=0)
        titles = {item["title"] for item in library.doc_list()}
        self.assertIn("note", titles)
        search = library.search("impedance matching", limit=4)
        self.assertGreaterEqual(search["count"], 1)

    def test_docx_upload(self):
        try:
            import docx
            import io
        except Exception:
            self.skipTest("python-docx is not installed")
        document = docx.Document()
        document.add_paragraph("Smith chart notes for a DOCX textbook")
        document.add_paragraph("Reflection coefficient and matching network")
        buffer = io.BytesIO()
        document.save(buffer)
        result = library.add_book("notes.docx", base64.b64encode(buffer.getvalue()).decode())
        self.assertTrue(result["ok"], result)
        library.sync_index(ocr_first_pages=0)
        search = library.search("reflection coefficient", limit=4)
        self.assertGreaterEqual(search["count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
