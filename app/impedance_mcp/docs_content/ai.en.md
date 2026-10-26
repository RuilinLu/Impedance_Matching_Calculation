# AI Model Interface

The application is provider-agnostic. The user selects a provider, protocol and model, then supplies their own API key. The software translates the same tool/message format into either OpenAI-compatible or Anthropic Messages requests.

## 1. Architecture

```
UI / floating assistant / MCP clients
        │
        ▼
agent.run_chat  ── tool loop, citations, usage aggregation
        │
        ▼
llm.chat  ── OpenAI-compatible / Anthropic Messages / custom URL
        │
        ▼
selected model provider (20 built-in catalog entries, updatable)
```

- `providers.json`: built-in public catalog (endpoints, model IDs, capabilities, reference prices, no keys).
- `data/catalog/providers_override.json`: user updates and manual edits, merged over the built-in catalog.
- `data/config.json`: active provider, protocol, model, key, model profile and UI settings.
- `data/usage.jsonl`: tokens, cache, cost and latency per request.

## 2. Built-in providers

OpenAI, Anthropic, Google Gemini, xAI, Mistral, Groq, OpenRouter, DeepSeek, Alibaba DashScope, Zhipu, Moonshot, Baidu Qianfan, Tencent Hunyuan, ByteDance Ark, MiniMax, 01.AI, StepFun, Baichuan, iFlytek Spark, SiliconFlow.

Each entry contains id, localized names, region, OpenAI base URL, optional Anthropic base URL, auth header, environment variable, documentation link and release-notes URL.

## 3. Protocols

### OpenAI-compatible

`POST {base}/chat/completions` with `Authorization: Bearer <key>`, `messages`, optional `tools`, `tool_choice`, `temperature`, `max_tokens`. Tool results are returned as `role="tool"` messages. Usage is read from `usage.prompt_tokens`, `completion_tokens`, `prompt_tokens_details.cached_tokens` and `completion_tokens_details.reasoning_tokens`.

### Anthropic Messages

`POST {base}/v1/messages` (or `/messages` when the base already ends with `/v1`) with `x-api-key` and `anthropic-version: 2023-06-01`. The system prompt is top-level; tools use `tool_use`/`tool_result` blocks; images use base64 `image` blocks. Usage includes `input_tokens`, `output_tokens`, `cache_read_input_tokens` and `cache_creation_input_tokens`.

### Custom URL

No path is appended. Use this for Azure OpenAI, gateways and reverse proxies; provide the complete endpoint and auth header.

## 4. Model profile

| Field | Meaning |
|---|---|
| `context` | context window in tokens |
| `max_output` | maximum output tokens |
| `vision` / `audio` | whether image/audio content may be sent |
| `tool_call` | function/tool calling |
| `json_output` | JSON mode |
| `reasoning` | thinking mode |
| `responses_api` / `anthropic_api` / `fim` | other capabilities |
| `pricing` | per-million-token prices by cache hit/miss and output, with optional peak/off-peak tables |
| `concurrency` | provider concurrency limit (reference) |
| `release` / `notes` | version date and restrictions |

Capabilities drive the UI, vision routing and cost calculation; they do not force a particular endpoint.

## 5. Pricing and usage

Prices are per 1,000,000 tokens. With `P` input tokens, `C` cached input tokens, `O` output tokens and prices `p_hit`, `p_miss`, `p_out`:

```
cost = [C × p_hit + (P − C) × p_miss + O × p_out] / 1,000,000
cache hit rate = C / P
context usage = P / context
```

If peak/off-peak tables exist, the local time and the provider's off-peak window select the price; automatic scheduling can be disabled in Settings.

### DeepSeek example

| Model | Context | Output | Thinking | Vision | Tools | Off-peak (CNY/M tokens) | Peak |
|---|---|---|---|---|---|---|---|
| `deepseek-flash` | 1M | 384K | yes | yes | yes | 0.02 hit / 1 miss / 4 output | 0.04 / 2 / 8 |
| `deepseek-v4-pro` | 1M | 384K | yes | no | yes | 0.15 / 4.5 / 13.5 | 0.30 / 9 / 27 |

Concurrency: 2500 and 500. Both support JSON output, tool calls, Responses API, Anthropic API and prefix completion; FIM is available in non-thinking mode only.

## 6. Vision

Enable “Image understanding” in the model profile. Images, scanned PDF pages and clipboard screenshots are attached as OpenAI `image_url` blocks or Anthropic base64 `image` blocks, together with any OCR text. Models without vision receive text only and the UI says so.

## 7. Tool loop

`agent.run_chat` runs at most five tool rounds: send system prompt, history and schemas; execute returned tool calls locally; return results as tool messages; continue until the model produces a final answer; aggregate usage. Tool results larger than 16 KB are truncated and marked. Textbook citations emit a separate `citation` event with a thumbnail and page-jump metadata.

## 8. Catalog updates

Sources: `https://models.dev/api.json`, the current provider's `GET {base}/models` (requires a valid key), and public model/pricing pages fetched over HTTPS.

Merge rules: match by provider id, append new models, preserve user-edited capabilities and prices, mark missing models as deprecated instead of deleting them, write an override file and keep a `.bak.json` backup.

AI-assisted update: fetch announcement text (about 20 KB per provider), ask the configured model for a strict JSON patch, validate the schema and numeric ranges, discard invalid entries, show a warning and keep rollback available.

## 9. Security

- Only `http/https`; resolve the host and reject loopback, private, reserved, link-local and multicast addresses.
- API keys stay in the local config file; the UI shows only the first/last four characters; logs never contain keys.
- Provider errors map to readable hints: 401 invalid key, 402 insufficient balance, 403 no permission, 404 wrong base/model, 429 rate limit.
- Textbooks and attachments are never uploaded automatically; only the conversation the user sends leaves the machine.
- Catalog updates read public pages only (the current provider's `/models` call uses its key).

## 10. Errors

| HTTP | Meaning | Action |
|---|---|---|
| 400 | bad request | check model id, tool schema, context length |
| 401 | invalid key | re-enter the key |
| 402 | insufficient balance | top up or switch provider |
| 403 | no permission | enable the model in the provider console |
| 404 | endpoint/model missing | check base URL and model id; switch protocol |
| 413 | payload too large | remove attachments or use a longer-context model |
| 429 | rate/concurrency limit | retry later; reduce concurrency |
| 5xx | provider outage | retry later; check status page |
