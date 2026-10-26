# MCP Protocol Interface

The application is also a standard MCP server. The same calculation and library tools serve the built-in agent and external clients such as ZCode, Claude Code, Codex, Cursor and Cherry Studio.

## 1. Transports

| Mode | Command | Endpoint |
|---|---|---|
| stdio | `python app/run_mcp.py` | newline-delimited JSON-RPC on stdin/stdout |
| Streamable HTTP | `python app/run_mcp.py --http 8790` | `POST http://127.0.0.1:8790/mcp` |
| legacy HTTP+SSE | same | `GET /sse` + `POST /messages?sessionId=...` |
| health | same | `GET /health` |

The Windows build uses `ImpedanceMatchingAI_MCP.exe --mcp` so the GUI subsystem does not consume stdio.

## 2. Client configuration

```json
{
  "mcp": {
    "servers": {
      "impedance-matching-ai": {
        "type": "stdio",
        "command": "python",
        "args": ["D:/path/to/app/run_mcp.py"],
        "env": {"PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"}
      }
    }
  }
}
```

HTTP clients use `{"type":"http","url":"http://127.0.0.1:8790/mcp"}`.

## 3. Protocol versions

`2024-11-05`, `2025-03-26`, `2025-06-18`; the server negotiates the requested version and falls back to `2025-06-18`. Capabilities: tools, resources, prompts, logging. JSON-RPC batches, server-initiated sampling and resource subscriptions are not supported.

## 4. Transport details

- stdio: one JSON-RPC message per line, also tolerates `Content-Length` framing; only JSON-RPC goes to stdout, logs go to stderr.
- Streamable HTTP: `POST /mcp`, optional `Mcp-Session-Id`; `Accept: text/event-stream` returns one SSE message, otherwise JSON; `DELETE /mcp` terminates the session; `GET /mcp` returns 405.
- Legacy SSE: `GET /sse` emits `event: endpoint`; client posts to `/messages?sessionId=...`; responses arrive as SSE `message` events; keepalive every 15 s.
- Security: bound to `127.0.0.1`, Origin restricted to localhost, 4 MB request limit.

## 5. Resources and prompts

Resources: `impedance://catalog`, `impedance://knowledge`, `impedance://status`.

Prompts: `design_match`, `explain_topology`, `troubleshoot`.

## 6. Library and documentation tools

- `search_textbooks`: full-text/fuzzy search with title, page, snippet, rectangles and thumbnail URL.
- `read_textbook_page`: page text, OCR lines and translation; may request a visual crop.
- `translate_textbook_page`: cached academic translation.
- `search_docs`: all four documentation domains.
- `get_code_reference`: AST-generated signature and description for a module or function.

Every tool returns `ok` and `summary`; failures include `error_code`, `message` and `hint`.

## 7. Error codes

`-32700` parse error, `-32600` invalid request, `-32601` method not found, `-32602` invalid params, `-32603` internal error, `-32000` unknown/expired session, plus `bad_arguments`, `unknown_tool`, `internal_error` for tool-level failures.

## 8. Live tool reference

The tables below are generated from the same `tools.TOOL_SPECS` used by the agent and MCP clients.
