# AI 大模型接口

> 本软件不绑定任何单一模型厂商。用户选择服务商、协议、模型并填写自己的 API Key；软件只负责把统一的工具/消息格式转换成对应协议。

## 1. 架构总览

```
界面 / 浮动助手 / MCP 客户端
        │
        ▼
agent.run_chat  ── 工具循环、引用事件、用量累计
        │
        ▼
llm.chat  ── OpenAI 兼容 / Anthropic Messages / 自定义 URL
        │
        ▼
用户选择的模型服务商（20 家内置目录，可一键更新）
```

- `providers.json`：内置目录，只包含公开的端点、模型 ID、能力与参考价格，不含任何密钥。
- `data/catalog/providers_override.json`：用户更新/手工修改后的覆盖层，优先于内置目录。
- `data/config.json`：当前服务商、协议、模型、密钥、模型详情与界面设置。
- `data/usage.jsonl`：每次调用的 token、缓存、费用与耗时。

## 2. 服务商目录

内置 20 家：

| 区域 | 服务商 | 默认协议 | 典型 Base URL |
|---|---|---|---|
| 国际 | OpenAI | OpenAI | `https://api.openai.com/v1` |
| 国际 | Anthropic | Anthropic | `https://api.anthropic.com` |
| 国际 | Google Gemini | OpenAI 兼容 | `https://generativelanguage.googleapis.com/v1beta/openai` |
| 国际 | xAI Grok | OpenAI | `https://api.x.ai/v1` |
| 国际 | Mistral | OpenAI | `https://api.mistral.ai/v1` |
| 国际 | Groq | OpenAI | `https://api.groq.com/openai/v1` |
| 国际 | OpenRouter | OpenAI | `https://openrouter.ai/api/v1` |
| 国内 | DeepSeek | OpenAI / Anthropic | `https://api.deepseek.com`，Anthropic：`https://api.deepseek.com/anthropic` |
| 国内 | 阿里云百炼 | OpenAI 兼容 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 国内 | 智谱 GLM | OpenAI 兼容 | `https://open.bigmodel.cn/api/paas/v4` |
| 国内 | Moonshot Kimi | OpenAI | `https://api.moonshot.cn/v1` |
| 国内 | 百度千帆 | OpenAI 兼容 | `https://qianfan.baidubce.com/v2` |
| 国内 | 腾讯混元 | OpenAI 兼容 | `https://api.hunyuan.cloud.tencent.com/v1` |
| 国内 | 字节火山方舟 | OpenAI 兼容 | `https://ark.cn-beijing.volces.com/api/v3` |
| 国内 | MiniMax | OpenAI 兼容 | `https://api.minimax.chat/v1` |
| 国内 | 零一万物 | OpenAI 兼容 | `https://api.lingyiwanwu.com/v1` |
| 国内 | 阶跃星辰 | OpenAI 兼容 | `https://api.stepfun.com/v1` |
| 国内 | 百川智能 | OpenAI 兼容 | `https://api.baichuan-ai.com/v1` |
| 国内 | 讯飞星火 | OpenAI 兼容 | `https://spark-api-open.xf-yun.com/v1` |
| 聚合 | SiliconFlow | OpenAI 兼容 | `https://api.siliconflow.cn/v1` |

每个服务商条目包含：`id`、中英文名、国家/地区、OpenAI Base URL、可选 Anthropic Base URL、鉴权头、环境变量名、文档链接、模型发布页、备注。

## 3. 协议适配

### 3.1 OpenAI 兼容

请求：`POST {base_url}/chat/completions`。

```json
{
  "model": "deepseek-flash",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "temperature": 0.25,
  "max_tokens": 4096,
  "tools": [{"type": "function", "function": {"name": "...", "parameters": {}}}],
  "tool_choice": "auto"
}
```

- 鉴权：`Authorization: Bearer <key>`，可在服务商条目中改为 `api-key` 等。
- 工具结果以 `role="tool"`、`tool_call_id` 回传。
- 用量读取 `usage.prompt_tokens`、`completion_tokens`、`prompt_tokens_details.cached_tokens`、`completion_tokens_details.reasoning_tokens`。

### 3.2 Anthropic Messages

请求：`POST {base}/v1/messages`（若 Base 已以 `/v1` 结尾则只追加 `/messages`）。

- 鉴权：`x-api-key` + `anthropic-version: 2023-06-01`。
- 系统提示放在顶层 `system`，不放在 messages 中。
- 工具调用使用 `tool_use` / `tool_result` 内容块。
- 图片使用 `{"type":"image","source":{"type":"base64","media_type":"image/png","data":"..."}}`。
- 用量读取 `usage.input_tokens`、`output_tokens`、`cache_read_input_tokens`、`cache_creation_input_tokens`。

### 3.3 自定义 URL

选择“完全自定义 URL”时不追加任何路径，适合 Azure OpenAI、企业网关、反向代理。需要用户自己填写完整端点与鉴权头。

## 4. 模型能力字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 调用时使用的模型 ID |
| `name` | string | 界面显示名 |
| `context` | int | 上下文窗口，tokens |
| `max_output` | int | 最大输出，tokens |
| `vision` | bool | 是否支持图像输入 |
| `audio` | bool | 是否支持音频输入 |
| `tool_call` | bool | 是否支持函数/工具调用 |
| `json_output` | bool | 是否支持 JSON 模式 |
| `reasoning` | bool | 是否支持思考模式 |
| `responses_api` | bool | 是否提供 Responses API |
| `anthropic_api` | bool | 是否提供 Anthropic 兼容端点 |
| `fim` | bool | 是否支持 FIM 补全 |
| `pricing` | object | 价格，见第 5 节 |
| `concurrency` | int | 厂商并发限制（参考值） |
| `release` | string | 模型发布/版本日期 |
| `notes` | string | 限制说明，例如“仅非思考模式支持 FIM” |

能力字段只用于界面提示、视觉消息路由与价格计算，不会因为标记为支持就强制调用对应接口；实际请求仍由所选协议决定。

## 5. 价格、缓存与费用

### 5.1 价格结构

价格统一为“每 100 万 tokens”：

```json
{
  "currency": "CNY",
  "input_cache_hit": 0.15,
  "input_cache_miss": 4.5,
  "output": 13.5,
  "peak": {
    "input_cache_hit": 0.30,
    "input_cache_miss": 9.0,
    "output": 27.0
  },
  "off_peak": {
    "input_cache_hit": 0.15,
    "input_cache_miss": 4.5,
    "output": 13.5
  }
}
```

### 5.2 计算公式

设：

- `P` = 输入 tokens（`prompt_tokens`）
- `C` = 缓存命中的输入 tokens（`cached_tokens`）
- `O` = 输出 tokens（`completion_tokens`）
- `p_hit`、`p_miss`、`p_out` = 对应单价（元/百万 tokens）

则：

```
费用 = [C × p_hit + (P − C) × p_miss + O × p_out] / 1,000,000
缓存命中率 = C / P
上下文占用率 = P / context
```

若模型配置了 `peak` 与 `off_peak`，软件按本地时间与厂商谷时窗口自动选择；也可在设置中关闭自动峰谷计价，始终使用基础价格。

### 5.3 DeepSeek 示例

| 模型 | 上下文 | 输出 | 思考 | 视觉 | 工具 | 价格（谷时，元/百万 tokens） | 价格（峰时） |
|---|---|---|---|---|---|---|---|
| `deepseek-flash` | 1M | 384K | 支持 | 支持 | 支持 | 命中 0.02 / 未命中 1 / 输出 4 | 0.04 / 2 / 8 |
| `deepseek-v4-pro` | 1M | 384K | 支持 | 不支持 | 支持 | 命中 0.15 / 未命中 4.5 / 输出 13.5 | 0.30 / 9 / 27 |

并发限制：`deepseek-flash` 2500，`deepseek-v4-pro` 500。两者均支持 JSON Output、Tool Calls、Responses API、Anthropic API、对话前缀续写；FIM 仅在非思考模式支持。

## 6. 视觉与多模态

1. 在模型详情中开启“图像理解”。
2. 用户上传图片、扫描版 PDF 或把截图粘贴到输入框。
3. 软件为每个附件生成缩略图与 base64 数据，按协议组装：
   - OpenAI：`{"type":"image_url","image_url":{"url":"data:image/png;base64,..."}}`
   - Anthropic：`{"type":"image","source":{"type":"base64","media_type":"image/png","data":"..."}}`
4. 同时发送 OCR 文本（若有），让模型既能读字也能看图。
5. 未开启视觉的模型只收到文字，界面会提示“当前模型不支持图像理解”。

## 7. 工具调用与智能体循环

`agent.run_chat` 的最多工具轮数为 5：

1. 发送系统提示、历史消息与工具 schema。
2. 模型返回 `tool_calls` 时，逐个执行本地工具。
3. 把结果以 `tool` 消息回传，继续下一轮。
4. 模型不再调用工具时，输出最终文本并发送 `done` 事件。
5. 累计每轮 `usage`，统一计算缓存命中率、上下文占用与费用。

工具结果超过 16 KB 会截断并标记；教材引用会额外发送 `citation` 事件，界面展示缩略图与跳转按钮。

## 8. 目录一键更新

### 8.1 数据来源

- `https://models.dev/api.json`：公开厂商/模型目录。
- 当前服务商的 `GET {base}/models`：需要有效 Key，返回该账号可见模型。
- 厂商公开的模型发布页/价格页：抓取 HTML 并提取模型 ID 候选。

### 8.2 合并策略

- 以厂商 `id` 匹配；新模型追加，已有模型保留用户手工填写的能力与价格。
- 已下线/不在官方列表的模型不会自动删除，只标记 `deprecated`，避免破坏用户现有配置。
- 更新写入 `data/catalog/providers_override.json`，原文件备份为 `.bak.json`。
- 每次更新记录 `updated_at`、来源、警告与失败厂商列表。

### 8.3 AI 校对更新

当官方页面结构变化、无法可靠解析时，可使用“用 AI 校对更新”：

1. 软件抓取公告/价格页面文本（最多约 20 KB/厂商）。
2. 把当前目录摘要与公告文本发送给已配置模型。
3. 要求模型输出严格 JSON：`{"providers":[{"id":"...","models":[...]}]}`。
4. 软件做 schema 校验、字段白名单与数值范围检查；不合法的条目直接丢弃。
5. 界面明确提示“AI 可能出错，请逐项核对”，并保留回滚入口。

## 9. 安全

- 只允许 `http/https`，请求前解析域名并拒绝 localhost、环回、私有、保留、链路本地与组播地址。
- API Key 只在本机配置文件中，界面只显示前后各 4 位；日志不记录 Key。
- 模型服务返回的错误会映射为可读提示：401 Key 无效、402 余额不足、403 无权限、404 Base URL/模型不存在、429 限流。
- 不自动把教材、附件或用户问题上传到任何第三方；只有用户主动发送的对话内容会离开本机。
- 一键更新只读取公开页面，不携带 API Key（当前服务商的 `/models` 接口除外）。

## 10. 常见错误

| HTTP | 含义 | 处理 |
|---|---|---|
| 400 | 请求格式/参数错误 | 检查模型 ID、工具 schema、上下文是否超限 |
| 401 | Key 无效 | 重新填写 Key；确认没有多余空格 |
| 402 | 余额不足 | 充值或更换服务商 |
| 403 | 无权限 | 检查该 Key 是否开通此模型 |
| 404 | 端点/模型不存在 | 检查 Base URL 与模型 ID；切换协议 |
| 413 | 请求体过大 | 减少附件或改用长上下文模型 |
| 429 | 限流/并发超限 | 稍后重试；降低并发 |
| 5xx | 服务商故障 | 稍后重试；查看厂商状态页 |
