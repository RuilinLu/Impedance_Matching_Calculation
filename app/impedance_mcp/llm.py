"""OpenAI-compatible / Anthropic Messages client for multiple providers.

The application never selects a vendor by default.  The user chooses a provider,
protocol, model and API key.  Only public http(s) endpoints are accepted.
Vision content, tool calls and cache-aware usage accounting are supported.
"""

from __future__ import annotations

import base64
import ipaddress
import json
import re
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

_VERIFIED_HOSTS: Dict[str, bool] = {}


class LLMError(Exception):
    def __init__(self, message: str, status: Optional[int] = None, hint: str = ""):
        super().__init__(message)
        self.message = message
        self.status = status
        self.hint = hint


def _is_public_host(host: str, port: int) -> bool:
    if host in _VERIFIED_HOSTS:
        return _VERIFIED_HOSTS[host]
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise LLMError(f"无法解析模型服务域名：{host}", hint=str(exc)) from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_reserved
                or ip.is_link_local or ip.is_multicast or ip.is_unspecified):
            raise LLMError(
                "出于安全策略，模型服务地址不能指向本机、内网或保留地址。",
                hint=f"{host} 解析到 {ip}",
            )
    _VERIFIED_HOSTS[host] = True
    return True


def _validate_url(url: str) -> urllib.parse.ParseResult:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise LLMError("Base URL 必须以 http:// 或 https:// 开头")
    if not parsed.hostname:
        raise LLMError("Base URL 缺少主机名")
    _is_public_host(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    return parsed


def normalize_base(base_url: str, api_style: str = "openai", chat_path: str = "") -> str:
    """Return a complete chat-completions URL.

    api_style:
      openai    -> append the provider's chat path (or /chat/completions)
      anthropic -> append /messages
      as_is     -> use the URL exactly as entered (Azure, custom gateways)
    """
    url = (base_url or "").strip().rstrip("/")
    if not url:
        raise LLMError("请选择模型服务商并填写 Base URL")
    parsed = _validate_url(url)
    style = (api_style or "openai").lower()
    if style in ("custom", "as_is"):
        return url
    if style == "anthropic":
        if url.endswith("/messages"):
            return url
        if url.endswith("/v1"):
            return url + "/messages"
        if re.search(r"/v\d+$", url):
            return url + "/messages"
        return url + "/v1/messages"
    if url.endswith("/chat/completions"):
        return url
    if chat_path:
        return url + "/" + chat_path.lstrip("/")
    path = parsed.path.lower()
    if re.search(r"/v\d+(?:/|$)", path) or path.endswith("/openai") or "compatible-mode" in path:
        return url + "/chat/completions"
    if path.endswith("/v1beta/openai"):
        return url + "/chat/completions"
    return url + "/v1/chat/completions"


def models_url(cfg: Dict[str, Any]) -> str:
    llm = cfg.get("llm", {})
    style = (llm.get("protocol") or llm.get("api_style") or "openai").lower()
    if style in ("custom", "as_is"):
        return ""
    chat = normalize_base(llm.get("base_url", ""), style, llm.get("chat_path", ""))
    if chat.endswith("/messages"):
        return chat[: -len("/messages")] + "/models"
    if chat.endswith("/chat/completions"):
        return chat[: -len("/chat/completions")] + "/models"
    return chat + "/models"


def _headers(api_key: str, cfg: Dict[str, Any]) -> Dict[str, str]:
    llm = cfg.get("llm", {})
    header = str(llm.get("auth_header") or "Authorization")
    prefix = llm.get("auth_prefix")
    if prefix is None:
        prefix = "Bearer " if header.lower() == "authorization" else ""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "ImpedanceMatchingAI/4.3",
        header: f"{prefix}{api_key}",
    }
    extra = llm.get("extra_headers") or {}
    if isinstance(extra, dict):
        for key, value in extra.items():
            headers[str(key)] = str(value)
    if (llm.get("protocol") or llm.get("api_style") or "").lower() == "anthropic":
        headers.setdefault("anthropic-version", "2023-06-01")
    return headers


def _open_json(url: str, body: Optional[Dict[str, Any]], headers: Dict[str, str],
               timeout: int) -> Any:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers,
                                 method="POST" if body is not None else "GET")
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
            detail = payload.get("error", payload)
            msg = detail.get("message") if isinstance(detail, dict) else str(detail)
        except Exception:
            msg = raw[:500]
        hint = ""
        if exc.code == 401:
            hint = "API Key 无效或已过期，请在设置中重新填写。"
        elif exc.code == 402:
            hint = "账户余额不足。"
        elif exc.code == 403:
            hint = "该 Key 没有调用此模型的权限，请检查服务商控制台。"
        elif exc.code == 404:
            hint = "Base URL、模型 ID 或部署名不存在，请检查服务商配置。"
        elif exc.code == 429:
            hint = "触发限流，请稍后重试。"
        raise LLMError(f"模型服务返回 HTTP {exc.code}：{msg or '未知错误'}",
                       status=exc.code, hint=hint) from exc
    except urllib.error.URLError as exc:
        raise LLMError(f"无法连接模型服务：{exc.reason}",
                       hint="请检查网络、代理与 Base URL。") from exc
    except TimeoutError as exc:
        raise LLMError("模型服务响应超时。", hint="请稍后重试或缩短问题。") from exc


def _profile(cfg: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from . import providers
        return providers.profile(cfg)
    except Exception:
        return {}


def _output_limit(cfg: Dict[str, Any]) -> int:
    llm = cfg.get("llm", {})
    configured = int(llm.get("max_tokens", 4096) or 4096)
    profile = _profile(cfg)
    maximum = int(profile.get("max_output", 0) or 0)
    if maximum > 0:
        return max(64, min(configured, maximum))
    return max(64, configured)


def _plain_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "\n".join(parts)
    return str(content or "")


def _anthropic_content(content: Any) -> List[Dict[str, Any]]:
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if not isinstance(content, list):
        return [{"type": "text", "text": str(content or "")}]
    blocks: List[Dict[str, Any]] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        kind = block.get("type")
        if kind == "text":
            blocks.append({"type": "text", "text": str(block.get("text", ""))})
        elif kind == "image":
            blocks.append(block)
        elif kind == "image_url":
            url = ((block.get("image_url") or {}) if isinstance(block.get("image_url"), dict)
                   else {"url": block.get("image_url")})
            data_url = str(url.get("url", ""))
            match = re.match(r"data:([^;]+);base64,(.*)", data_url, re.S)
            if match:
                blocks.append({
                    "type": "image",
                    "source": {"type": "base64", "media_type": match.group(1),
                               "data": match.group(2)},
                })
    return blocks or [{"type": "text", "text": ""}]


def _anthropic_messages(messages: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]]]:
    system_parts: List[str] = []
    out: List[Dict[str, Any]] = []
    pending_tools: List[Dict[str, Any]] = []
    for message in messages:
        role = message.get("role")
        content = message.get("content")
        if role == "system":
            if content:
                system_parts.append(_plain_text(content))
            continue
        if role == "tool":
            pending_tools.append({
                "type": "tool_result",
                "tool_use_id": message.get("tool_call_id") or "",
                "content": _plain_text(content),
            })
            continue
        if pending_tools:
            out.append({"role": "user", "content": pending_tools})
            pending_tools = []
        if role == "assistant":
            blocks: List[Dict[str, Any]] = []
            if content:
                blocks.append({"type": "text", "text": _plain_text(content)})
            for call in message.get("tool_calls") or []:
                fn = call.get("function") or {}
                raw_args = fn.get("arguments") or "{}"
                try:
                    parsed = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
                except Exception:
                    parsed = {}
                blocks.append({
                    "type": "tool_use",
                    "id": call.get("id") or "tool_call",
                    "name": fn.get("name") or "unknown",
                    "input": parsed if isinstance(parsed, dict) else {},
                })
            if blocks:
                out.append({"role": "assistant", "content": blocks})
        elif role == "user":
            out.append({"role": "user", "content": _anthropic_content(content)})
    if pending_tools:
        out.append({"role": "user", "content": pending_tools})
    return system_parts, out


def _chat_openai(cfg: Dict[str, Any], messages: List[Dict[str, Any]],
                 tools: Optional[List[Dict[str, Any]]], timeout: int) -> Dict[str, Any]:
    llm = cfg.get("llm", {})
    style = (llm.get("protocol") or llm.get("api_style") or "openai").lower()
    url = normalize_base(llm.get("base_url", ""), style, llm.get("chat_path", ""))
    payload: Dict[str, Any] = {
        "model": llm.get("model", ""),
        "messages": messages,
        "temperature": float(llm.get("temperature", 0.25)),
        "max_tokens": _output_limit(cfg),
        "stream": False,
    }
    model_id = str(llm.get("model") or "")
    if re.match(r"^o[1-9]", model_id):
        payload.pop("temperature", None)
        payload["max_completion_tokens"] = payload.pop("max_tokens")
    effort = str(llm.get("reasoning_effort") or "").strip()
    if effort:
        payload["reasoning_effort"] = effort
    extra_body = llm.get("extra_body")
    if isinstance(extra_body, dict):
        for key, value in extra_body.items():
            payload[str(key)] = value
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    headers = _headers(llm.get("api_key", ""), cfg)
    data = None
    last_exc: Optional[Exception] = None
    for attempt in range(3):
        try:
            data = _open_json(url, payload, headers, timeout)
            break
        except LLMError as exc:
            last_exc = exc
            if exc.status in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise
    if data is None:
        raise last_exc or LLMError("模型请求失败")
    choice = (data.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    return {
        "content": msg.get("content") or "",
        "reasoning": msg.get("reasoning_content") or "",
        "tool_calls": msg.get("tool_calls") or [],
        "finish_reason": choice.get("finish_reason"),
        "usage": data.get("usage") or {},
        "model": data.get("model") or llm.get("model"),
        "raw_message": msg,
        "protocol": "openai",
    }


def _chat_anthropic(cfg: Dict[str, Any], messages: List[Dict[str, Any]],
                    tools: Optional[List[Dict[str, Any]]], timeout: int) -> Dict[str, Any]:
    llm = cfg.get("llm", {})
    url = normalize_base(llm.get("base_url", ""), "anthropic", llm.get("chat_path", ""))
    system_parts, converted = _anthropic_messages(messages)
    payload: Dict[str, Any] = {
        "model": llm.get("model", ""),
        "max_tokens": _output_limit(cfg),
        "messages": converted,
        "temperature": float(llm.get("temperature", 0.25)),
    }
    thinking_budget = int(llm.get("thinking_budget", 0) or 0)
    if thinking_budget > 0:
        thinking_budget = min(thinking_budget, max(1024, payload["max_tokens"] - 1024))
        payload["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}
        payload.pop("temperature", None)
    if system_parts:
        payload["system"] = "\n\n".join(system_parts)
    if tools:
        payload["tools"] = [
            {
                "name": tool.get("function", {}).get("name", ""),
                "description": tool.get("function", {}).get("description", ""),
                "input_schema": tool.get("function", {}).get("parameters", {"type": "object"}),
            }
            for tool in tools
        ]
    headers = _headers(llm.get("api_key", ""), cfg)
    data = None
    last_exc: Optional[Exception] = None
    for attempt in range(3):
        try:
            data = _open_json(url, payload, headers, timeout)
            break
        except LLMError as exc:
            last_exc = exc
            if exc.status in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise
    if data is None:
        raise last_exc or LLMError("模型请求失败")

    text_parts: List[str] = []
    tool_calls: List[Dict[str, Any]] = []
    for block in data.get("content") or []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text":
            text_parts.append(block.get("text") or "")
        elif block.get("type") == "tool_use":
            tool_calls.append({
                "id": block.get("id") or "tool_call",
                "type": "function",
                "function": {
                    "name": block.get("name") or "",
                    "arguments": json.dumps(block.get("input") or {}, ensure_ascii=False),
                },
            })
    usage = data.get("usage") or {}
    stop = data.get("stop_reason")
    finish = "tool_calls" if tool_calls else ("length" if stop == "max_tokens" else "stop")
    return {
        "content": "\n".join(x for x in text_parts if x),
        "reasoning": "",
        "tool_calls": tool_calls,
        "finish_reason": finish,
        "usage": usage,
        "model": data.get("model") or llm.get("model"),
        "raw_message": data,
        "protocol": "anthropic",
    }


def chat(
    cfg: Dict[str, Any],
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: str = "auto",
    timeout: int = 150,
) -> Dict[str, Any]:
    llm = cfg.get("llm", {})
    key = (llm.get("api_key") or "").strip()
    if not llm.get("base_url"):
        raise LLMError("尚未选择模型服务商。",
                       hint="打开右上角「设置」→ 选择服务商 → 填写 Base URL、模型 ID 和 API Key。")
    if not llm.get("model"):
        raise LLMError("尚未选择模型 ID。",
                       hint="在设置中选择服务商后选择模型，或填写「自定义模型 ID」。")
    if not key:
        raise LLMError("尚未填写 API Key。",
                       hint="在设置中填写你从服务商控制台获取的 Key；本软件不会内置任何厂商密钥。")
    style = (llm.get("protocol") or llm.get("api_style") or "openai").lower()
    if style == "anthropic":
        return _chat_anthropic(cfg, messages, tools, timeout)
    return _chat_openai(cfg, messages, tools, timeout)


def vision_supported(cfg: Dict[str, Any]) -> bool:
    return bool(_profile(cfg).get("vision"))


def test_connection(cfg: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
    started = time.time()
    resp = chat(cfg, [
        {"role": "system", "content": "你是微波工程助手，只回复两个字。"},
        {"role": "user", "content": "请回复：在线"},
    ], timeout=timeout)
    from . import usage
    stats = usage.compute_cost(_profile(cfg), resp.get("usage") or {})
    return {
        "ok": True,
        "latency_s": round(time.time() - started, 2),
        "model": resp.get("model"),
        "reply": (resp.get("content") or "")[:80],
        "usage": resp.get("usage"),
        "cost": stats,
        "summary": f"模型连接成功（{resp.get('model')}，{time.time() - started:.1f}s）。",
    }


def list_models(cfg: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    llm = cfg.get("llm", {})
    key = (llm.get("api_key") or "").strip()
    if not key:
        raise LLMError("尚未填写 API Key")
    url = models_url(cfg)
    if not url:
        return {"ok": True, "models": []}
    data = _open_json(url, None, _headers(key, cfg), timeout)
    items = data.get("data") if isinstance(data, dict) else data
    models = []
    for item in items or []:
        if isinstance(item, dict):
            models.append(item.get("id"))
        elif isinstance(item, str):
            models.append(item)
    return {"ok": True, "models": [m for m in models if m]}
