# MCP 客户端兼容性说明

**版本：v4.2.0 ｜ 更新日期：2026-10-26**

---

## 1. 先给结论

**MCP 是一个开放协议，不是所有 AI 软件都实现了它。**

- 支持 MCP 的客户端（Claude Code / Claude Desktop / Codex / ZCode / Cursor / Cherry Studio 等）可以通过标准配置加载本软件；
- 本身不支持 MCP 的聊天软件（例如某些旧版 Chatbox、DeepSeek 官方 App 的某些版本）**无法直接加载任何 MCP 服务器**——这是客户端能力问题，不是本服务器“协议不标准”；
- 本软件同时提供**独立运行界面**，不依赖 MCP：双击 `ImpedanceMCP.exe` 就能完成全部匹配计算、圆图、耐压和报告；
- 对于“任意 OpenAI 兼容模型”，本软件内置了 214 家国内外服务商目录，用户在设置里自己选择，不设默认厂商。

所以更准确的说法是：

> **本软件遵循通用 MCP 标准，并覆盖主流客户端的三种传输方式；但不能承诺“任何叫 AI 的软件都能直接适配”，因为有些软件根本没有 MCP 入口。**

---

## 2. 本软件实现的 MCP 标准

| 项目 | 实现 |
|---|---|
| 协议 | Model Context Protocol（JSON-RPC 2.0） |
| 协议版本 | 2024-11-05 / 2025-03-26 / 2025-06-18（按客户端请求回显） |
| 传输 1 | **stdio**（最通用，Claude Code / Codex / ZCode / Cursor / Claude Desktop） |
| 传输 2 | **Streamable HTTP**（`POST /mcp`，`Mcp-Session-Id`，支持 JSON 或 SSE 响应） |
| 传输 3 | **Legacy HTTP+SSE**（`GET /sse` + `POST /messages`，兼容 Cherry Studio / 旧版客户端） |
| 工具 | 15 个，JSON Schema 参数 |
| 资源 | 3 个（catalog / knowledge / status） |
| 提示模板 | 3 个（design_match / explain_topology / troubleshoot） |
| 会话 | Streamable HTTP 与 SSE 均分配 `Mcp-Session-Id` |
| 日志 | 只写 stderr，stdout 只输出协议 JSON |
| 安全 | 默认只监听 `127.0.0.1`；校验 Origin；不内置任何 API Key |

### 2.1 启动方式

```bat
:: 1) 独立运行（双击 exe 也可以）
ImpedanceMCP.exe

:: 2) stdio MCP（Claude Code / Codex / ZCode / Cursor）
ImpedanceMCP.exe --mcp

:: 3) Streamable HTTP + legacy SSE
ImpedanceMCP.exe --mcp --http 8790
```

源码方式：

```bat
python app\run_app.py            :: 独立运行
python app\run_mcp.py            :: stdio MCP
python app\run_mcp.py --http 8790 :: HTTP/SSE MCP
```

HTTP 端点：

- `POST http://127.0.0.1:8790/mcp`（Streamable HTTP）
- `GET http://127.0.0.1:8790/sse`（legacy SSE 握手）
- `POST http://127.0.0.1:8790/messages?sessionId=...`
- `GET http://127.0.0.1:8790/health`

---

## 3. 主流客户端适配矩阵

> “支持”指客户端自身提供 MCP 入口；具体菜单位置可能随版本变化。配置时把路径替换为你本机的实际路径。

| 客户端 | MCP 支持 | 推荐传输 | 配置方式 |
|---|---|---|---|
| **Claude Code** | 是 | stdio | `.mcp.json` 或 `claude mcp add` |
| **Claude Desktop** | 是 | stdio | `claude_desktop_config.json` |
| **OpenAI Codex CLI** | 是 | stdio | `~/.codex/config.toml` 的 `[mcp_servers.*]` |
| **ZCode** | 是 | stdio | `~/.zcode/cli/config.json` 的 `mcp.servers`（本机已写入） |
| **Cursor** | 是 | stdio | `.cursor/mcp.json` 或设置界面 |
| **Windsurf** | 是 | stdio | MCP 设置界面 |
| **Cherry Studio** | 是（较新版本） | stdio / SSE | 设置 → MCP 服务器 → 添加 |
| **Chatbox** | 取决于版本 | SSE / HTTP | 较新版本支持 MCP；旧版没有入口 |
| **DeepSeek 官方 App / Harness** | 取决于版本 | — | 若没有 MCP 入口则无法加载；请用独立界面或支持 MCP 的客户端 |
| **其他 MCP 客户端** | 是 | stdio 或 Streamable HTTP | 按客户端文档添加 |

> **“所有 AI 软件”并不现实**：MCP 是工具调用协议，不是所有聊天软件都实现了它；一个只支持 OpenAI Chat Completions 的客户端不会自动获得 MCP 工具。此时：
> - 用本软件的**独立界面**；
> - 或换用支持 MCP 的客户端（Claude Code / Codex / ZCode / Cursor / Cherry Studio 等）；
> - 本软件的**内置智能体**本身也支持任意 OpenAI 兼容 / Anthropic 模型，不依赖外部客户端。

---

## 4. 各客户端配置示例

### 4.1 Claude Desktop

文件：`%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "impedance-matching": {
      "command": "C:\\path\\to\\ImpedanceMCP.exe",
      "args": ["--mcp"]
    }
  }
}
```

### 4.2 Claude Code

推荐：

```bat
claude mcp add impedance-matching -- "C:\path\to\ImpedanceMCP.exe" --mcp
```

或项目根目录 `.mcp.json`：

```json
{
  "mcpServers": {
    "impedance-matching": {
      "command": "C:\\path\\to\\ImpedanceMCP.exe",
      "args": ["--mcp"]
    }
  }
}
```

### 4.3 OpenAI Codex CLI

文件：`~/.codex/config.toml`

```toml
[mcp_servers.impedance-matching]
command = "C:\\path\\to\\ImpedanceMCP.exe"
args = ["--mcp"]
startup_timeout_sec = 30
tool_timeout_sec = 120
```

### 4.4 ZCode

文件：`~/.zcode/cli/config.json`

```json
{
  "mcp": {
    "servers": {
      "impedance-matching": {
        "type": "stdio",
        "command": "C:\\path\\to\\ImpedanceMCP.exe",
        "args": ["--mcp"],
        "timeoutMs": 120000
      }
    }
  }
}
```

> 本机已把 Python 版写入该配置；重启 ZCode 后即可看到 `mcp__impedance-matching__*` 工具。

### 4.5 Cursor

项目根目录 `.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "impedance-matching": {
      "command": "C:\\path\\to\\ImpedanceMCP.exe",
      "args": ["--mcp"]
    }
  }
}
```

### 4.6 Cherry Studio

1. 先启动 HTTP/SSE 模式：
   ```bat
   ImpedanceMCP.exe --mcp --http 8790
   ```
2. 设置 → MCP 服务器 → 添加：
   - 类型：`SSE`
   - URL：`http://127.0.0.1:8790/sse`
3. 保存后应看到 15 个工具。

如果 Cherry Studio 当前版本只支持 stdio，也可以添加：
- 命令：`C:\path\to\ImpedanceMCP.exe`
- 参数：`--mcp`

### 4.7 Chatbox

Chatbox 的 MCP 支持随版本变化：

- 若设置里有 MCP Servers：添加 stdio（exe + `--mcp`）或 SSE（`http://127.0.0.1:8790/sse`）；
- 若没有 MCP 入口：该版本无法加载 MCP，请换用支持 MCP 的客户端，或使用本软件独立界面；
- 不要把“Chatbox 不支持 MCP”理解为“本服务器不兼容”——这是客户端功能差异。

### 4.8 纯 Python 方式（不想用 exe）

```json
{
  "mcpServers": {
    "impedance-matching": {
      "command": "C:\\Python314\\python.exe",
      "args": ["D:\\path\\to\\app\\run_mcp.py"],
      "env": {"PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"}
    }
  }
}
```

---

## 5. “模型”与“客户端”是两件事

很多用户会把“DeepSeek / Qwen / GLM / Claude / GPT”与“MCP 客户端”混在一起：

- **模型**：负责理解与生成；是否支持工具调用（tool calling）由模型/服务商决定；
- **客户端**：负责把工具描述发给模型、执行工具调用；MCP 是客户端与工具服务器之间的协议；
- **本软件**：既是独立工具，也是 MCP 服务器；它的内置智能体可以选择任意 OpenAI 兼容 / Anthropic 模型。

因此：

- 用 Claude Code / Codex / ZCode 时，模型是这些客户端自己的模型，本软件只提供 MCP 工具；
- 用本软件内置 AI 对话时，模型由你在设置里选择（214 家服务商之一，或自定义），本软件不内置任何厂商 Key；
- 只要模型支持 tool calling，内置智能体就能调用本软件的 15 个工具；不支持 tool calling 的模型仍可聊天，但不会自动调用工具。

---

## 6. 本软件内置的模型服务商目录

目录来自开源项目 **models.dev（github.com/sst/models.dev）**，共 **214 家**，包括：

- 国内：DeepSeek、阿里云百炼（通义千问）、智谱 GLM、月之暗面 Kimi、硅基流动、火山引擎方舟（豆包）、MiniMax、阶跃星辰、商汤 SenseNova、魔搭 ModelScope、腾讯 TokenHub 等；
- 国外：OpenAI、Anthropic Claude、Google Gemini、xAI Grok、Mistral、Groq、Cohere、Together AI、DeepInfra、Perplexity、OpenRouter、NVIDIA NIM、Fireworks 等；
- 自定义：任意 OpenAI 兼容服务（填写 Base URL / 模型 ID / Key）。

**没有默认服务商、没有默认模型、没有内置 Key。** 用户选择后自行填写自己的 API Key。

特殊适配：

- **Anthropic Claude**：使用 Messages 原生协议（本软件已适配工具调用）；
- **Azure OpenAI**：`api-key` 头 + 部署名 + `api-version`，Base URL 中替换 `<resource>` / `<deployment>`；
- **OpenAI 兼容**：其他厂商统一走 `/chat/completions`；
- **Google Gemini**：使用其 OpenAI 兼容端点；
- **Localhost/内网地址**：出于安全策略，模型服务 URL 不允许指向本机/内网；如需本地模型，请通过公网网关或反向代理。

---

## 7. 验证记录

| 项目 | 结果 |
|---|---|
| stdio initialize / tools/list / tools/call | 通过 |
| 精确 ZCode 配置命令启动 | 通过，15 个工具 |
| Streamable HTTP `POST /mcp` + `Mcp-Session-Id` | 通过 |
| SSE-only 响应 | 通过 |
| Legacy SSE `/sse` + `/messages` | 通过 |
| 独立 exe `--mcp` | 通过 |
| 独立 exe 双击运行（Web UI + 计算） | 通过 |
| Python 引擎 / MCP 协议回归 | 19/19 |

---

## 8. 故障排查

1. **客户端看不到工具**：
   - 先运行 `ImpedanceMCP.exe --mcp`，看终端是否报错；
   - 确认配置中的路径是绝对路径；
   - 重启客户端（大多数客户端只在启动时读取 MCP 配置）；
   - 查看客户端 MCP 日志。
2. **HTTP/SSE 连不上**：
   - 确认先启动了 `--mcp --http 8790`；
   - 浏览器访问 `http://127.0.0.1:8790/health`；
   - 端口被占用时换一个端口，并同步修改客户端 URL。
3. **模型 401/404/403**：
   - 401：Key 错误；
   - 404：Base URL / 模型 ID / Azure 部署名错误；
   - 403：Key 没有该模型权限；
   - 检查服务商控制台的模型开通情况。
4. **工具调用不触发**：
   - 模型可能不支持 tool calling；换一个支持工具调用的模型（如 DeepSeek Chat、GPT、Claude、Qwen 等）；
   - 本软件系统提示要求“先算后说”；如果模型仍不调用，直接在问题里说“请调用 design_matching_network 工具”。
5. **安全**：
   - MCP HTTP 只绑定 `127.0.0.1`；
   - 不要将 8790 端口暴露到公网；
   - API Key 只保存在本机 `data/config.json`（exe 为 `%LOCALAPPDATA%\ImpedanceMCP\data\config.json`）。

---

## 9. 结论

- **协议层面**：本软件遵循 MCP 标准，覆盖 stdio / Streamable HTTP / legacy SSE 三种传输和三个协议版本，工具描述使用标准 JSON Schema。
- **客户端层面**：Claude Code、Claude Desktop、Codex、ZCode、Cursor、Cherry Studio 等主流 MCP 客户端可以接入；具体配置格式不同，但协议一致。
- **不能保证**：所有叫“AI”的软件都能接入。没有 MCP 入口的客户端无法加载 MCP 服务器；这是客户端限制，不是服务器协议问题。
- **独立可用**：即使不接任何 AI 客户端，双击 exe 也能完整运行匹配设计、圆图、耐压和报告。

> 一句话：**MCP 是标准，但不是“万能插头”；本软件把标准该做的部分做全了，并把独立运行和 214 家模型服务商选择也做好了。**
