# MCP 协议接口

> 本软件同时是一个标准 MCP 服务器：同一套计算与教材检索工具既服务于内置智能体，也能被 ZCode、Claude Code、Codex、Cursor、Cherry Studio 等 MCP 客户端调用。

## 1. 启动

| 模式 | 命令 | 端点 |
|---|---|---|
| stdio | `python app/run_mcp.py` | 标准输入/输出，换行分隔 JSON-RPC |
| Streamable HTTP | `python app/run_mcp.py --http 8790` | `POST http://127.0.0.1:8790/mcp` |
| legacy HTTP+SSE | 同上 | `GET /sse` + `POST /messages?sessionId=...` |
| 健康检查 | 同上 | `GET /health` |

安装版使用同目录的 `ImpedanceMatchingAI_MCP.exe --mcp`，避免桌面窗口的 Windows 子系统吞掉 stdio。

## 2. 客户端配置

### ZCode / Claude Desktop

```json
{
  "mcp": {
    "servers": {
      "impedance-matching-ai": {
        "type": "stdio",
        "command": "python",
        "args": ["D:/path/to/app/run_mcp.py"],
        "env": {
          "PYTHONUNBUFFERED": "1",
          "PYTHONIOENCODING": "utf-8"
        }
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add impedance-matching-ai -- python D:/path/to/app/run_mcp.py
```

### HTTP 客户端

```json
{
  "mcpServers": {
    "impedance-matching-ai": {
      "type": "http",
      "url": "http://127.0.0.1:8790/mcp"
    }
  }
}
```

## 3. 协议版本

支持 `2024-11-05`、`2025-03-26`、`2025-06-18`；初始化时按客户端请求协商，未知版本回退到 `2025-06-18`。

服务器能力：`tools`、`resources`、`prompts`、`logging`。不支持批量 JSON-RPC、服务端主动采样与资源订阅。

## 4. 传输细节

### stdio

- 每行一个 JSON-RPC 消息；同时兼容 `Content-Length` 分帧。
- 只有 JSON-RPC 写入 stdout；日志写入 stderr。
- 收到 `shutdown`/`exit` 后结束进程。

### Streamable HTTP

- `POST /mcp`，可选 `Mcp-Session-Id`；首次 `initialize` 会返回新的会话 ID。
- `Accept: text/event-stream` 时返回单条 SSE 事件，否则返回 JSON。
- `DELETE /mcp` 结束会话。
- `GET /mcp` 返回 405（不支持服务端主动推送）。

### legacy SSE

- `GET /sse` 返回 `event: endpoint`，内容为 `/messages?sessionId=...`。
- 客户端把 JSON-RPC 发到该 endpoint；响应通过 SSE 的 `message` 事件返回。
- 每 15 秒发送一次 `: keepalive`。

### 安全

- 只绑定 `127.0.0.1`。
- 校验 `Origin`，只允许 `127.0.0.1`、`localhost`、`::1`。
- 请求体上限 4 MB。
- 不接受跨站写操作。

## 5. 资源

| URI | 内容 |
|---|---|
| `impedance://catalog` | 五种拓扑的适用条件、结构、公式 |
| `impedance://knowledge` | 内置微波匹配知识库（Markdown） |
| `impedance://status` | 版本、模型、MCP 与教材目录状态 |

## 6. 提示模板

| 名称 | 参数 | 用途 |
|---|---|---|
| `design_match` | `frequency_mhz`、`load`、`topology` | 生成一次完整匹配设计请求 |
| `explain_topology` | `topology` | 解释某种拓扑的原理与适用条件 |
| `troubleshoot` | `problem` | 排查无解、VSWR 偏高、带宽不足 |

## 7. 教材与文档工具

- `search_textbooks`：全库全文/模糊搜索，返回书名、页码、命中片段、矩形与缩略图 URL。
- `read_textbook_page`：读取指定页文字、OCR 行与译文；没有文字时可请求视觉截图。
- `translate_textbook_page`：按页翻译并缓存。
- `search_docs`：检索四类文档（功能、代码、AI 接口、MCP）。
- `get_code_reference`：按模块/函数名返回源码生成的签名与说明。

工具返回统一包含 `ok`、`summary`；失败时包含 `error_code`、`message`、`hint`。

## 8. 错误码

| code | 含义 |
|---|---|
| `-32700` | JSON 解析错误 |
| `-32600` | 非法请求 |
| `-32601` | 方法不存在 |
| `-32602` | 参数错误 |
| `-32603` | 服务器内部错误 |
| `-32000` | 会话不存在或已过期 |
| `bad_arguments` | 工具参数不是合法 JSON/对象 |
| `unknown_tool` | 工具名不存在 |
| `internal_error` | 工具执行异常 |

## 9. 工具参考

以下表格由 `tools.TOOL_SPECS` 实时生成，包含每个工具的参数、类型、必填项、默认值与枚举。工具数量、参数和内置智能体看到的 schema 完全一致。
