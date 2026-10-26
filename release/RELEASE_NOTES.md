# 智配芯生 · ImpedanceMCP v4.3.0

**发布日期：2026-10-26** ｜ **赛道一 · AI 智能体** ｜ 上海交通大学集成电路学院（信息与电子工程学院）
**开发者：卢瑞林、卢柯吉、林芷伊、张昀蕾**
**联系：radarlurui@gmail.com ｜ Lu_Skywalker2915@sjtu.edu.cn**

---

## 一、这一版解决两个核心问题

### 1. 真正“一个窗口打开”的桌面软件

v4.3.0 起，双击 `ImpedanceMCP.exe`：

- 打开的是 **原生 Windows 窗口**（标题栏、图标、任务栏、最小化/最大化/关闭）；
- **不弹命令行窗口**：主程序编译为 Windows GUI 子系统（PE subsystem 2）；
- **不调用 Edge/Chrome**：界面由内置 pywebview + Microsoft Edge WebView2 在窗口内渲染；
- 本地计算服务仍只监听 `127.0.0.1` 的随机空闲端口，窗口关闭即停止；
- 帮助文档和报告在原生子窗口打开，不跳出软件。

MCP 不再复用 GUI exe，而是独立的控制台程序：

```text
ImpedanceMCP.exe       原生窗口（GUI 子系统）
ImpedanceMCP_MCP.exe   MCP stdio / HTTP+SSE（console 子系统，stdout 纯净）
```

这样 GUI 可以彻底去掉控制台，MCP 又能保持标准输入/输出的 JSON-RPC 通信。安装器、ZCode 配置和界面“复制配置”都会自动指向 `ImpedanceMCP_MCP.exe`。

### 2. 一键彻底卸载，不保留任何用户数据

安装后提供：

- 开始菜单「一键卸载 ImpedanceMCP（清除全部数据）」；
- 可选桌面「一键卸载 ImpedanceMCP」快捷方式；
- 安装目录 `unins000.exe`。

卸载流程：

1. 先强制关闭正在运行的 `ImpedanceMCP.exe` / `ImpedanceMCP_MCP.exe`，避免 WebView2 缓存和 exe 被占用；
2. 调用 `ImpedanceMCP_MCP.exe --cleanup`；
3. 删除所有 Windows 用户的 `%LOCALAPPDATA%\ImpedanceMCP`、`%APPDATA%\ImpedanceMCP`；
4. 删除 API Key、上传、报告、WebView2 用户缓存；
5. 删除 ZCode / Claude / Codex / Cursor 配置中的 `impedance-matching` 条目，**保留其他 MCP 服务器**；
6. 删除开始菜单/桌面快捷方式、应用注册表项、Windows“应用和功能”卸载项；
7. 由 Inno 删除安装目录。

**不保留任何用户数据。** 共享的 Microsoft Edge WebView2 Runtime 属于系统组件，不随本软件删除，以免影响其他应用。

---

## 二、安装程序

`ImpedanceMCP_Setup_v4.3.0.exe`（约 57 MB）：

- 检测 Windows 10/11 x64、磁盘空间、VC++ 运行库；
- 检测 Microsoft Edge WebView2 Runtime，缺失时自动静默安装；
- 支持自定义安装目录；
- 可选桌面/开始菜单快捷方式；
- 可选一键卸载桌面快捷方式；
- 可选为 ZCode 写入 MCP 配置（自动备份原配置）；
- 可选安装原版 MATLAB 经典界面；
- 安装完成可立即启动。

新版 `ImpedanceMCP.exe` 与 MCP **不需要 Python、MATLAB、Node.js**。
原版经典界面才需要 MATLAB Runtime R2023b；安装程序会检测并提示，不会强制下载 974 MB Runtime。

---

## 三、计算与 MCP 能力保持不变并重新验证

| 项目 | 结果 |
|---|---|
| Python 全量回归测试 | **29/29 通过** |
| ABCD 级联 vs 节点法 | 通过，误差 < 1e-8 |
| 300 组随机设计 | VSWR 全部 1.000000 |
| MATLAB R2025b 交叉 | 5/5 通过，Zin 偏差 0.0 |
| MCP stdio | 15 个工具，initialize / tools/list / tools/call 通过 |
| MCP Streamable HTTP | `POST /mcp` + `Mcp-Session-Id`，15 个工具通过 |
| 214 家服务商 | 无默认厂商/模型/Key，用户自行选择 |
| 原生窗口 | 1440×900 加载 AI/设计/分析/耐压/帮助/关于页面 |
| 一键卸载 | 运行中程序、程序目录、数据、MCP 配置、注册表、快捷方式全部清除 |

计算范围仍是**理想无损集总参数网络**：PCB 寄生、封装 ESL/ESR、SRF、微带不连续性和全波效应需实测或全波仿真复核。本软件不冒充全波求解器。

---

## 四、MCP 兼容性

| 传输 | 入口 | 客户端 |
|---|---|---|
| stdio | `ImpedanceMCP_MCP.exe --mcp` | Claude Code / Claude Desktop / Codex / ZCode / Cursor |
| Streamable HTTP | `--mcp --http 8790` → `POST /mcp` | 支持 HTTP 的 MCP 客户端 |
| legacy HTTP+SSE | `--mcp --http 8790` → `GET /sse` | Cherry Studio / 旧版客户端 |

**诚实说明**：MCP 是标准，但不是所有 AI 软件都实现了它。没有 MCP 入口的聊天软件无法加载任何 MCP 服务器；此时使用本软件的原生窗口即可。

---

## 五、杀毒软件与签名

**没有许可证可以阻止卡巴斯基/Windows Defender 误报。** MIT License 只是法律授权，不是白名单。

本版本的措施：

- GUI 安装载荷使用 PyInstaller onedir（不是 onefile 自解压）；
- 不使用 UPX；
- exe 与安装程序带完整版本信息、图标、公司/产品/版权；
- 提供 `SHA256SUMS.txt` 供下载后校验；
- 不写启动项、不注入进程、不修改系统浏览器、不上传数据。

真正有效的长期方案是代码签名（OV/EV Authenticode 证书），签名安装程序与两个 exe，并使用时间戳。仓库提供 `installer/sign_example.ps1` 模板，但不包含证书。

---

## 六、系统要求

- Windows 10/11 **x64**（x86_64）；
- 32 位 Windows（x86 OS）不支持：程序使用 64 位 Python/NumPy 运行时；
- 新版软件/MCP 不需要 Python、MATLAB、Node.js；
- 原生窗口需要 Microsoft Edge WebView2 Runtime（安装器自动安装）；
- AI 对话需要联网 + 用户自己的 API Key；
- 原版经典界面需要 VC++ 运行库 + MATLAB Runtime R2023b。

---

## 七、附件

- `ImpedanceMCP_Setup_v4.3.0.exe`：Windows 安装程序（推荐）
- `ImpedanceMCP_v4.3.0_Portable.exe`：原生窗口便携版
- `ImpedanceMCP_v4.3.0_Portable_MCP.exe`：便携版 MCP 控制台
- `ImpedanceMCP_v4.3.0_Source.zip`：完整源码与文档
- `User_Manual_v4.3.0.pdf`
- `White_Paper_v4.3.0.pdf`
- `Competition_Dossier_v4.3.0.pdf`
- `MCP_Compatibility_v4.3.0.pdf`
- `Calculation_Audit_v4.3.0.pdf`
- `Installation_And_Antivirus_v4.3.0.pdf`
- `SHA256SUMS.txt`

> 974 MB 的 `MyAppInstaller_mcr.exe` 与 4.6 GB 的 Runtime ZIP 不放入 GitHub Release（体积限制）；它们位于项目 `APP_Release_Release_Version` 目录，安装指南中有说明。

---

## 八、团队

| 成员 | 分工 |
|---|---|
| **卢瑞林** | 项目负责人 · 算法与 MCP 架构 |
| **卢柯吉** | MATLAB 计算内核与仿真验证 |
| **林芷伊** | 交互设计、可视化与文档 |
| **张昀蕾** | 测试、演示与用户研究 |

上海交通大学集成电路学院（信息与电子工程学院）
“智绘芯生，AI 赋能” AI 教与学活动周 · 赛道一

> 本软件用于教学、科研与工程估算；正式产品请用实际元件模型与实测数据复核。
