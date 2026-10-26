# Impedance Matching AI v4.3.0

**发布日期：2026-10-27**
**开发者：卢瑞林、卢柯吉、林芷伊、张昀蕾**
**项目主页：** https://github.com/RuilinLu/Impedance_Matching_Calculation

一个独立运行的微波阻抗匹配、Smith 圆图、教材检索与 MCP 服务软件。本版本完成了从“比赛作品”到独立开源项目的重构，补齐安装器、卸载器、完整离线说明书、教材数据库与真实模型测试。

---

## 下载资产

| 资产 | 大小 | 说明 |
|---|---:|---|
| `Impedance_Matching_AI_v4.3.0_Setup.exe` | 约 175 MB | 完整安装程序：主程序 + MCP + 离线说明书 + 教材数据库 + VC++/WebView2 检测 |
| `Impedance_Matching_AI_v4.3.0_Portable.exe` | 约 172 MB | 免安装便携版 |
| `Impedance_Matching_AI_v4.3.0_MCP.exe` | 约 172 MB | 独立 MCP stdio / HTTP / SSE 服务 |
| `Impedance_Matching_AI_v4.3.0_Source.zip` | 约 6 MB | 干净源码（含说明书、安装器脚本、测试，不含教材/用户数据/API Key） |
| `SHA256SUMS.txt` | — | 下载校验 |

教材文件不随 Release 发布，用户可自行放入 `TextBook/`。

## 界面截图

![匹配设计](https://raw.githubusercontent.com/RuilinLu/Impedance_Matching_Calculation/main/docs/assets/screenshot_design.png)

![圆图分析](https://raw.githubusercontent.com/RuilinLu/Impedance_Matching_Calculation/main/docs/assets/screenshot_scan.png)

![教材库](https://raw.githubusercontent.com/RuilinLu/Impedance_Matching_Calculation/main/docs/assets/screenshot_library.png)

更多截图见仓库 `docs/assets/` 与安装目录 `docs/index.html`。

## 本版本重点

### 1. 安装器与卸载器

- Inno Setup 安装程序，按当前用户安装到 `%LOCALAPPDATA%\Programs\Impedance Matching AI`；
- 自动检测 VC++ 与 WebView2；
- 安装主程序、MCP 程序、离线说明书、MathJax、`TextBook/` 与教材数据库；
- 开始菜单/可选桌面快捷方式；
- 一键卸载：关闭进程，删除程序、用户数据、API Key、上传、报告、教材索引、MCP 客户端配置、快捷方式与注册表项；
- 已实测静默安装 → 启动 → 静默卸载，确认程序目录、用户数据、快捷方式与注册项全部清除。

### 2. 圆图分析与耐压单位修复

- 圆图分析/耐压分析的 L 单位统一为 **nH**，修复此前按 1.94 µH 解释 1.94 nH 导致的异常 X 范围（−29241…29097 Ω）与 VSWR 2,128,409；
- 修正后 L=1.939 nH、C1=1.624 pF、C2=6.803 pF 的结果为 VSWR≈1.0006、源峰值 31.6 V、负载峰值 20.6 V；
- 灰色密度云、外包络边界与青色近圆心高亮恢复正常显示；
- 运行扫描按钮、错误提示与旧结果保留逻辑同步修复。

### 3. 完整 LaTeX 渲染

- 内置离线 MathJax 3.2.2 `tex-svg-full`，不依赖 CDN；
- 支持 `$...$`、`\(...\)`、`$$...$$`、`\[...\]`、`align`、`cases`、矩阵、`\ce{}`、physics、boldsymbol 等；
- AI 回答、文档中心、离线说明书均渲染公式；
- 系统提示词要求“叙述性文本 + 大量 LaTeX 推导”，除非用户要求代码，否则不使用代码块回答；
- 已用 DeepSeek 实际 API 测试公式回答与浏览器渲染。

### 4. 教材库与数据库

- 本地 SQLite 索引：`%LOCALAPPDATA%\ImpedanceMatchingAI\data\library\index.sqlite3`；
- 支持 PDF、TXT、Markdown、TeX、DOCX、PPTX、XLSX、IPYNB，旧版 Office 尽量提取文本；
- 全文/模糊搜索、页码定位、命中矩形、页面渲染缩放；
- 扫描版 PDF 本地 RapidOCR，可单页或按页码范围 OCR；
- 学术翻译、引用缩略图与命中区域裁剪；
- 19 本中英文教材实测：2197 页可检索、36 页 OCR。

### 5. AI 智能体与模型设置

- 任意文件、剪贴板、拖拽、图片/扫描页视觉输入；
- 20 家国内外厂商；DeepSeek `deepseek-flash` / `deepseek-v4-pro` 完整能力与峰谷价格；
- 逐模型上下文、输出、视觉、工具、JSON、Reasoning、Responses/Anthropic API、FIM、并发、币种、谷时窗口；
- 对话统计：输入/输出 tokens、缓存命中率、上下文占用率、费用、峰谷时段；
- 默认最大输出 16384 tokens，并在思考模型输出截断时自动补全一次；
- 已用 DeepSeek 实际 API 测试连接、工具调用、LaTeX 回答、缓存命中率与费用统计。

### 6. 四域文档中心

- 软件功能、代码参考、AI 接口、MCP 协议；
- 逐字全文搜索、全部高亮、上一个/下一个匹配；
- 代码参考由 AST 实时生成，覆盖模块、函数、参数、返回、局部变量与前端函数；
- 安装目录 `docs/` 提供完整离线 HTML 说明书（含截图与 MathJax）。

### 7. 工程清理

- 完全移除 MATLAB / MATLAB Runtime / 原版 exe 支持；
- 删除旧比赛文档、旧安装包、旧 PDF、旧 MATLAB 工程与冗余目录；
- 品牌统一为 **Impedance Matching AI**；
- README、CHANGELOG、SECURITY、第三方许可证与安装说明全部重写为中英文。

## 测试

- **51 项单元测试全部通过**：计算内核、物理审计、MCP 协议、教材索引/OCR、DOCX 教材、任意附件、引用裁剪、模型目录/费用/谷时窗口、Web API、智能体工具循环、视觉消息。
- **真实 DeepSeek API**：连接、设计工具调用、LaTeX 长回答、缓存命中率约 88%、上下文占用与费用统计。
- **安装/卸载**：静默安装到测试目录，验证主程序、MCP、docs、TextBook、数据库、快捷方式、注册表；静默卸载后全部清除。
- **打包后**：MCP 握手、设计工具、教材索引/OCR、代码参考、MathJax 文档均正常。

## 说明

- 安装程序按当前用户安装；VC++/WebView2 缺失时引导程序可能请求管理员权限。
- 教材、模型 Key 与用户数据不包含在发布包中。
- 旧版本用户请先卸载旧版，再安装本版本；卸载会清理 API Key，请提前备份。
- PyMuPDF 为 AGPL-3.0，第三方许可证见 `THIRD_PARTY_NOTICES.md`。
