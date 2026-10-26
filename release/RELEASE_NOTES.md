# Impedance Matching AI v4.3.0

**Release date: 2026-10-27**
**Developers: Ruilin Lu, Keji Lu, Zhiyi Lin, Yunlei Zhang**

A standalone microwave matching application and MCP server. It combines L/T/π design with full nodal verification, Smith-chart animation and scan density, voltage stress, a searchable textbook library with OCR and translation, four documentation domains, and a tool-calling AI agent.

## Highlights

- **Textbook library**: local PDF indexing, full-text/fuzzy search, page rendering and zoom, OCR for scanned books (single page or page range), academic translation, full-page thumbnails and cropped citation screenshots.
- **Documentation centre**: four searchable domains (application, code, AI interface, MCP) with every-word highlighting and previous/next match navigation. Code reference is generated from the live AST.
- **Any-file agent input**: PDF, DOCX, PPTX, XLSX, source code, images, archives and arbitrary binaries; clipboard and drag-and-drop; vision models receive page/image content.
- **Complete offline LaTeX**: AI answers and documentation render `$...$`, `\(...\)`, `$$...$$`, `\[...\]`, `align`, `cases`, matrices, physics/chemistry extensions; no CDN required.
- **20 provider catalog**: per-model context, output, vision/audio, tools, JSON, reasoning, Responses/Anthropic API, FIM, concurrency, currency, cache-hit/miss/output prices and editable peak/off-peak windows; one-click updates from models.dev / official `/models` / announcements, AI-assisted review, backup and rollback.
- **Usage accounting**: tokens, cache hit rate, context usage and cost per request and per day/week/all time.
- **Scan visualization**: grey density cloud, boundary envelope and cyan near-centre highlights; fixed Run Scan state handling.
- **Bilingual UI** and independent branding; MATLAB/MATLAB Runtime support removed completely.

## Assets

- `Impedance_Matching_AI_v4.3.0_Source.zip` — clean source tree without textbooks, user data or API keys.
- `Impedance_Matching_AI_v4.3.0_Portable.exe` — native WebView2 GUI.
- `Impedance_Matching_AI_v4.3.0_MCP.exe` — MCP stdio/HTTP server.
- `SHA256SUMS.txt` — verify downloads.

Textbooks are user-supplied and not included. Put PDFs in `TextBook/` or `data/library/books/`.
