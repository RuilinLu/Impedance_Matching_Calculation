"""Any-file attachment tests, including OCR and vision payloads."""

from __future__ import annotations

import base64
import io
import sys
import tempfile
import unittest
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from impedance_mcp import attachments, config  # noqa: E402

try:
    import pymupdf as fitz
except Exception:  # pragma: no cover
    fitz = None

try:
    from PIL import Image, ImageDraw
except Exception:  # pragma: no cover
    Image = None


class AttachmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_upload = config.UPLOAD_DIR
        config.UPLOAD_DIR = Path(self.tmp.name) / "uploads"
        config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        config.UPLOAD_DIR = self.old_upload
        self.tmp.cleanup()

    def upload(self, name, raw):
        return attachments.save_upload(name, base64.b64encode(raw).decode())

    def test_matlab_and_binary_files(self):
        code = self.upload("demo.m", b"function y = demo(z)\n% Smith chart\ny=abs(z);\nend\n")
        self.assertEqual(code["kind"], "code")
        self.assertIn("Smith chart", code["text"])
        binary = self.upload("payload.bin", bytes(range(256)) * 8)
        self.assertEqual(binary["kind"], "binary")
        self.assertIn("二进制", binary["note"])

    @unittest.skipIf(Image is None, "Pillow is not installed")
    def test_image_ocr_and_vision_payload(self):
        image = Image.new("RGB", (900, 260), "white")
        draw = ImageDraw.Draw(image)
        draw.text((30, 80), "Smith chart reflection coefficient VSWR", fill="black")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        info = self.upload("chart.png", buffer.getvalue())
        self.assertEqual(info["kind"], "image")
        self.assertEqual(info["image_count"], 1)
        self.assertIn("Smith", info["text"])
        text, ui = attachments.attachment_context([{"id": info["id"], "name": info["name"]}])
        self.assertIn("Smith chart", text)
        images = attachments.vision_images([{"id": info["id"], "name": info["name"]}])
        self.assertEqual(len(images), 1)
        self.assertTrue(images[0]["url"].startswith("data:image/"))

    @unittest.skipIf(fitz is None, "PyMuPDF is not installed")
    def test_scanned_pdf_ocr(self):
        source = fitz.open()
        page = source.new_page()
        page.insert_text((72, 100), "Smith chart impedance matching", fontsize=20)
        pix = page.get_pixmap(dpi=150)
        png = pix.tobytes("png")
        source.close()
        scanned = fitz.open()
        target = scanned.new_page(width=612, height=792)
        target.insert_image(target.rect, stream=png)
        buffer = io.BytesIO()
        scanned.save(buffer)
        scanned.close()
        info = self.upload("scan.pdf", buffer.getvalue())
        self.assertEqual(info["kind"], "pdf")
        self.assertEqual(info["image_count"], 1)
        self.assertIn("Smith", info["text"])
        self.assertIn("OCR", info["note"])

    def test_clipboard_text(self):
        info = attachments.save_text("z = 20 + 5j  % Smith chart", "clipboard.m")
        self.assertEqual(info["kind"], "code")
        self.assertIn("Smith chart", info["text"])

    def test_legacy_office_is_accepted(self):
        info = self.upload("old.doc", b"\xd0\xcf\x11\xe0" + b"\x00" * 512)
        self.assertEqual(info["kind"], "legacy_office")
        self.assertIn("DOCX", info["note"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
