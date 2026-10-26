# 智配芯生 · ImpedanceMCP v4.1.0

**发布日期：2026-10-26** ｜ **赛道一 · AI 智能体** ｜ 上海交通大学集成电路学院（信息与电子工程学院）
**开发者：卢瑞林、卢柯吉、林芷伊、张昀蕾**

---

## 一、这次更新的核心

v4.1.0 把 v4.0.0 的“DeepSeek 单厂商 + stdio MCP”升级为：

> **独立可运行软件 + 标准 MCP 服务器 + 214 家国内外模型服务商可选。**

具体：

1. **不再默认使用任何厂商**（包括 DeepSeek）：设置里第一项永远是“请选择模型服务商”，用户自己选厂商、模型、填自己的 Key。
2. **内置 214 家服务商目录**（来自开源项目 models.dev）：
   - 国内：DeepSeek、阿里云百炼（Qwen）、智谱 GLM、Kimi、硅基流动、火山引擎方舟（豆包）、MiniMax、阶跃星辰、商汤、魔搭、腾讯 TokenHub 等；
   - 国外：OpenAI、Anthropic Claude、Google Gemini、xAI、Mistral、Groq、Cohere、Together、DeepInfra、Perplexity、OpenRouter、NVIDIA、Fireworks 等；
   - 自定义：任意 OpenAI 兼容服务。
3. **DeepSeek Flash 已在目录中**：选择“DeepSeek 深度求索”可看到 `deepseek-flash`、`deepseek-v4-flash`、`deepseek-v4-pro` 等模型。
4. **MCP 三种传输**：stdio、Streamable HTTP、legacy HTTP+SSE。
5. **独立 Windows exe**：双击运行完整界面；`--mcp` 运行 MCP；`--mcp --http 8790` 运行 HTTP/SSE。

---

## 二、MCP：协议与客户端兼容性

### 2.1 实现的协议

- JSON-RPC 2.0；
- 协议版本：2024-11-05 / 2025-03-26 / 2025-06-18；
- 15 个工具、3 个资源、3 个提示模板；
- `Mcp-Session-Id` 会话；
- 日志只写 stderr，stdout 只输出协议 JSON；
- 只监听 `127.0.0.1`，校验 Origin。

### 2.2 三种传输

| 传输 | 启动 | 客户端 |
|---|---|---|
| stdio | `ImpedanceMCP.exe --mcp` | Claude Code / Claude Desktop / Codex / ZCode / Cursor |
| Streamable HTTP | `--mcp --http 8790` → `POST /mcp` | 支持 HTTP 的客户端 |
| legacy HTTP+SSE | `--mcp --http 8790` → `GET /sse` | Cherry Studio / 旧版 MCP 客户端 |

### 2.3 客户端矩阵（摘要）

| 客户端 | MCP | 推荐传输 |
|---|---|---|
| Claude Code | 是 | stdio |
| Claude Desktop | 是 | stdio |
| OpenAI Codex CLI | 是 | stdio |
| ZCode | 是 | stdio |
| Cursor | 是 | stdio |
| Cherry Studio | 是（较新版本） | stdio / SSE |
| Chatbox | 取决于版本 | SSE / HTTP |
| DeepSeek 官方 App / Harness | 取决于版本 | 无 MCP 入口则无法加载 |

> **诚实说明**：MCP 是开放协议，但不是所有 AI 软件都实现了它。没有 MCP 入口的客户端无法加载任何 MCP 服务器，这是客户端限制，不是本服务器“协议不标准”。即使不接 MCP，双击 exe 也能独立运行完整功能。
>
> 完整配置与排查见 `docs/MCP兼容性说明.md`。

---

## 三、独立运行：它不只是 MCP

- 双击 `ImpedanceMCP_v4.1.0_Windows.exe`：打开独立 Web UI；
- 不连接 AI、不配置 MCP，也能完成五种拓扑设计、Smith 圆图、扫描、带宽、灵敏度、耐压、报告；
- 原版 `Impedance_Matching.exe` 仍保留，可从右上角「打开原版」启动；
- 源码方式：`pip install numpy pypdf openpyxl Pillow` + `start_app.bat`。

---

## 四、模型服务商配置（无默认）

设置 → 模型服务：

1. 选择服务商（214 家；常用在顶部）；
2. Base URL 自动填入；
3. 选择模型，或填写「自定义模型 ID」；
4. 填写你自己在厂商控制台申请的 API Key；
5. 点击「测试连接」。

**没有默认厂商、没有默认模型、没有内置 Key。**

特殊适配：

- **Anthropic Claude**：Messages 原生协议（已适配工具调用）；
- **Azure OpenAI**：`api-key` + 部署名 + `api-version`；
- **Google Gemini**：OpenAI 兼容端点；
- **其他**：OpenAI 兼容 `/chat/completions`。

环境变量（可选，仍然不设默认厂商）：

```bat
set LLM_BASE_URL=https://api.deepseek.com/v1
set LLM_API_KEY=sk-...
set LLM_MODEL=deepseek-chat
```

---

## 五、验证结果

| 测试 | 结果 |
|---|---|
| Python 引擎 + MCP 协议回归 | **19/19 通过** |
| 300 组随机设计 | **VSWR 全部 1.000000** |
| MATLAB R2025b 交叉验证 | **5/5 通过，Zin 偏差 0.0** |
| MCP stdio | initialize / tools/list / tools/call 通过 |
| Streamable HTTP | initialize / tools/list / tools/call / DELETE 通过 |
| Legacy SSE | endpoint / initialize / tools/list / notification 通过 |
| 独立 exe | 双击启动 Web UI + 设计计算通过；`--mcp` 15 个工具通过 |
| 浏览器 | AI / 设计 / 分析 / 耐压 / 设置 / 关于 / 报告逐页检查 |

---

## 六、安装

### 6.1 独立软件

双击 `ImpedanceMCP_v4.1.0_Windows.exe`（约 32 MB，Release 附件）。
无需 Python；用户数据在 `%LOCALAPPDATA%\ImpedanceMCP\data`。

源码：`start_app.bat`，Python 3.10+。

### 6.2 原版 MATLAB 软件

- **安装包（推荐）**：`APP_Release_Release_Version/Main_Installation/MyAppInstaller_mcr.exe`。
  **已内置 MATLAB Runtime**（`package.mcr=true`），直接安装即可。
- **便携 exe**：需先装 `VC_redist.x64.exe` + `MATLAB_Runtime_R2023b_Update_10_win64.zip`。

> 新版独立软件 / MCP 的 Python 内核不依赖 MATLAB Runtime；Runtime 只影响“打开原版 exe”和“MATLAB R2025b 复核”。

---

## 七、本次修复

- 修复 PyInstaller 冻结模式数据目录写入临时目录的问题；exe 用户数据改存 `%LOCALAPPDATA%\ImpedanceMCP\data`。
- 修复 MCP HTTP 仅支持简单 POST 的问题，补齐 Streamable HTTP 会话与 legacy SSE。
- 修复切换服务商时可能复用旧 Key 的问题。
- 默认配置改为空白，不再预设任何厂商 / Base URL / 模型 / Key。
- 移除交大平台专用配置与文档；不绑定任何校园网关。
- 保留 v4.0.0 已修复的 L 型（右）正向扫描共轭、S11 显示、报告元件值、耐压输入电压等问题。

---

## 八、附件

- `ImpedanceMCP_v4.1.0_Windows.exe`：独立软件 + MCP（双击运行；`--mcp` 进 MCP）。
- `ImpedanceMCP_v4.1.0_Source.zip`：完整源码、文档、测试（不含大安装包/Runtime）。
- `User_Manual_v4.1.0.pdf`、`White_Paper_v4.1.0.pdf`、`Competition_Dossier_v4.1.0.pdf`、`MCP_Compatibility_v4.1.0.pdf`、`Installation_Guide_v4.1.0.pdf`。

> 974 MB 的 `MyAppInstaller_mcr.exe` 与 4.6 GB 的 Runtime ZIP 不放入 GitHub Release（体积限制），它们位于项目 `APP_Release_Release_Version` 目录，安装指南中有说明与下载链接。

---

## 九、团队

| 成员 | 分工 |
|---|---|
| **卢瑞林** | 项目负责人 · 算法与 MCP 架构 |
| **卢柯吉** | MATLAB 计算内核与仿真验证 |
| **林芷伊** | 交互设计、可视化与文档 |
| **张昀蕾** | 测试、演示与用户研究 |

上海交通大学集成电路学院（信息与电子工程学院）
“智绘芯生，AI 赋能” AI 教与学活动周 · 赛道一

> 本软件用于教学、科研与工程估算；正式产品请用实际元件模型与实测数据复核。
