"""Minimal DeepSeek / OpenAI-compatible client (stdlib only)."""

from __future__ import annotations

import ipaddress
import json
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

_VERIFIED_HOSTS: Dict[str, bool] = {}


class LLMError(Exception):
    def __init__(self, message: str, status: Optional[int] = None,
                 hint: str = ""):
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


def normalize_base(base_url: str) -> str:
    url = (base_url or "").strip().rstrip("/")
    if not url:
        raise LLMError("尚未配置模型服务的 Base URL")
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise LLMError("Base URL 必须以 http:// 或 https:// 开头")
    if not parsed.hostname:
        raise LLMError("Base URL 缺少主机名")
    _is_public_host(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    if url.endswith("/chat/completions"):
        return url
    if url.endswith("/v1"):
        return url + "/chat/completions"
    return url + "/v1/chat/completions"


def models_url(base_url: str) -> str:
    chat = normalize_base(base_url)
    return chat[: -len("/chat/completions")] + "/models"


def _headers(api_key: str) -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "ImpedanceMCP/4.0 (+SJTU)",
    }


def _open_json(url: str, body: Optional[Dict[str, Any]], api_key: str,
               timeout: int) -> Any:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=_headers(api_key),
                                 method="POST" if body is not None else "GET")
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw).get("error", {})
            msg = detail.get("message") if isinstance(detail, dict) else str(detail)
        except Exception:
            msg = raw[:500]
        hint = ""
        if exc.code == 401:
            hint = "API Key 无效或已过期，请在设置中重新填写。"
        elif exc.code == 402:
            hint = "账户余额不足。"
        elif exc.code == 404:
            hint = "模型名称或接口路径不存在，请检查模型 ID 与 Base URL。"
        elif exc.code == 429:
            hint = "触发限流，请稍后重试。"
        raise LLMError(f"模型服务返回 HTTP {exc.code}：{msg or '未知错误'}",
                       status=exc.code, hint=hint) from exc
    except urllib.error.URLError as exc:
        raise LLMError(f"无法连接模型服务：{exc.reason}",
                       hint="请检查网络、代理与 Base URL。") from exc
    except TimeoutError as exc:
        raise LLMError("模型服务响应超时。", hint="请稍后重试或缩短问题。") from exc


def chat(
    cfg: Dict[str, Any],
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: str = "auto",
    timeout: int = 150,
) -> Dict[str, Any]:
    llm = cfg.get("llm", {})
    key = (llm.get("api_key") or "").strip()
    if not key:
        raise LLMError("尚未配置 DeepSeek API Key。",
                       hint="点击右上角「设置」填写 API Key，或设置环境变量 DEEPSEEK_API_KEY。")
    url = normalize_base(llm.get("base_url", ""))
    payload: Dict[str, Any] = {
        "model": llm.get("model", "deepseek-chat"),
        "messages": messages,
        "temperature": float(llm.get("temperature", 0.25)),
        "max_tokens": int(llm.get("max_tokens", 2600)),
        "stream": False,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice

    last_exc: Optional[Exception] = None
    for attempt in range(3):
        try:
            data = _open_json(url, payload, key, timeout)
            break
        except LLMError as exc:
            last_exc = exc
            if exc.status in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(1.5 * (attempt + 1))
                continue
            if tools and exc.status == 400 and "tool" in exc.message.lower():
                payload.pop("tools", None)
                payload.pop("tool_choice", None)
                continue
            raise
    else:
        raise last_exc or LLMError("模型请求失败")

    try:
        choice = (data.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
    except Exception as exc:  # noqa: BLE001
        raise LLMError(f"模型返回格式异常：{str(exc)}") from exc
    return {
        "content": msg.get("content") or "",
        "reasoning": msg.get("reasoning_content") or "",
        "tool_calls": msg.get("tool_calls") or [],
        "finish_reason": choice.get("finish_reason"),
        "usage": data.get("usage") or {},
        "model": data.get("model") or payload["model"],
        "raw_message": msg,
    }


def test_connection(cfg: Dict[str, Any], timeout: int = 45) -> Dict[str, Any]:
    started = time.time()
    resp = chat(cfg, [
        {"role": "system", "content": "你是微波工程助手，只回复两个字。"},
        {"role": "user", "content": "请回复：在线"},
    ], timeout=timeout)
    return {
        "ok": True,
        "latency_s": round(time.time() - started, 2),
        "model": resp.get("model"),
        "reply": (resp.get("content") or "")[:80],
        "usage": resp.get("usage"),
        "summary": f"模型连接成功（{resp.get('model')}，{time.time() - started:.1f}s）。",
    }


def list_models(cfg: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    llm = cfg.get("llm", {})
    key = (llm.get("api_key") or "").strip()
    if not key:
        raise LLMError("尚未配置 API Key")
    url = models_url(llm.get("base_url", ""))
    data = _open_json(url, None, key, timeout)
    items = data.get("data") if isinstance(data, dict) else data
    models = []
    for item in items or []:
        if isinstance(item, dict):
            models.append(item.get("id"))
        elif isinstance(item, str):
            models.append(item)
    return {"ok": True, "models": [m for m in models if m]}
