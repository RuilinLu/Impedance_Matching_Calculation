# Changelog

## v4.3.0 — 2026-10-26

### 新增
- **原生 Windows 窗口**：主程序改为 pywebview + WebView2，GUI 子系统，无控制台、无系统浏览器；帮助文档/报告在原生子窗口打开。
- **双 exe 打包**：`ImpedanceMCP.exe`（GUI）与 `ImpedanceMCP_MCP.exe`（console MCP）共享同一个 `_internal`，MCP stdio stdout 保持纯净。
- **一键彻底卸载**：开始菜单/可选桌面快捷方式 + `unins000.exe`；先关闭运行中进程，再删除所有用户数据、API Key、上传、报告、WebView2 缓存、MCP 条目、快捷方式与注册表项，不保留数据。
- **WebView2 自动安装**：安装器检测缺失时静默安装 Evergreen Runtime。
- 新增 `desktop.py`、`cleanup.py`，launcher 支持 `--browser` 调试回退与 `--cleanup`。

### 变更
- MCP 配置、界面复制配置、安装器 ZCode 写入统一指向 `ImpedanceMCP_MCP.exe`。
- 版本号 v4.3.0；安装包约 57 MB；便携 GUI 与便携 MCP 各约 34 MB。
- 文档、PDF、DOCX、帮助中心同步原生窗口与彻底卸载说明。

### 修复
- 卸载时运行中的 GUI/WebView2 锁定文件，导致安装目录或用户数据残留；现在卸载器先 `taskkill /F /T`，cleanup 带重试。
- 帮助中心中文文件名导致 HTTP `Content-Disposition` 非 latin-1、响应 500/截断；RFC 5987 ASCII 头 + 回归测试保持修复。

### 说明
- 32 位 Windows（x86 OS）不支持；需要 Windows 10/11 x64。
- 共享 Microsoft Edge WebView2 Runtime 是系统组件，不随本软件删除。

## v4.2.0 — 2026-10-26

### 新增
- **Windows 安装程序** `ImpedanceMCP_Setup_v4.2.0.exe`：检测 x64/磁盘/VC++/ZCode，自动补全 VC++，支持自定义安装目录、桌面/开始菜单快捷方式、可选写入 ZCode MCP 配置、安装后启动。
- **独立运行 + MCP 一体**：安装后的 `ImpedanceMCP.exe` 双击打开软件，`--mcp` 进 stdio，`--mcp --http 8790` 进 HTTP/SSE。
- **内置帮助中心**：用户手册、MCP 兼容性、计算正确性审计、技术白皮书、架构说明、比赛说明、安装与杀毒说明；安装目录 `docs` 同时提供 PDF。
- **计算正确性审计**：新增 ABCD 级联独立校验、正向扫描逐点反算、轨迹连续性、功率守恒、VSWR 关系测试；26/26 通过。
- 关于页/文档/安装程序加入作者联系方式：radarlurui@gmail.com、Lu_Skywalker2915@sjtu.edu.cn。
- 应用与安装程序加入版本信息、图标、许可证页；发布 `SHA256SUMS.txt`。
- 安装程序使用 **onedir** 载荷（非 onefile 自解压），降低杀毒误报；提供代码签名/误报处理指南。

### 修复
- 帮助中心中文文件名导致 HTTP `Content-Disposition` 非 latin-1、响应 500/截断；改用 RFC 5987 ASCII 头，并新增回归测试。

### 变更
- 版本号 v4.2.0；文档、PDF、DOCX、Release 同步。
- 安装后的用户数据仍保存在 `%LOCALAPPDATA%\ImpedanceMCP\data`。

### 说明
- 32 位 Windows（x86 OS）不支持；需要 Windows 10/11 x64。
- 杀毒软件误报无法用许可证消除；正确做法是代码签名、SHA-256、VirusTotal 信誉和误报提交，详见 `docs/安装与杀毒软件说明.md`。

## v4.1.0 — 2026-10-26

### 新增
- **214 家模型服务商目录**（来自开源项目 models.dev）：DeepSeek、OpenAI、Anthropic Claude、Google Gemini、阿里云百炼、智谱 GLM、Kimi、硅基流动、火山引擎方舟、MiniMax、阶跃星辰、商汤、腾讯 TokenHub、xAI、Groq、Mistral、Cohere、Together、OpenRouter、NVIDIA 等；**不设默认厂商/模型，不内置 Key**。
- **协议适配**：OpenAI 兼容、Anthropic Messages 原生、Azure OpenAI（`api-key` + 部署名 + `api-version`）。
- **MCP 三种传输**：stdio、Streamable HTTP（`/mcp` + `Mcp-Session-Id`）、legacy HTTP+SSE（`/sse` + `/messages`）。
- **独立 Windows exe**：双击运行独立界面；`--mcp` 运行 stdio MCP；`--mcp --http 8790` 运行 HTTP/SSE。
- **MCP 客户端兼容性说明**：Claude Code/Desktop、Codex、ZCode、Cursor、Cherry Studio、Chatbox 等配置示例与限制说明。
- 设置中「自定义模型 ID」，可填写任意新模型（如未来的 DeepSeek Flash）。

### 变更
- 默认配置改为空白：不预设任何厂商、Base URL、模型或 Key。
- 环境变量统一为通用 `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL`。
- 移除交大平台专用配置；不绑定任何校园网关。
- MCP 状态栏改为 `stdio / HTTP / SSE · 15 个工具`。

### 修复
- 修复 PyInstaller 冻结模式下数据目录写到临时目录的问题；exe 用户数据改存 `%LOCALAPPDATA%\ImpedanceMCP\data`。
- 修复 MCP HTTP 仅支持简单 POST 的问题，补齐 Streamable HTTP 会话与 legacy SSE。
- 修复切换服务商时可能复用旧 Key 的问题。

### 验证
- 独立 exe：双击启动 Web UI + 设计计算通过；`--mcp` 15 个工具通过。
- Streamable HTTP：initialize / tools/list / tools/call / DELETE 通过。
- Legacy SSE：endpoint / initialize / tools/list / notification 通过。
- Python 引擎 + MCP 协议回归 19/19；MATLAB 5/5；300 组随机设计 VSWR 1.000000。

## v4.0.0 — 2026-10-26

### 新增
- **MCP 标准服务**：stdio 与本地 HTTP 两种传输；15 个工具、3 个资源、3 个提示模板。
- **DeepSeek 智能体**：OpenAI 兼容工具调用、SSE 流式回答、PDF/DOCX/XLSX/PPTX/Notebook 附件解析。
- **现代化 Web 外壳**：AI 对话、五种拓扑设计、Smith 圆图动画、匹配范围扫描、带宽/灵敏度/耐压分析、报告导出。
- **Python 计算内核**：五种拓扑解析解 + 完整网络节点法复核；自动选值；自动拓扑比较。
- **MATLAB R2025b 复核**：`-batch` 独立复算；保留原版 `Impedance_Matching.exe` 启动入口。
- **工程文档**：README、用户手册、技术白皮书、比赛说明（MD/HTML/PDF）。

### 修复
- 修复原版 L 型（右）**正向扫描**中源端并联电容的共轭符号错误；旧代码使用 `1/(1/50 − jωC1)` 且未取共轭。
- 统一 S11 显示：低于 −60 dB 时显示“< −60 dB（理想）”，避免出现 −321 dB 这类无意义数值。
- 报告导出使用界面上的精确 C1/C2，避免因 L 四舍五入导致报告与界面不一致。
- 元件耐压界面区分“输入峰值电压”和“源开路电压”，避免把 2× 源电压误读为节点电压。
- 原版 MATLAB `mw_design.m` 函数文件名与函数名不一致导致 `-batch` 调用失败；已重命名并验证。
- 修复多页面图表在隐藏时尺寸为 0、切换后不重绘的问题。

### 验证
- Python 引擎 8 项回归测试通过；300 组随机用例 VSWR 全部为 1.000000。
- MATLAB R2025b 交叉验证 5/5 通过，Zin 偏差 0.0。
- MCP 协议测试 11/11 通过。
- 浏览器逐页视觉检查：AI、设计、圆图分析、耐压、设置、关于、报告。

## v3.0 — 2025-12-30（原版）
- 基于 MATLAB App Designer R2023b 的五种拓扑匹配计算、Smith 圆图动画、耐压分析、独立说明书子 App。
- 通过 MATLAB Application Compiler 打包为 `Impedance_Matching.exe`。
- 提供 `MyAppInstaller_mcr.exe`（内置 Runtime）与便携版 exe。
