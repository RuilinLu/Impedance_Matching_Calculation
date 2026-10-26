# Documentation

The full documentation is built into the application. Open **文档中心 / Documentation** in the app to search it word by word:

| Domain | Contents |
|---|---|
| 软件功能 / Application | Every view, input, button, output metric and Smith-chart learning workflow |
| 代码参考 / Code | AST-generated module, function, parameter, return, local-variable and front-end function reference |
| AI 接口 / AI | Providers, protocols, capability matrix, vision, pricing, cache, cost and catalog updates |
| MCP 协议 / MCP | stdio / Streamable HTTP / legacy SSE, live tool schemas, resources, prompts and client setup |

Documentation is Markdown stored in `app/impedance_mcp/docs_content/` plus the live code reference generated from `app/impedance_mcp/code_docs.py`. No PDF is generated.

Textbooks are **not** part of this repository. Put your own PDFs in `TextBook/` (next to the app or repository) or `data/library/books/`; the local index and OCR stay on your machine.
