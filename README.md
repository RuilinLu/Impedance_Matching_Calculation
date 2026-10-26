# Impedance Matching AI

**微波阻抗匹配智能计算、Smith 圆图仿真、教材检索与 MCP 服务**

一个可独立运行的桌面软件，也是一个标准 MCP 服务器。它把匹配网络设计、节点法复核、Smith 圆图、教材全文/OCR/翻译、四类工程文档和工具调用大模型放进同一个本地应用。

> 独立开源项目 · MIT License · 不绑定任何平台或模型厂商
> 开发者：卢瑞林、卢柯吉、林芷伊、张昀蕾

---

## 功能

| 模块 | 能力 |
|---|---|
| 匹配设计 | L 型（左/右）、T 型、π 型Ⅰ/Ⅱ；解析解 + 完整网络节点法复核；自动选型 |
| Smith 圆图 | 逐段动画、负载/匹配点、等电阻/等电导圆、步骤回放 |
| 圆图分析 | 正向扫描可匹配范围；灰色密度云、外包络边界、悬停 Z/Γ/VSWR |
| 工程分析 | VSWR<2 带宽、±5% 容差灵敏度、峰值电压/电流与安全系数 |
| 教材库 | PDF 逐页索引、全文/模糊搜索、OCR、页面渲染缩放、学术翻译、引用截图 |
| 文档中心 | 软件功能、代码参考、AI 接口、MCP 协议；全文高亮与 AI 模糊搜索 |
| AI 智能体 | 任意文件、剪贴板、拖拽、图片/扫描页视觉输入；20 个本地工具；教材引用 |
| 模型设置 | 20 家厂商、逐模型能力/价格、峰谷计价、缓存与上下文统计、目录一键更新 |
| MCP | stdio / Streamable HTTP / legacy SSE；20 个工具、5 个资源、5 个提示模板 |

## 快速开始

### 源码运行

```bash
pip install -r requirements.txt
python app/run_app.py            # 原生 WebView2 窗口
python app/run_app.py --browser  # 浏览器界面（调试）
python app/run_mcp.py            # MCP stdio
python app/run_mcp.py --http 8790
```

Windows 原生窗口需要 `pywebview`、`pythonnet` 与 Edge WebView2 Runtime。教材 OCR 需要 `rapidocr_onnxruntime`；不安装 OCR 也可以使用文字层搜索与视觉模型。

### 发布包

Release 提供源码包与 Windows 便携版。教材、模型 Key 与用户数据不包含在发布包内。

## 教材库

教材不随仓库发布。你可以：

1. 把 PDF 放进项目或安装目录的 `TextBook/`；
2. 放进用户数据目录 `data/library/books/`；
3. 在软件内点击“添加教材”。

首次打开教材库会建立本地 SQLite 索引。文字层 PDF 立即可搜索；扫描版会标记 OCR，可逐页或按范围识别。所有教材处理都在本机完成，不会上传。

## 模型配置

设置 → 模型服务：

1. 选择服务商（内置 20 家，可一键更新）；
2. 选择协议（OpenAI 兼容 / Anthropic / 自定义 URL）；
3. 选择模型或填写自定义模型 ID；
4. 填写自己的 API Key（仅保存在本机 `data/config.json`）。

模型详情页可设置上下文、最大输出、视觉/音频、工具调用、JSON、思考模式、峰谷价格与币种。对话结束后会显示本轮 tokens、缓存命中率、上下文占用率与费用。

目录更新支持 models.dev、当前厂商 `/models`、官方公告抓取与 AI 校对补丁；每次更新自动备份，可回滚。

## MCP 接入

```json
{
  "mcp": {
    "servers": {
      "impedance-matching-ai": {
        "type": "stdio",
        "command": "python",
        "args": ["D:/path/to/app/run_mcp.py"],
        "env": {"PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"}
      }
    }
  }
}
```

HTTP：`python app/run_mcp.py --http 8790`，端点 `POST /mcp` 与 `GET /sse`。

## 文档

软件内置四类文档，可在“文档中心”全文搜索：

- **软件功能**：每个界面、输入、按钮、指标与 Smith 圆图学习流程；
- **代码参考**：AST 自动生成的模块、函数、参数、返回、局部变量与前端函数；
- **AI 接口**：厂商、协议、能力矩阵、视觉、价格、缓存与更新机制；
- **MCP 协议**：传输、工具 schema、资源、提示模板与客户端配置。

## 项目结构

```
app/
  impedance_mcp/
    engine.py          # 五种拓扑设计、节点法复核、扫描、带宽、耐压
    library.py         # 教材索引、全文搜索、OCR、页面渲染、翻译
    docs_hub.py        # 四域文档检索
    code_docs.py       # AST 代码参考
    agent.py           # 工具调用循环
    llm.py             # OpenAI / Anthropic 客户端
    providers.py       # 20 家厂商目录、更新、回滚
    usage.py           # tokens、缓存、上下文、费用
    attachments.py     # 任意文件、图片、OCR、视觉输入
    mcp_server.py      # stdio / HTTP / SSE
    web_server.py      # 本地 API
    web/               # 前端
    docs_content/      # 四域 Markdown 文档
  tests/               # 48 项单元测试
docs/                  # 仓库说明（软件内文档不生成 PDF）
release/               # 构建脚本与发布资产
```

## 测试

```bash
python -m unittest discover -s app/tests -v
```

覆盖计算内核、物理审计、MCP 协议、教材索引/OCR、任意附件、模型目录/费用、Web API、智能体工具循环与视觉消息。

## English

Impedance Matching AI is a standalone microwave-engineering desktop application and MCP server. It provides L/T/π matching-network design with full nodal verification, Smith-chart animation and scan density, voltage stress, a searchable textbook library with OCR and academic translation, four documentation domains, and a tool-calling AI agent with any-file and clipboard input. It supports 20 model providers with per-model capability/pricing profiles, cache/context/cost accounting, and one-click catalog updates with rollback. Textbooks and API keys are user-supplied and never bundled. See the in-app Documentation Centre for the full reference.

## License

MIT. See [LICENSE](LICENSE).
