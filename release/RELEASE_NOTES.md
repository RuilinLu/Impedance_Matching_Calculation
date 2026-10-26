# 智配芯生 · ImpedanceMCP v4.2.0

**发布日期：2026-10-26** ｜ **赛道一 · AI 智能体** ｜ 上海交通大学集成电路学院（信息与电子工程学院）
**开发者：卢瑞林、卢柯吉、林芷伊、张昀蕾**
**联系：radarlurui@gmail.com ｜ Lu_Skywalker2915@sjtu.edu.cn**

---

## 一、v4.2.0 的核心：一个安装程序，两种使用模式

v4.2.0 把 v4.1.0 的“独立 exe + MCP”进一步做成 **可交付给普通用户的 Windows 安装程序**：

> **复制 `ImpedanceMCP_Setup_v4.2.0.exe` 到任意 Windows 10/11 x64 电脑 → 双击安装 → 桌面/开始菜单 `ImpedanceMCP` → 打开即用。**

安装后的 `ImpedanceMCP.exe` 同时是：

1. **独立软件**：双击打开匹配设计、Smith 圆图、扫描、耐压、报告；
2. **MCP 服务器**：`ImpedanceMCP.exe --mcp` 作为 stdio 服务，供 ZCode / Claude Code / Codex / Cursor 等调用；
3. **HTTP/SSE MCP**：`ImpedanceMCP.exe --mcp --http 8790`，供 Cherry Studio 等使用；
4. **内置 AI**：设置里选择 214 家服务商之一，填自己的 API Key，像 MATLAB Copilot 一样对话；
5. **外部 AI**：通过 MCP，让 Codex/ZCode 等调用本软件，像 MATLAB 的 MCP 连接 Codex。

---

## 二、安装程序能力

`ImpedanceMCP_Setup_v4.2.0.exe`（约 52 MB）：

- 检测 Windows 10/11 x64（32 位 Windows 会明确提示不支持）；
- 支持**自定义安装目录**；
- 可选**桌面快捷方式**、开始菜单、帮助文档快捷方式；
- 检测 **VC++ 运行库**，缺失时自动静默安装（仅原版经典界面需要）；
- 可选**为 ZCode 写入 MCP 配置**（自动备份原 `config.json`，保留其他 MCP 服务器）；
- 可选安装原版 MATLAB 经典界面（`classic\Impedance_Matching.exe`）；
- 安装完成可立即启动；
- 卸载保留 `%LOCALAPPDATA%\ImpedanceMCP\data` 用户数据。

> **新版 ImpedanceMCP 与 MCP 不需要 Python、不需要 MATLAB、不需要 Node.js。**
> 原版经典界面才需要 MATLAB Runtime R2023b；安装程序会检测并提示，不会强制下载 974 MB Runtime。

---

## 三、内置帮助中心（类似 MATLAB Help）

软件左侧新增「帮助文档」：

- 用户手册
- MCP 兼容性说明
- **计算正确性审计**
- 技术白皮书
- 软件架构说明
- 比赛说明文档
- 安装与杀毒软件说明

支持搜索、iframe 阅读、新标签打开、打印/另存 PDF。
安装目录 `docs` 同时提供 HTML 与 PDF，开始菜单也有帮助快捷方式。

---

## 四、计算正确性审计（重点）

新增 `app/tests/test_physics.py`，用**独立的 ABCD 级联矩阵**复核节点法，避免“同一个错误在两条公式里重复”：

| 测试 | 结果 |
|---|---|
| ABCD vs 节点法（5 拓扑随机） | 通过，误差 < 1e-8 |
| 正向扫描点逐点反算 | 通过，VSWR < 1.001 |
| Smith 轨迹连续性 / 终点 | 通过 |
| 功率守恒 / 输入峰值电压 | 通过 |
| VSWR 与 Γ 关系 | 通过 |
| Web 帮助 HTTP 头（中文文件名） | 通过 |
| **总测试** | **26/26 通过** |
| MATLAB R2025b 交叉 | 5/5，Zin 偏差 0.0 |
| 300 组随机设计 | VSWR 全部 1.000000 |

详细推导、边界与测试证据见 `docs/计算正确性审计.pdf`。

> 适用范围：理想无损集总参数网络。PCB 寄生、封装 ESL/ESR、SRF、微带不连续性和全波电磁场需实测/全波仿真复核；本软件不冒充全波求解器。

---

## 五、214 家模型服务商，无默认

- 目录来自开源项目 models.dev（214 家）；
- **不设默认厂商/模型/Key**；
- 国内：DeepSeek、阿里云百炼、智谱 GLM、Kimi、硅基流动、火山引擎方舟、MiniMax、阶跃星辰、商汤、魔搭、腾讯 TokenHub 等；
- 国外：OpenAI、Anthropic Claude、Google Gemini、xAI、Mistral、Groq、Cohere、Together、DeepInfra、Perplexity、OpenRouter、NVIDIA、Fireworks 等；
- 自定义：任意 OpenAI 兼容服务；
- DeepSeek 目录包含 `deepseek-flash`、`deepseek-v4-flash` 等；
- Anthropic 使用 Messages 原生适配；Azure 使用 `api-key` + 部署名。

---

## 六、MCP 兼容性

| 传输 | 入口 | 客户端 |
|---|---|---|
| stdio | `ImpedanceMCP.exe --mcp` | Claude Code / Claude Desktop / Codex / ZCode / Cursor |
| Streamable HTTP | `--mcp --http 8790` → `POST /mcp` | 支持 HTTP 的 MCP 客户端 |
| legacy HTTP+SSE | `--mcp --http 8790` → `GET /sse` | Cherry Studio / 旧版客户端 |

15 个工具、3 个资源、3 个提示模板；协议版本 2024-11-05 / 2025-03-26 / 2025-06-18。

**诚实说明**：MCP 是标准，但不是所有 AI 软件都实现了它。没有 MCP 入口的聊天软件无法加载任何 MCP 服务器；此时使用本软件的独立界面即可。详见 `docs/MCP兼容性说明.pdf`。

---

## 七、关于杀毒软件误报（重要）

**没有许可证可以阻止卡巴斯基/Windows Defender 误报。** MIT License 只是法律授权，不是白名单。

本版本已做的降低误报措施：

- 安装载荷使用 **PyInstaller onedir**（不是 onefile 自解压）；
- 不使用 UPX；
- exe 与安装程序带完整版本信息、图标、公司/产品/版权；
- 提供 `SHA256SUMS.txt` 供下载后校验；
- 不写启动项、不注入进程、不修改浏览器、不上传数据。

**真正有效的长期方案是代码签名**（OV/EV Authenticode 证书），签名安装程序与 `ImpedanceMCP.exe`，并使用时间戳。本仓库提供 `installer/sign_example.ps1` 模板，但**不包含证书**；没有证书就无法伪造受信任签名。

如果被杀毒软件隔离：

1. 从 GitHub Release 重新下载；
2. 用 `certutil -hashfile <文件> SHA256` 核对 `SHA256SUMS.txt`；
3. 在杀毒软件中恢复并加入排除（仅在哈希一致时）；
4. 向 Microsoft/Kaspersky/VirusTotal 提交误报。

详见 `docs/安装与杀毒软件说明.pdf`。

---

## 八、系统要求

- Windows 10/11 **x64**（x86_64）；
- 32 位 Windows（x86 OS）不支持：程序使用 64 位 Python/NumPy 运行时；
- 新版软件/MCP 不需要 Python、MATLAB、Node.js；
- AI 对话需要联网 + 用户自己的 API Key；
- 原版经典界面需要 VC++ 运行库 + MATLAB Runtime R2023b（安装程序自动装 VC++；Runtime 需另外安装）。

---

## 九、附件

- `ImpedanceMCP_Setup_v4.2.0.exe`：Windows 安装程序（推荐）
- `ImpedanceMCP_v4.2.0_Portable.exe`：便携版（可选）
- `ImpedanceMCP_v4.2.0_Source.zip`：完整源码与文档
- `User_Manual_v4.2.0.pdf`
- `White_Paper_v4.2.0.pdf`
- `Competition_Dossier_v4.2.0.pdf`
- `MCP_Compatibility_v4.2.0.pdf`
- `Calculation_Audit_v4.2.0.pdf`
- `Installation_And_Antivirus_v4.2.0.pdf`
- `SHA256SUMS.txt`

> 974 MB 的 `MyAppInstaller_mcr.exe` 与 4.6 GB 的 Runtime ZIP 不放入 GitHub Release（体积限制）；它们位于项目 `APP_Release_Release_Version` 目录，安装指南中有说明。

---

## 十、团队

| 成员 | 分工 |
|---|---|
| **卢瑞林** | 项目负责人 · 算法与 MCP 架构 |
| **卢柯吉** | MATLAB 计算内核与仿真验证 |
| **林芷伊** | 交互设计、可视化与文档 |
| **张昀蕾** | 测试、演示与用户研究 |

上海交通大学集成电路学院（信息与电子工程学院）
“智绘芯生，AI 赋能” AI 教与学活动周 · 赛道一

> 本软件用于教学、科研与工程估算；正式产品请用实际元件模型与实测数据复核。
