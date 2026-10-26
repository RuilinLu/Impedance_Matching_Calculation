"""Build the built-in provider catalog from the open-source models.dev registry.

Source: https://github.com/sst/models.dev (public JSON API https://models.dev/api.json)
The generated file contains no secrets; it only lists provider endpoints, model IDs
and documentation URLs.  Users still have to enter their own API keys.

Usage:
    python release/build_providers.py
"""

from __future__ import annotations

import ipaddress
import json
import socket
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "impedance_mcp" / "providers.json"
SOURCE = "https://models.dev/api.json"
DOC = "https://github.com/sst/models.dev"

ZH = {
    "openai": "OpenAI",
    "anthropic": "Anthropic Claude",
    "google": "Google Gemini",
    "azure": "Azure OpenAI",
    "deepseek": "DeepSeek 深度求索",
    "alibaba": "阿里云百炼（国际）",
    "alibaba-cn": "阿里云百炼（中国）",
    "zhipuai": "智谱 AI（GLM）",
    "moonshotai": "月之暗面 Kimi（国际）",
    "moonshotai-cn": "月之暗面 Kimi（中国）",
    "siliconflow": "硅基流动 SiliconFlow（国际）",
    "siliconflow-cn": "硅基流动 SiliconFlow（中国）",
    "volcengine": "火山引擎方舟（豆包）",
    "stepfun": "阶跃星辰 StepFun（中国）",
    "stepfun-ai": "阶跃星辰 StepFun（国际）",
    "sensenova": "商汤 SenseNova",
    "modelscope": "魔搭 ModelScope",
    "tencent-tokenhub": "腾讯 TokenHub",
    "minimax": "MiniMax（国际）",
    "minimax-cn": "MiniMax（中国）",
    "xai": "xAI Grok",
    "groq": "Groq",
    "mistral": "Mistral",
    "cohere": "Cohere",
    "togetherai": "Together AI",
    "deepinfra": "DeepInfra",
    "perplexity": "Perplexity",
    "openrouter": "OpenRouter",
    "nvidia": "NVIDIA NIM",
    "fireworks": "Fireworks AI",
}

FEATURED = [
    "openai", "anthropic", "google", "deepseek", "alibaba-cn", "zhipuai",
    "moonshotai-cn", "siliconflow-cn", "volcengine", "minimax-cn", "xai",
    "groq", "mistral", "openrouter", "nvidia", "cohere", "togetherai",
]

# Providers whose native API is Anthropic Messages rather than OpenAI chat.
ANTHROPIC_STYLE = {"anthropic", "minimax", "minimax-cn", "minimax-coding-plan",
                   "minimax-cn-coding-plan"}

# Curated endpoints for providers where models.dev omits the base URL.
CURATED = {
    "openai": ("https://api.openai.com/v1", "openai"),
    "anthropic": ("https://api.anthropic.com/v1", "anthropic"),
    "google": ("https://generativelanguage.googleapis.com/v1beta/openai", "openai"),
    "azure": ("https://<resource>.openai.azure.com/openai/deployments/<deployment>/chat/completions?api-version=2024-10-21", "as_is"),
    "xai": ("https://api.x.ai/v1", "openai"),
    "groq": ("https://api.groq.com/openai/v1", "openai"),
    "mistral": ("https://api.mistral.ai/v1", "openai"),
    "cohere": ("https://api.cohere.ai/compatibility/v1", "openai"),
    "togetherai": ("https://api.together.xyz/v1", "openai"),
    "deepinfra": ("https://api.deepinfra.com/v1/openai", "openai"),
    "perplexity": ("https://api.perplexity.ai", "openai"),
    "fireworks": ("https://api.fireworks.ai/inference/v1", "openai"),
    "openrouter": ("https://openrouter.ai/api/v1", "openai"),
}

NOTES = {
    "azure": "把 <resource>、<deployment> 换成你的 Azure 资源名和部署名；鉴权头为 api-key。",
    "google": "使用 Gemini 的 OpenAI 兼容端点；模型 ID 如 gemini-2.5-pro。",
    "anthropic": "使用 Anthropic Messages 原生协议（本软件已适配工具调用）。",
}

# Providers whose chat endpoint is not the usual <base>/chat/completions.
CHAT_PATHS = {
    "perplexity": "/chat/completions",
    "perplexity-agent": "/chat/completions",
    "anthropic": "/messages",
    "minimax": "/messages",
    "minimax-cn": "/messages",
    "minimax-coding-plan": "/messages",
    "minimax-cn-coding-plan": "/messages",
}

# Providers not present in models.dev can be added here in the future.
EXTRA = {}



def _public_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return False
    try:
        infos = socket.getaddrinfo(parsed.hostname, parsed.port or 443,
                                   proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_reserved
                or ip.is_link_local or ip.is_multicast or ip.is_unspecified):
            return False
    return True


def _models(provider: dict, limit: int = 14) -> list:
    models = provider.get("models") or {}
    preferred = []
    other = []
    for mid, m in models.items():
        item = {
            "id": mid,
            "name": m.get("name") or mid,
            "tool_call": bool(m.get("tool_call")),
            "reasoning": bool(m.get("reasoning")),
        }
        (preferred if item["tool_call"] else other).append(item)
    preferred.sort(key=lambda x: (not x["reasoning"], x["id"]))
    return (preferred + other)[:limit]


def build() -> dict:
    if not _public_url(SOURCE):
        raise SystemExit("models.dev resolves to a non-public address; refusing to fetch")
    req = urllib.request.Request(SOURCE, headers={"User-Agent": "ImpedanceMCP-build/4.1"})
    with urllib.request.urlopen(req, timeout=45) as response:
        raw = json.loads(response.read().decode("utf-8"))

    providers = []
    seen = set()
    for pid, p in raw.items():
        npm = p.get("npm") or ""
        api = p.get("api") or ""
        curated = CURATED.get(pid)
        if curated:
            api, style = curated
        elif npm in ("@ai-sdk/openai-compatible", "@ai-sdk/openai",
                     "@ai-sdk/openai-compatible-cn"):
            style = "openai"
        elif pid in ANTHROPIC_STYLE:
            style = "anthropic"
        elif npm in ("@ai-sdk/azure",):
            style = "as_is"
        else:
            continue
        if not api:
            continue
        if pid in seen:
            continue
        seen.add(pid)
        models = [] if pid == "azure" else _models(p)
        if not models and pid not in CURATED:
            continue
        item = {
            "id": pid,
            "name": p.get("name") or pid,
            "name_zh": ZH.get(pid, p.get("name") or pid),
            "api": api,
            "api_style": style,
            "chat_path": CHAT_PATHS.get(pid, "/messages" if style == "anthropic" else ""),
            "auth_header": "api-key" if style == "as_is" else (
                "x-api-key" if style == "anthropic" else "Authorization"),
            "auth_prefix": "" if style in ("as_is", "anthropic") else "Bearer ",
            "env": p.get("env") or [],
            "doc": p.get("doc") or "",
            "models": models,
            "featured": pid in FEATURED,
            "featured_rank": FEATURED.index(pid) if pid in FEATURED else 999,
            "notes": NOTES.get(pid, ""),
        }
        if style == "as_is":
            item["model_hint"] = "部署名 / deployment name"
        providers.append(item)

    for pid, p in EXTRA.items():
        if pid in seen:
            continue
        providers.append({
            "id": pid,
            "name": p["name"],
            "name_zh": p.get("name_zh") or p["name"],
            "api": p["api"],
            "api_style": p.get("api_style", "openai"),
            "chat_path": CHAT_PATHS.get(pid, ""),
            "auth_header": p.get("auth_header", "Authorization"),
            "auth_prefix": p.get("auth_prefix", "Bearer "),
            "env": p.get("env", []),
            "doc": p.get("doc", ""),
            "models": p.get("models", []),
            "featured": bool(p.get("featured")),
            "featured_rank": 999,
            "notes": p.get("notes", ""),
        })

    providers.sort(key=lambda x: (not x["featured"], x["featured_rank"], x["name_zh"], x["id"]))
    return {
        "version": "4.1.0",
        "updated": "2026-10-26",
        "source": DOC,
        "source_api": SOURCE,
        "note": "目录来自 models.dev；不包含任何 API Key。用户自行选择服务商并填写密钥。",
        "providers": providers,
    }


def main() -> int:
    data = build()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {OUT}  providers={len(data['providers'])}  "
          f"size={OUT.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
