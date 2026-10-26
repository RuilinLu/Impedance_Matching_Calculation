# Third-party notices

This project is distributed under the MIT License (see `LICENSE`). It uses the following third-party components; their licenses apply to those components.

| Component | Version / source | License | Use |
|---|---|---|---|
| MathJax | 3.2.2, `web/vendor/mathjax/tex-svg-full.js` | Apache-2.0 (`web/vendor/mathjax/LICENSE`) | Offline LaTeX rendering |
| PyMuPDF | `pymupdf` package | AGPL-3.0 (or commercial license from Artifex) | PDF text, page rendering, search rectangles |
| pypdf | `pypdf` package | BSD-3-Clause | Fallback/optional PDF text handling |
| RapidOCR / onnxruntime | `rapidocr_onnxruntime` | Apache-2.0 / MIT | Offline Chinese/English OCR |
| Pillow | `Pillow` | HPND | Image handling |
| python-docx / python-pptx / openpyxl | respective packages | MIT / MIT / MIT | Office text extraction |
| pywebview / pythonnet | respective packages | BSD-3-Clause / MIT | Native Windows window |
| NumPy | `numpy` | BSD-3-Clause | Numerical arrays |

## PyMuPDF (AGPL) note

PyMuPDF is used by the PDF library and page-rendering features. Its AGPL-3.0 license is stricter than MIT. The complete source of this project is published in the same repository, which supports AGPL compliance for the combined work. If you redistribute a binary that includes PyMuPDF, review the AGPL-3.0 obligations (or obtain a commercial PyMuPDF license). Users who need an MIT-only distribution can remove the textbook PDF rendering/OCR features and replace `pymupdf` with a permissive PDF renderer.

MathJax is bundled locally so the documentation and AI formulas render without any CDN or network access.
