# Application Guide

> This is an independent microwave/RF teaching, calculation and simulation tool. It is not tied to any platform or event. All computation, plotting, library indexing and MCP serving happen locally. Only AI chat sends the current question and the attachments you explicitly add to the provider you configure.

## 1. Layout

| Area | Contents | Notes |
|---|---|---|
| Left navigation | AI Agent, Design, Smith Analysis, Stress, Library, Documentation, About | Each view keeps the current design context |
| Top bar | active model, MCP status, language, settings, export report | Local calculation works without any model |
| Main workspace | forms, charts, documentation, textbook pages | Responsive width and scrolling |
| Floating assistant | bottom-right `AI` button on every view | Collapse to a button, expand for contextual questions |

The language button switches the interface between Chinese and English. Numerical values, units and textbook originals keep their standard notation.

### 1.1 Mathematics and LaTeX

AI answers, documentation and textbook translations render LaTeX. Use `\( ... \)` for inline math and `\[ ... \]` for display math; `$ ... $`, `$$ ... $$` and `\begin{equation}` are also accepted. The bundled offline MathJax supports fractions, roots, Greek letters, sub/superscripts, integrals, matrices, cases, `align`, `cases`, `boldsymbol` and `mhchem`.

For example:

\[
z = \frac{Z_L}{Z_0}, \qquad
\Gamma = \frac{z-1}{z+1}, \qquad
\mathrm{VSWR} = \frac{1+|\Gamma|}{1-|\Gamma|}
\]

An ABCD cascade:

\[
\begin{bmatrix} A & B \\ C & D \end{bmatrix}
=
\begin{bmatrix} 1 & j\omega L \\ 0 & 1 \end{bmatrix}
\begin{bmatrix} 1 & 0 \\ j\omega C_1 & 1 \end{bmatrix}
\]

If a formula cannot be rendered, the original LaTeX text is preserved instead of disappearing.

## 2. AI Agent

- `Enter` sends, `Shift+Enter` inserts a newline.
- Tool cards show the tool name, arguments, latency and a result summary.
- All numerical conclusions about frequency, impedance, component values, VSWR, bandwidth and voltage stress come from local tools; the model explains them.
- Each answer reports input/output tokens, cache hit rate, context usage, cost and latency.

### 2.1 Any file, clipboard and drag-and-drop

Click the paperclip, drop files onto the composer, or press `Ctrl+V`. Extensions are no longer restricted.

| Type | Handling |
|---|---|
| PDF | Text layer; scanned pages can be OCR'ed or rendered for a vision model |
| DOCX / PPTX / XLSX | Paragraphs, slide text, worksheet cells |
| TXT / MD / TEX / CSV / source code | MATLAB, C, C++, Python, Verilog and other text files |
| Images | Local OCR plus the original image when the model supports vision |
| Audio / video / archives / other binaries | Stored and described; readable metadata or archive listing is sent |

Plain text on the clipboard becomes a temporary `.txt` attachment. Code-like text is named according to the detected language. Attachments can be removed before sending.

### 2.2 Vision

If “Image understanding” is enabled in the model profile, images and scanned pages are sent as OpenAI `image_url` or Anthropic `image` blocks. Without vision support, only OCR text is sent and the UI says so.

### 2.3 Textbook citations

The agent can call `search_textbooks`, `read_textbook_page`, `translate_textbook_page` and `search_docs`. Textbook citations include the title, page, matched snippet, a page thumbnail or crop, and an “Open textbook page” button that jumps to the library and highlights the match.

### 2.4 Floating assistant

The floating assistant is available on every view and carries context automatically:

- current design: topology, frequency, load, components, VSWR;
- current textbook: title, page, selected text;
- current document: category, heading, selected paragraph.

It shares the model configuration and usage accounting with the main agent but keeps a separate conversation.

## 3. Design

### 3.1 Inputs

| Parameter | Unit | Meaning |
|---|---|---|
| Frequency | MHz | operating frequency f0 |
| System impedance | Ω | reference Z0, usually 50 |
| R_L | Ω | load resistance, > 0 |
| X_L | Ω | load reactance, negative for capacitive loads |
| Topology | — | auto, L-right, L-left, T, π-I, π-II |
| Auto fixed elements | — | choose practical L and C3 automatically |
| L | µH | fixed series inductance when auto is off |
| C3 | pF | third capacitor for T/π topologies |

### 3.2 Outputs

- KPIs: VSWR, S11 (dB), VSWR<2 bandwidth (%), design Q.
- Smith chart: load, match point, animated trajectory, play/pause/reset/speed.
- Matching steps: element, series/shunt, start/end impedance, explanation; click a step to show only the trajectory up to it.
- Topology diagram and component values.
- VSWR bandwidth sweep and threshold.
- ±5% component tolerance sensitivity.
- Engineering warnings: tiny/large components, parasitics, self-resonance, high Q.
- Alternative topologies with component values, bandwidth, Q and ranking.

### 3.3 Formulas

- `z = Z/Z0`, `Γ = (z−1)/(z+1)`.
- `VSWR = (1+|Γ|)/(1−|Γ|)`, `S11(dB) = 20log10|Γ|`, return loss `RL = −S11`.
- L-network Q: `Q = √(R_high/R_low − 1)`.
- Series elements move along constant-resistance circles; shunt elements move along constant-conductance circles. Series inductance moves up, series capacitance down; shunt capacitance up, shunt inductance down.
- Every analytical solution is re-evaluated with a full nodal analysis of Zin, VSWR, S11 and element voltages/currents.

### 3.4 Smith-chart learning path

1. Enter a load such as `2.4 GHz, 20+j5 Ω`.
2. Solve and watch the load move to the centre.
3. Pause and click individual steps to isolate each element.
4. Switch between L, T and π to compare trajectory length, Q and bandwidth.
5. Search the library for `Smith chart`, `reflection coefficient` or `反射系数` and read the textbook page beside the chart; use the floating assistant to explain formulas.

## 4. Smith Analysis (forward scan)

- Inputs: topology, frequency, Z0, fixed L, grid steps, C1/C2/C3 ranges, target load.
- Grey density cloud: darker grey means more matchable loads in that region.
- Cyan highlight: points close to the centre (low reflection).
- Orange marker: current load.
- Boundary envelope: shows whether the target load is inside the matchable region.
- Hover shows Z, Γ and VSWR.

Results: R/X min/max and 5–95% percentiles, valid point count, sampled point count, five-topology bandwidth comparison, and an automatic conclusion.

If “Run scan” appears unresponsive, check that L is positive and the ranges are valid; errors are shown in the conclusion panel and the previous successful result is kept.

## 5. Stress

Inputs: topology, frequency, power, load, L/C1/C2/C3 and rated voltage. Outputs: source open-circuit peak, input peak, load peak, per-element peak/RMS voltage and current, safety factor (rated/peak), and engineering advice. The calculation uses the full nodal model including the 50 Ω source.

## 6. Textbook Library

### 6.1 Adding books

Put PDFs in `TextBook/` (project or installation folder) or `data/library/books/`, or click “Add textbook”. TXT, Markdown and TeX are also accepted. “Rebuild index” forces a full rescan; normal startup only processes new or modified files.

Textbooks are not distributed with the repository. The software reads local files only and never uploads them.

### 6.2 Indexing and OCR

- Text-layer PDFs are indexed page by page.
- Scanned PDFs are flagged as “OCR needed”; the first pages of each book are OCR'ed automatically so the table of contents becomes searchable.
- “OCR this page” runs RapidOCR locally (Chinese/English).
- “OCR this book” queues a page range in the background.
- A vision model can read page images even without OCR.

### 6.3 Search

- Instant full-text search for Chinese, English, code symbols and formula fragments.
- Fuzzy search corrects English typos and splits long Chinese terms into bigrams.
- AI semantic search expands a natural-language question into Chinese/English keywords, then ranks locally.
- Filter by book; results are grouped by book and page (up to four pages per book).
- Matches are highlighted in the snippet and as rectangles on the page image.

### 6.4 Reading

- Previous/next page, page jump, zoom in/out/fit width.
- Text panel: text layer or OCR result; if empty, OCR or use vision.
- Translation panel: one-click academic Chinese/English translation, cached per page to avoid repeated cost.
- PDF outline when available.
- Search results and AI citations open the exact page and highlight the match.

### 6.5 Working with the AI

- “Ask about this page” sends the title, page and text to the floating assistant.
- For scanned pages, the assistant can request a page image for a vision model.
- Citations in answers include a thumbnail; “Open textbook page” returns to the library at the right page.

## 7. Documentation Centre

Four searchable domains:

1. **Application guide** — this document.
2. **Code reference** — generated from the live AST: modules, classes, functions, parameters, defaults, returns, exceptions, local variables, module constants and front-end functions.
3. **AI model interface** — providers, protocols, capability matrix, vision, tools, pricing, cache and updates.
4. **MCP protocol** — stdio / Streamable HTTP / legacy SSE, tool schemas, resources, prompts and client configuration.

Search highlights every occurrence in the current document and provides “previous / next” navigation with an `n / m` counter. “All documents” searches across the four domains. “AI fuzzy search” expands natural language into keywords and falls back to local fuzzy matching when no model is configured.

Select text and use the floating assistant to explain it with the current document and section as context.

## 8. Settings

### 8.1 Model service

- 20 built-in providers: OpenAI, Anthropic, Google, DeepSeek, Alibaba DashScope, Zhipu, Moonshot, Baidu Qianfan, Tencent Hunyuan, ByteDance Ark, MiniMax, 01.AI, StepFun, Baichuan, iFlytek Spark, SiliconFlow, OpenRouter, xAI, Mistral, Groq.
- Protocol: OpenAI-compatible, Anthropic Messages, or a fully custom URL.
- Model: catalog selection or a custom model ID.
- API key: stored only in local `data/config.json`, displayed as the first/last four characters.
- Temperature, maximum output tokens, reasoning mode and thinking budget.

### 8.2 Model profile

Context length, maximum output, image/audio input, tool calls, JSON output, reasoning, Responses API, Anthropic API, FIM, input price with/without cache, output price, peak/off-peak prices, concurrency and currency. These values drive context usage and cost accounting.

### 8.3 Catalog updates

- **Update from official catalog**: reads models.dev and the current provider's `/models` endpoint; user overrides are preserved.
- **Read official announcements**: fetches public model/pricing pages and extracts candidate model IDs; failures are listed per provider.
- **AI-assisted update**: sends the current catalog and announcement excerpts to the configured model and asks for a strict JSON patch. The UI warns that AI output may be wrong and must be reviewed.
- **Rollback**: every update is backed up; one click restores the previous catalog.

### 8.4 Usage

Per-request and daily/7-day/all-time totals: requests, tokens, cache hit rate, cost. The log is `data/usage.jsonl`.

### 8.5 MCP configuration

Copy the stdio configuration from Settings or About:

```json
{
  "mcp": {
    "servers": {
      "impedance-matching-ai": {
        "type": "stdio",
        "command": "python",
        "args": ["<project>/app/run_mcp.py"]
      }
    }
  }
}
```

## 9. Standalone and MCP modes

- Standalone: design, scan, stress, reports, library and documentation work without any model.
- MCP server: exposes the same tools to ZCode, Claude Code, Codex, Cursor, Cherry Studio and other clients.
- HTTP/SSE: `python app/run_mcp.py --http 8790` provides `/mcp` and `/sse`.

## 10. Troubleshooting

| Symptom | Check |
|---|---|
| No models listed | Base URL, API key, network/proxy; use “Test connection” for the HTTP error |
| Attachment not parsed | File may be corrupt or legacy binary `.doc`/`.ppt`; it is still stored; export to PDF/DOCX or send a screenshot |
| Scanned PDF not searchable | No text layer; OCR the page/book or configure a vision model |
| OCR is slow | RapidOCR takes about 1–3 s per page on CPU; batch OCR runs in the background |
| Translation fails | Model not configured, key invalid, or the page has no text; OCR first |
| Context usage too high | Remove attachments or use a longer-context model; adjust the profile |
| MCP client sees no tools | Check client config, Python path and `run_mcp.py`; inspect client logs |
| Model broken after update | Use “Rollback catalog” in Settings |


## 11. v4.4 operations

### 11.1 Library paths and panel sizes

1. Open **Textbook Library** and click **Paths**.
2. The dialog shows the installation directory, user-data directory and current library. The installation `TextBook` folder is resolved dynamically, so moving the application does not leave a stale path.
3. Folders are scanned top to bottom. Each row can be enabled, moved up/down or removed. Enter an absolute path at the bottom, or use **Browse…** in the desktop window.
4. **Save and reindex** rescans every enabled folder in the background. Missing folders are marked and skipped.
5. Drag the vertical handle between search results and the reader to change their widths, and the horizontal handle between the page and the original/translation panes to change their heights. Sizes persist across restarts.

### 11.2 Smith scan and simulation points

- **Simulation points** is the number of real component combinations (default 10,000, maximum 250,000). Two-element topologies distribute it over C1/C2; three-element topologies over C1/C2/C3.
- While scanning, the progress bar reports evaluated/total and valid points, and real points appear on the chart. The grey region is drawn only after all points finish.
- The region is rasterised from the parameter-grid curves and the strips between adjacent curves, not from a convex hull. Capacitance values use logarithmic spacing, so widening a range cannot shrink the covered area.
- Increase the point count for a smoother boundary, or lower it for a quick preview. **Stop scan** aborts the stream.

### 11.3 Stress sweep and evidence

- With **Frequency × power sweep** enabled, every combination in ±frequency span and 10 %–100 % power performs a full nodal solve. The UI reports solve count, elapsed time and the worst frequency/power/element.
- A `*` in the peak-voltage column means the worst value over the sweep; hover for the nominal value. Safety factors use the worst voltage.
- With the sweep off only the nominal point is solved. A single linear solve is genuinely fast for a network with at most three nodes; the UI now shows the solve count and elapsed time.

### 11.4 Uploads and chat display

- Pasted screenshots/files appear immediately with a spinner, uploaded percentage and progress bar. Sending is blocked until every attachment reaches 100 %.
- The **Thinking** and **References** chips under the composer control the default expanded state. Each answer has its own collapsible thinking and sources sections and nothing is lost when collapsed.
- The same defaults can be changed under Settings → Interface and apply to both the main chat and the floating assistant.

### 11.5 Updates and uninstall

- About two seconds after startup the app checks the latest GitHub Release. When a newer version exists, a dialog shows current/latest versions, release notes and (if a model is configured) a compatibility review.
- **Skip this version** stores the version and stops proactive prompts. **Open release page** opens the browser; **Download and install** downloads with a percentage and launches the installer.
- The uninstaller uses a checkbox to keep personal data. It is checked by default and preserves API keys, model connections, settings, index, uploads, reports, translation cache and search paths; only unchecking it deletes them. In keep mode, files in the installation `TextBook` folder are first copied to the user-data directory, and the next installer detects and reuses them.

### 11.6 Compatibility

4.4.0 reads 4.3.x `config.json`, textbook SQLite index, uploads and reports directly. New settings are merged with defaults without dropping old keys, and the index rebuilds automatically when paths change. 4.5.x remains compatible with 4.4.x data and interfaces and is the compatibility baseline for later releases.


## 12. v4.4.1 stability fixes

- `POST /api/stress` honours `sweep=false` and performs exactly one nodal solve; single-point worst voltage/current are no longer zero.
- `POST /api/scan` accepts `points_budget`/`sim_points`; three-element scans add samples for wide capacitance ranges so coverage does not shrink as the range grows.
- Textbook translation raises its own output limit and retries with a shorter chunk, avoiding empty answers from thinking models.
- Documentation search highlights terms inside code blocks; long library paths wrap inside the sidebar.

## 13. v4.5.0 chat and multi-model work

### 13.1 Long conversations and clearing

Chat messages no longer shrink inside the flex scroller, and the assistant's smooth-scroll queue was replaced by frame-throttled instant scrolling. Both the main panel and the floating assistant can scroll back through the full conversation. Each panel has a New conversation button that clears only the transcript, leaving reports, textbook index, uploads and settings intact.

### 13.2 Stop, edit and resend

During streaming the send button becomes a spinning stop control. Stopping aborts the request immediately, keeps the partial answer and shows a stopped note. Enter cannot send a second question while a response is running. Every user message offers Edit and Copy; saving an edit truncates the conversation at that question and resends it. A generation counter discards late events from a cleared or replaced stream.

### 13.3 Multi-provider connections

Settings → Model service lists saved connections. Every save stores provider, Base URL, model and key as one connection and makes it active; configuring another vendor keeps the previous one. The model pickers in both chat surfaces group models by connection and switch through `/api/connections/activate`, updating the status pill and usage accounting. Keys stay in the local config file; public API responses expose only `has_key` and a masked hint.

### 13.4 Multimodal output

Provider `image`, `audio`, `video` and `file` blocks become media events. Markdown images, video, audio, PDF and data files render as media cards with download, copy-image, copy-link and open actions. `get_smith_trajectory` now generates a Smith-chart SVG on the server (`/api/media/…`) that appears directly in chat and can be downloaded.

### 13.5 LaTeX copy

Every formula keeps its TeX source in `data-latex`. Click a formula to copy the TeX; display formulas also show a Copy LaTeX button on hover. Each answer offers Copy answer (Markdown plus TeX) and Copy all formulas, instead of copying MathJax's generated SVG text.

### 13.6 Display switches

Show thinking, Show references and Show tool calls are synchronised between settings, the main chat and the floating assistant. Tool cards are hidden by default behind a compact activity line, and web references render as clickable links.

### 13.7 Installer and data

The uninstaller now uses a custom form with a checked “keep my personal data, settings, textbook index and library” box; only unchecking it invokes `--delete-user-data`. The installer detects an existing config, textbook index or TextBook folder and shows a reuse confirmation page, so an in-place upgrade never clears keys or index data.

- MCP HTTP sessions have a TTL and a hard cap, so misbehaving clients cannot grow memory without bound.
