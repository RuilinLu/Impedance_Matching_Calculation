# 智配芯生 · ImpedanceMCP

**微波阻抗匹配智能计算与仿真软件 · v4.0.0**

把「Smith 圆图 + L/T/π 匹配网络 + DeepSeek 智能体 + MCP 标准接口」放进同一个桌面外壳：
既能像传统射频软件一样精确算元件，也能让 ZCode / Claude / 任意 MCP 客户端直接调用你的仿真能力。

> 上海交通大学集成电路学院（信息与电子工程学院）
> “智绘芯生，AI 赋能” AI 教与学活动周 · 赛道一（AI 智能体）
> 开发者：**卢瑞林、卢柯吉、林芷伊、张昀蕾** ｜ 更新日期：**2026-10-26**

![设计界面](docs/assets/screenshot_design.png)

---

## 1. 这是什么

原有软件是基于 MATLAB App Designer 的微波阻抗匹配计算器（`Impedance_Matching.exe`，V3.0）。
V4.0 **保留原 exe 作为经典计算内核**，并在外面增加了一层完整的智能外壳：

| 层 | 内容 |
|---|---|
| 表现层 | 现代化 Web UI：AI 对话、Smith 圆图动画、五种拓扑、带宽/灵敏度/耐压、报告 |
| 智能体层 | DeepSeek 工具调用、PDF/DOCX/XLSX 附件解析、本地微波知识库 |
| 协议层 | **MCP（Model Context Protocol）stdio / HTTP**，15 个工具、3 个资源、3 个提示模板 |
| 计算层 | Python 计算内核（默认，毫秒级）+ MATLAB R2025b 批处理复核 + 原版 `Impedance_Matching.exe` |

这意味着它不再只是一个“点按钮出结果”的程序，而是可以被智能体调用的**微波仿真 MCP 服务器**。

---

## 2. 核心亮点

- **15 个 MCP 工具**：设计、正向扫描、网络复核、阻抗/导纳换算、耐压、带宽、拓扑对比、知识库、校验、报告、启动原版 exe、状态查询、预设。
- **五种拓扑**：L 型（左/右）、T 型、π 型Ⅰ/Ⅱ；支持 `topology="auto"` 自动比较选优。
- **解析解 + 节点法双重校验**：每个设计都会用完整网络节点分析重新计算 `Zin / VSWR / S11`，不是“只套公式”。
- **Smith 圆图动画**：串联沿等电阻圆、并联沿等电导圆，逐步演示负载 → 源端的匹配路径。
- **工程分析**：VSWR<2 带宽、±5% 元件容差灵敏度、峰值电压/电流应力、安全系数。
- **AI 智能体**：自然语言提问 → 自动调用本地工具 → 用微波工程语言解释结果；支持附件。
- **报告导出**：一键生成 HTML / Markdown 报告（含圆图、带宽、灵敏度、风险）。
- **离线可用**：除 DeepSeek 对话外，所有计算、绘图、MCP 工具均在本机运行，不需要联网。

![AI 智能体](docs/assets/screenshot_agent.png)

---

## 3. 安装与启动

### 3.1 使用新版智能外壳（推荐）

需要：

- Windows 10/11
- Python **3.10+**（本项目在 Python 3.14 上开发与测试）
- Python 包：`numpy`
- 可选：`pypdf`（PDF 附件）、`openpyxl`（XLSX 附件）、`Pillow`（图片尺寸）

```bat
pip install numpy pypdf openpyxl Pillow
start_app.bat
```

启动后浏览器会自动打开 `http://127.0.0.1:8765/`。
如果端口被占用，程序会自动尝试 8766–8776。

### 3.2 使用原版 MATLAB 软件（经典界面）

原版 `Impedance_Matching.exe` 由 MATLAB R2023b 编译，运行需要：

1. **`VC_redist.x64.exe`**（Visual C++ 运行库）
2. **MATLAB Runtime R2023b Update 10**

两种安装方式：

- **方式 A（推荐，最省事）**：直接安装
  `APP_Release_Release_Version/Main_Installation/MyAppInstaller_mcr.exe`。
  **这个安装包已经内置 MATLAB Runtime**（工程配置 `package.mcr=true`），安装它即可，不需要再单独装 Runtime。
- **方式 B（便携 exe）**：如果只想用
  `.../for_redistribution_files_only/Impedance_Matching.exe`，
  则需要先安装 `Problem_Solution/VC_redist.x64.exe` 和
  `Problem_Solution/MATLAB_Runtime_R2023b_Update_10_win64.zip` 中的 Runtime。

> 新版智能外壳的 **Python 计算内核不依赖 MATLAB Runtime**；Runtime 只影响“打开原版 exe”和“MATLAB R2025b 复核”两个功能。

### 3.3 配置 DeepSeek

打开右上角「设置」：

- 服务预设：`上海交大模型平台` 或 `DeepSeek 官方`
- 模型：`deepseek-chat`（默认，支持工具调用）/ `deepseek-reasoner`
- API Key：只保存在本机 `data/config.json`，不会写入仓库
- 点击「测试连接」验证

也可以使用环境变量（优先级高于配置文件）：

```bat
set DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
set DEEPSEEK_API_KEY=sk-...
```

交大平台：

```bat
set SJTU_LLM_BASE_URL=https://models.sjtu.edu.cn/api/v1
set SJTU_LLM_API_KEY=...
```

---

## 4. 接入 ZCode / 任意 MCP 客户端

### 4.1 ZCode

把下面这段加入 `~/.zcode/cli/config.json` 的 `mcp.servers`（本项目已为本机自动写入）：

```json
{
  "mcp": {
    "servers": {
      "impedance-matching": {
        "type": "stdio",
        "command": "C:\\Python314\\python.exe",
        "args": [
          "D:\\path\\to\\app\\run_mcp.py"
        ],
        "env": {
          "PYTHONUNBUFFERED": "1",
          "PYTHONIOENCODING": "utf-8"
        },
        "timeoutMs": 120000
      }
    }
  }
}
```

重启 ZCode 后，智能体就能看到 `mcp__impedance-matching__*` 工具。
可以直接对它说：

> 用 impedance-matching 工具设计 2.4 GHz、20+j5 Ω 的匹配网络，并分析 ±5% 容差和 10 W 耐压。

### 4.2 手动测试 MCP

```bat
python app\run_mcp.py
```

发送一行 JSON-RPC 即可（stdio，换行分隔）：

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

### 4.3 HTTP 模式（可选）

```bat
python app\run_mcp.py --http 8790
```

`POST http://127.0.0.1:8790/mcp`，JSON-RPC 2.0；`GET /health` 返回状态。
默认只监听 `127.0.0.1`，不对外网开放。

### 4.4 工具清单

| 工具 | 作用 |
|---|---|
| `design_matching_network` | 反向设计：拓扑/频率/负载 → L、C1、C2、C3、VSWR、带宽 |
| `scan_matching_range` | 正向扫描：固定 L/C3，遍历电容范围 → 可匹配的 R/X 区域 |
| `evaluate_network` | 节点法复核给定元件值的 Zin/VSWR/S11/功率 |
| `convert_impedance_admittance` | Z ↔ Y |
| `compute_voltage_stress` | 峰值电压、RMS 电流、安全系数 |
| `analyze_bandwidth` | VSWR 扫频与分数带宽 |
| `compare_topologies` | 五种拓扑可行性与带宽排序 |
| `get_topology_guide` | 拓扑原理、适用条件、公式 |
| `get_smith_trajectory` | 返回 Γ 平面轨迹采样点 |
| `search_knowledge` | 本地微波匹配知识库 |
| `validate_design` | 工程风险校验 |
| `export_design_report` | 生成 HTML/Markdown 报告 |
| `launch_classic_app` | 启动原版 `Impedance_Matching.exe` |
| `get_system_status` | 版本、LLM、MATLAB、exe 状态 |
| `list_presets` | 常用频段/负载预设 |

资源：`impedance://catalog`、`impedance://knowledge`、`impedance://status`。
提示模板：`design_match`、`explain_topology`、`troubleshoot`。

---

## 5. 使用界面

### 5.1 AI 智能体

- 直接用自然语言描述负载与频率，智能体会调用工具并把结果渲染成元件卡片。
- 支持附件：`.txt/.md/.csv/.json/.pdf/.docx/.xlsx/.pptx/.ipynb/.py/.m` 等（单文件 ≤25 MB）。
- 右侧“当前设计上下文”会同步最近一次设计的元件值、VSWR、带宽和圆图缩略图。
- 工具调用过程可见：每个工具卡会显示名称、耗时、摘要和可展开的原始返回。

### 5.2 匹配设计

- 选择拓扑（或“自动”），输入频率、Z0、负载 R/X。
- 打开“自动选值”时，软件会自动选择可行的 L 与 C3；关闭后可手动指定。
- 点击「求解设计」得到解析解；右侧同时给出节点法复核的 `Zin`、`VSWR`、`S11`。
- Smith 圆图支持播放/暂停/重置/速度调节；步骤列表可点击跳到对应路径。
- 下方展示带宽曲线、±5% 灵敏度、元件表、工程提示、可选拓扑对比。
- 「MATLAB 复核」会调用 MATLAB R2025b 批处理，独立复算一次（约 15–20 秒）。
- 「扫描范围」会跳到圆图分析页并自动运行正向扫描。

![圆图分析](docs/assets/screenshot_analysis.png)

### 5.3 耐压分析

- 输入功率、额定电压，点击「从当前设计填入」可复用设计结果。
- 表格给出各元件峰值电压、RMS 电压、峰值电流、RMS 电流和安全系数。
- 柱状图按安全系数着色：绿色 ≥2，黄色 ≥1.3，红色 <1.3。

![耐压分析](docs/assets/screenshot_stress.png)

### 5.4 报告

点击右上角「导出报告」生成 HTML；在浏览器中 `Ctrl+P` 可另存为 PDF。
报告包含：设计任务、拓扑图、元件表、节点法复核、Smith 圆图、带宽曲线、步骤、灵敏度、风险提示、团队信息。

![报告](docs/assets/screenshot_report.png)

---

## 6. 计算模型

### 6.1 网络与节点法

每个拓扑都被展开成无损集总网络，用节点电压法求解：

```
Y · V = I
```

源用 50Ω Thevenin 等效（`Vs = sqrt(8·P·50)`），负载为 `Z_L`。
由 `Zin = V_s / I_in` 得到输入阻抗，再计算：

```
Γ = (Zin − Z0) / (Zin + Z0)
VSWR = (1 + |Γ|) / (1 − |Γ|)
S11(dB) = 20 log10 |Γ|
```

元件电压/电流由节点电压直接得到，因此耐压分析包含源阻抗的负载效应，而不是简单分压估算。

### 6.2 五种拓扑

| 拓扑 | 结构 | 适用 |
|---|---|---|
| L 型（右） | 源 — 并联 C1 — 串联 L+C2 — 负载 | `R_L < Z0` |
| L 型（左） | 源 — 串联 L+C2 — 并联 C1 — 负载 | `R_L > Z0` |
| T 型 | 源 — 串 C3 — 节点（并 L+C2）— 串 C1 — 负载 | 需要中间节点调节/带宽 |
| π 型Ⅰ | 源 — 并 C3 — 串 L+C2 — 并 C1 — 负载 | C-L-C 结构 |
| π 型Ⅱ | 源 — 并 C1 — 串 L+C2 — 并 C3 — 负载 | 低阻负载 |

公式与推导见 [`docs/技术白皮书.md`](docs/技术白皮书.md)。

### 6.3 自动选值

当用户不指定 L/C3 时，软件按可行性条件选取实用值：

- L 型：由 `denom = ωL + d0 > 0` 反推最小 L，再取 1.5× 裕量。
- T 型：令中间虚拟电阻 `R_v ≈ max(1.8R_L, 75Ω)`，反解 C3。
- π 型Ⅰ：令源端等效电阻 `R_S ≈ min(0.45R_par, 40Ω)`，反解 C3。
- π 型Ⅱ：令负载并联 C3 后的等效电阻 `R_eff ≈ min(0.45R_par, 25Ω)`，反解 C3。

如果负载落在固定电容拓扑的物理不可行区（例如强容性负载），会返回明确的 `ok=false`、物理原因和替代拓扑建议。

---

## 7. 正确性验证

### 7.1 随机用例

`app/tests/test_engine.py` 对 5 种拓扑、多个频段、随机负载做设计 + 节点法复核：

```text
Ran 8 tests ... OK
```

所有成功设计的 `VSWR < 1.001`，`|Zin − 50| < 0.01 Ω`。

### 7.2 MATLAB R2025b 交叉验证

同一组设计分别用 Python 与 MATLAB R2025b 计算：

```text
MATLAB 交叉验证：5/5 通过
l_right  pass  py 1.000000  ml 1.000000  dz 0.0
l_left   pass  py 1.000000  ml 1.000000  dz 0.0
t        pass  py 1.000000  ml 1.000000  dz 0.0
pi1      pass  py 1.000000  ml 1.000000  dz 0.0
pi2      pass  py 1.000000  ml 1.000000  dz 0.0
```

### 7.3 MCP 协议测试

`app/tests/test_mcp_protocol.py` 覆盖 initialize、tools/list、tools/call、resources、prompts、错误处理：

```text
Ran 11 tests ... OK
```

---

## 8. 目录结构

```text
.
├─ app/
│  ├─ impedance_mcp/
│  │  ├─ engine.py          # 计算内核（五种拓扑 + 节点法）
│  │  ├─ tools.py           # 15 个 MCP 工具
│  │  ├─ mcp_server.py      # MCP stdio / HTTP
│  │  ├─ agent.py           # DeepSeek 工具调用智能体
│  │  ├─ llm.py             # OpenAI 兼容客户端
│  │  ├─ attachments.py     # PDF/DOCX/XLSX 附件解析
│  │  ├─ reports.py         # HTML/Markdown 报告
│  │  ├─ matlab_bridge.py   # MATLAB R2025b / 原版 exe
│  │  ├─ config.py          # 配置与路径
│  │  ├─ knowledge.py       # 本地知识库
│  │  └─ web/               # 前端（index.html/styles.css/app.js/smith.js）
│  ├─ matlab/
│  │  ├─ mw_design.m        # MATLAB 解析解 + 节点法复核
│  │  ├─ mw_batch_entry.m   # -batch 批处理入口
│  │  └─ original_v3/       # V3 原版 App Designer 提取源码
│  ├─ tests/
│  ├─ run_app.py
│  └─ run_mcp.py
├─ docs/                    # 用户手册、技术白皮书、比赛说明（MD/HTML/PDF）
├─ APP_Release_Release_Version/  # 原版安装包、Runtime、问题解决文件
├─ start_app.bat
├─ start_mcp.bat
├─ README.md
├─ CHANGELOG.md
└─ LICENSE
```

---

## 9. 常见问题

**Q：`MyAppInstaller_mcr.exe` 是否包含 MATLAB Runtime？**
A：包含。工程配置里 `package.mcr=true`，这是 MATLAB Compiler 的“打包 Runtime”安装包，直接安装即可。
`for_redistribution_files_only/Impedance_Matching.exe` 是便携版，需要单独安装 Runtime。

**Q：新版外壳为什么还需要 MATLAB？**
A：不需要。默认 Python 内核完成全部计算；MATLAB 只用于“复核”和“打开原版 exe”。没有 MATLAB 也能使用所有 MCP 工具和 AI 对话。

**Q：DeepSeek 报 401 / 404？**
A：检查 API Key、Base URL 和模型 ID。交大平台用 `https://models.sjtu.edu.cn/api/v1` + `deepseek-chat`；官方用 `https://api.deepseek.com/v1`。

**Q：设计返回“无解”或 C2 为负？**
A：这是物理限制，不是程序错误。固定电容拓扑无法匹配强容性/强感性负载；换 `topology="auto"` 或改用文中建议的拓扑。

**Q：C2 只有 0.00x pF？**
A：说明手动指定的 L 太大。打开“自动选值”，或把 L 减小到 1–10 nH 量级。

**Q：ZCode 看不到工具？**
A：确认 `~/.zcode/cli/config.json` 的 `mcp.servers` 中有 `impedance-matching`，路径存在，然后重启 ZCode。可先用 `python app/run_mcp.py` 手动验证。

---

## 10. 团队

| 成员 | 分工 |
|---|---|
| **卢瑞林** | 项目负责人 · 算法与 MCP 架构 |
| **卢柯吉** | MATLAB 计算内核与仿真验证 |
| **林芷伊** | 交互设计、可视化与文档 |
| **张昀蕾** | 测试、演示与用户研究 |

上海交通大学集成电路学院（信息与电子工程学院）
“智绘芯生，AI 赋能” AI 教与学活动周 · 2026-10-26

---

## 11. 许可与致谢

- 代码：MIT License（见 `LICENSE`）
- 原版 MATLAB App Designer 软件、`Impedance_Matching.exe` 及相关图片：由本项目团队开发，版权归团队所有。
- 感谢 MathWorks 提供的 MATLAB R2025b 与 App Designer / RF Toolbox 生态。
- 比赛介绍页面版权归上海交通大学集成电路学院所有，本仓库仅作学习与参赛说明引用。

> 本软件用于教学、科研与工程估算；正式产品请用实际元件模型、网络分析仪与实测数据复核。
