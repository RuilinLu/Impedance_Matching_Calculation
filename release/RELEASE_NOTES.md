# 智配芯生 · ImpedanceMCP v4.0.0

**发布日期：2026-10-26** ｜ **赛道一 · AI 智能体** ｜ 上海交通大学集成电路学院（信息与电子工程学院）
**开发者：卢瑞林、卢柯吉、林芷伊、张昀蕾**

---

## 一、这次发布做了什么

在原有 MATLAB App Designer 软件（V3.0，`Impedance_Matching.exe`）的基础上，V4.0 完成了一次“智能外壳 + MCP 服务”的升级：

- **保留经典内核**：原版 exe、L/T/π 五种拓扑、Smith 圆图动画、耐压分析全部保留；
- **新增 Python 计算内核**：解析解 + 完整网络节点法复核，毫秒级，无 MATLAB 也能运行；
- **新增 MCP 标准服务**：15 个工具、3 个资源、3 个提示模板，ZCode / Claude / Cursor 等可直接调用；
- **新增 DeepSeek 智能体**：自然语言 → 工具调用 → 工程解释；支持 PDF/DOCX/XLSX/PPTX/Notebook 附件；
- **新增现代化 Web 界面**：AI 对话、五种拓扑、圆图动画、匹配范围扫描、带宽/灵敏度/耐压、HTML 报告；
- **新增 MATLAB R2025b 复核**：一键 `-batch` 独立复算。

一句话：**它既是一个更好用的匹配设计软件，也是一个能被 AI 智能体调用的微波仿真 MCP。**

---

## 二、核心亮点

### 1. 15 个 MCP 工具

`design_matching_network`、`scan_matching_range`、`evaluate_network`、`convert_impedance_admittance`、`compute_voltage_stress`、`analyze_bandwidth`、`compare_topologies`、`get_topology_guide`、`get_smith_trajectory`、`search_knowledge`、`validate_design`、`export_design_report`、`launch_classic_app`、`get_system_status`、`list_presets`。

资源：`impedance://catalog`、`impedance://knowledge`、`impedance://status`。
提示模板：`design_match`、`explain_topology`、`troubleshoot`。

### 2. 解析解 + 节点法双重校验

每个设计先用拓扑公式求元件值，再把整个网络展开成 2/3 节点导纳矩阵，独立计算 `Zin/VSWR/S11`。公式符号或单位写错会立即暴露。

### 3. 五个拓扑 + 自动选型

L 型（左/右）、T 型、π 型Ⅰ/Ⅱ；`topology="auto"` 会自动比较五种拓扑，优先选择元件更少、可实现性更好的方案。

### 4. 工程分析

- VSWR<2 带宽（±60% 扫频）；
- ±5% 元件容差灵敏度；
- 峰值电压/RMS 电流/安全系数；
- 正向匹配范围扫描；
- 工程风险提示与替代拓扑。

### 5. 教学可视化

Smith 圆图逐段动画、播放/暂停/重置/速度、悬停读数、步骤卡片联动；带宽曲线、灵敏度柱状图、耐压柱状图。

---

## 三、验证结果

| 测试 | 结果 |
|---|---|
| Python 引擎回归 | **8/8 通过** |
| 300 组随机设计 | **VSWR 全部 1.000000** |
| MATLAB R2025b 交叉验证 | **5/5 通过，Zin 偏差 0.0** |
| MCP 协议测试 | **11/11 通过** |
| 浏览器逐页视觉验收 | AI / 设计 / 圆图分析 / 耐压 / 设置 / 关于 / 报告 |
| 报告一致性 | 报告与界面使用同一组精确元件值 |

复现：

```bat
python -m unittest app.tests.test_engine -v
python -m unittest app.tests.test_mcp_protocol -v
```

---

## 四、安装

### 4.1 新版智能外壳

```bat
pip install numpy pypdf openpyxl Pillow
start_app.bat
```

浏览器打开 `http://127.0.0.1:8765/`。Python 3.10+（开发环境 3.14）。

### 4.2 原版 MATLAB 软件

| 方式 | 文件 | Runtime |
|---|---|---|
| 安装包（推荐） | `APP_Release_Release_Version/Main_Installation/MyAppInstaller_mcr.exe` | **已内置**，直接安装 |
| 便携 exe | `.../for_redistribution_files_only/Impedance_Matching.exe` | 需先装 `VC_redist.x64.exe` + `MATLAB_Runtime_R2023b_Update_10_win64.zip` |

> 重要：`MyAppInstaller_mcr.exe` 的工程配置为 `package.mcr=true`，**安装包已包含 MATLAB Runtime R2023b**，不需要再单独安装 Runtime。
>
> 由于 GitHub Release 单文件/仓库体积限制，本 Release 的附件**不包含** 974 MB 的安装包与 4.6 GB 的 Runtime ZIP；它们位于项目 `APP_Release_Release_Version` 目录中，或按安装指南从 MathWorks 下载。

### 4.3 DeepSeek

右上角「设置」填写 API Key：

- 交大平台：`https://models.sjtu.edu.cn/api/v1` + `deepseek-chat`
- DeepSeek 官方：`https://api.deepseek.com/v1` + `deepseek-chat`

Key 只保存在本机 `data/config.json`，不会进入仓库。

---

## 五、MCP 接入

把下面加入 `~/.zcode/cli/config.json` 的 `mcp.servers`，重启 ZCode：

```json
{
  "mcp": {
    "servers": {
      "impedance-matching": {
        "type": "stdio",
        "command": "C:\\Python314\\python.exe",
        "args": ["D:\\path\\to\\app\\run_mcp.py"],
        "env": {"PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"},
        "timeoutMs": 120000
      }
    }
  }
}
```

然后对智能体说：

> 用 impedance-matching 工具设计 2.4 GHz、20+j5 Ω 的匹配网络，并分析 ±5% 容差和 10 W 耐压。

HTTP 模式：`python app\run_mcp.py --http 8790`（仅监听 127.0.0.1）。

---

## 六、本次修复

- 修复 V3.0 **L 型（右）正向扫描**的共轭符号错误：旧代码使用 `1/(1/50 − jωC1)` 且未取共轭；正确形式为 `conj(1/(1/50 + jωC1))`。
- S11 低于 −60 dB 时显示“< −60 dB（理想）”，不再出现 −321 dB 这类无意义数值。
- 报告导出使用界面上的精确 C1/C2，避免 L 四舍五入导致报告与界面不一致。
- 耐压界面区分“输入峰值电压”和“源开路电压”，避免把 2× 源电压误读为节点电压。
- 修复 MATLAB `mw_design.m` 文件名与函数名不一致导致 `-batch` 调用失败；已重命名并验证。
- 修复多页面图表在隐藏时尺寸为 0、切换后不重绘的问题。

---

## 七、文档

- [README](https://github.com/RuilinLu/Impedance_Matching_Calculation/blob/main/README.md)
- [用户手册（PDF）](https://github.com/RuilinLu/Impedance_Matching_Calculation/blob/main/docs/用户手册.pdf)
- [技术白皮书（PDF）](https://github.com/RuilinLu/Impedance_Matching_Calculation/blob/main/docs/技术白皮书.pdf)
- [比赛说明文档（PDF）](https://github.com/RuilinLu/Impedance_Matching_Calculation/blob/main/docs/比赛说明文档.pdf)
- [软件架构说明（PDF）](https://github.com/RuilinLu/Impedance_Matching_Calculation/blob/main/docs/软件架构说明.pdf)
- [安装指南（PDF）](https://github.com/RuilinLu/Impedance_Matching_Calculation/blob/main/APP_Release_Release_Version/ReadMe/Readme_First_Installation_Instruction.pdf)

---

## 八、附件说明

- `ImpedanceMCP_v4.0.0_Source.zip`：完整源码、文档与测试（不含 974 MB 安装包 / 4.6 GB Runtime ZIP）。
- `用户手册.pdf`、`技术白皮书.pdf`、`比赛说明文档.pdf`、`安装指南.pdf`：可直接阅读/打印。

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
