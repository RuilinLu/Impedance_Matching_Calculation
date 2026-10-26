"""Provider catalog, model profiles, catalog updates and rollback.

The built-in catalog is data only.  Updates are written to a user-side override
file so application upgrades never destroy a user's edits.  Every network fetch
is restricted to http(s) and public hosts.
"""

from __future__ import annotations

import copy
import html
import ipaddress
import json
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PATH = Path(__file__).resolve().parent / "providers.json"

DEFAULT_PROFILE: Dict[str, Any] = {
    "context": 128000,
    "max_output": 4096,
    "vision": False,
    "audio": False,
    "tool_call": True,
    "json_output": True,
    "reasoning": False,
    "responses_api": False,
    "anthropic_api": False,
    "fim": False,
    "concurrency": 0,
    "release": "",
    "notes": "",
    "pricing": {
        "currency": "CNY",
        "input_cache_hit": 0.0,
        "input_cache_miss": 0.0,
        "output": 0.0,
    },
}

_MODEL_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/+\-]{2,80}")
_KNOWN_MODEL_RE = re.compile(
    r"\b(?:gpt|o[1-9]|claude|gemini|deepseek|qwen|glm|kimi|moonshot|ernie|hunyuan|"
    r"doubao|minimax|abab|yi|step|baichuan|spark|grok|mistral|pixtral|llama|"
    r"qwen|command|nova|jamba|sonar)[A-Za-z0-9_.:/+\-]{1,70}",
    re.I,
)


# ---------------------------------------------------------------------------
# Paths and loading
# ---------------------------------------------------------------------------

def _config():
    from . import config
    return config


def override_path() -> Path:
    cfg = _config()
    return cfg.CATALOG_DIR / "providers_override.json"


def backup_path() -> Path:
    cfg = _config()
    return cfg.CATALOG_DIR / "providers_override.bak.json"


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def _merge_model(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    for key, value in (patch or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge_model(out[key], value)
        elif value is not None:
            out[key] = value
    return out


def _merge_provider(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    patch = copy.deepcopy(patch or {})
    patch_models = patch.pop("models", None)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge_model(out[key], value)
        elif value is not None:
            out[key] = value
    if isinstance(patch_models, list):
        existing = {str(m.get("id")): m for m in out.get("models", []) if isinstance(m, dict)}
        for model in patch_models:
            if not isinstance(model, dict) or not model.get("id"):
                continue
            mid = str(model["id"])
            if mid in existing:
                existing[mid] = _merge_model(existing[mid], model)
            else:
                existing[mid] = _merge_model({}, model)
        out["models"] = list(existing.values())
    return out


def load() -> Dict[str, Any]:
    base = _read_json(PATH)
    if not base.get("providers"):
        base = {"version": "0", "providers": []}
    patch = _read_json(override_path())
    if patch.get("providers"):
        by_id = {str(p.get("id")): p for p in base.get("providers", []) if isinstance(p, dict)}
        order = [str(p.get("id")) for p in base.get("providers", []) if isinstance(p, dict)]
        for provider in patch.get("providers", []):
            if not isinstance(provider, dict) or not provider.get("id"):
                continue
            pid = str(provider["id"])
            if pid in by_id:
                by_id[pid] = _merge_provider(by_id[pid], provider)
            else:
                by_id[pid] = _merge_provider({}, provider)
                order.append(pid)
        base = copy.deepcopy(base)
        base["providers"] = [by_id[pid] for pid in order if pid in by_id]
        base["override"] = {
            "updated_at": patch.get("updated_at", ""),
            "source": patch.get("source", ""),
            "warnings": patch.get("warnings", []),
            "version": patch.get("version", ""),
        }
    return base


def all() -> List[Dict[str, Any]]:
    return list(load().get("providers") or [])


def find(provider_id: str) -> Optional[Dict[str, Any]]:
    pid = str(provider_id or "").strip()
    if not pid:
        return None
    for item in all():
        if item.get("id") == pid:
            return item
    return None


def models_of(provider_id: str) -> List[Dict[str, Any]]:
    provider = find(provider_id) or {}
    return list(provider.get("models") or [])


def model_meta(provider_id: str, model_id: str) -> Dict[str, Any]:
    provider = find(provider_id) or {}
    for model in provider.get("models", []):
        if str(model.get("id")) == str(model_id):
            merged = _merge_model(DEFAULT_PROFILE, model)
            merged["provider"] = provider.get("id", provider_id)
            merged["provider_name"] = provider.get("name_zh") or provider.get("name") or provider_id
            merged["pricing_schedule"] = provider.get("pricing_schedule") or {}
            return merged
    merged = copy.deepcopy(DEFAULT_PROFILE)
    merged.update({"id": model_id, "name": model_id,
                   "provider": provider_id,
                   "provider_name": provider.get("name_zh") or provider_id})
    merged["pricing_schedule"] = provider.get("pricing_schedule") or {}
    return merged


def profile(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve the active model profile: catalog, then user overrides."""
    llm = (cfg or {}).get("llm", {})
    provider_id = str(llm.get("provider") or "")
    model_id = str(llm.get("model") or "")
    base = model_meta(provider_id, model_id)
    overrides = llm.get("profiles") or {}
    saved = overrides.get(f"{provider_id}/{model_id}") if isinstance(overrides, dict) else None
    if not isinstance(saved, dict):
        saved = llm.get("model_profile") if isinstance(llm.get("model_profile"), dict) else {}
    merged = _merge_model(base, saved or {})
    pricing = merged.get("pricing")
    if not isinstance(pricing, dict):
        pricing = copy.deepcopy(DEFAULT_PROFILE["pricing"])
    for key in ("input_cache_hit", "input_cache_miss", "output"):
        try:
            pricing[key] = float(pricing.get(key, 0) or 0)
        except (TypeError, ValueError):
            pricing[key] = 0.0
    for bucket in ("peak", "off_peak"):
        if isinstance(pricing.get(bucket), dict):
            for key in ("input_cache_hit", "input_cache_miss", "output"):
                try:
                    pricing[bucket][key] = float(pricing[bucket].get(key, 0) or 0)
                except (TypeError, ValueError):
                    pricing[bucket][key] = 0.0
    merged["pricing"] = pricing
    return merged


def defaults(provider_id: str) -> Dict[str, Any]:
    item = find(provider_id)
    if not item:
        return {}
    return {
        "provider": item.get("id", ""),
        "provider_name": item.get("name_zh") or item.get("name") or item.get("id"),
        "base_url": item.get("api", ""),
        "base_url_openai": item.get("api", ""),
        "base_url_anthropic": item.get("api_anthropic", ""),
        "auth_header": item.get("auth_header", "Authorization"),
        "auth_prefix": item.get("auth_prefix", "Bearer "),
        "api_style": item.get("api_style", "openai"),
        "chat_path": item.get("chat_path", ""),
        "models": item.get("models", []),
        "doc": item.get("doc", ""),
        "release_url": item.get("release_url", ""),
        "env": item.get("env", []),
        "notes": item.get("notes", ""),
    }


# ---------------------------------------------------------------------------
# Validation and persistence
# ---------------------------------------------------------------------------

def _valid_provider(provider: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(provider, dict):
        return False, "provider is not an object"
    pid = str(provider.get("id") or "")
    if not re.fullmatch(r"[a-z0-9_\-]{2,32}", pid):
        return False, f"invalid provider id: {pid}"
    models = provider.get("models")
    if models is not None and not isinstance(models, list):
        return False, f"{pid}: models must be a list"
    if isinstance(models, list) and len(models) > 500:
        return False, f"{pid}: too many models"
    for model in models or []:
        if not isinstance(model, dict) or not model.get("id"):
            return False, f"{pid}: model without id"
        mid = str(model["id"])
        if len(mid) > 120 or not re.fullmatch(r"[\w./:+@\-]{1,120}", mid):
            return False, f"{pid}: invalid model id {mid!r}"
        for key, maximum in (("context", 20_000_000), ("max_output", 2_000_000),
                             ("concurrency", 10_000_000)):
            if key in model:
                try:
                    value = int(model[key])
                except (TypeError, ValueError):
                    return False, f"{pid}/{mid}: {key} must be an integer"
                if value < 0 or value > maximum:
                    return False, f"{pid}/{mid}: {key} out of range"
        pricing = model.get("pricing")
        if pricing is not None and not isinstance(pricing, dict):
            return False, f"{pid}/{mid}: pricing must be an object"
    return True, ""


def _sanitize_provider(provider: Dict[str, Any]) -> Dict[str, Any]:
    allowed_provider = {
        "id", "name", "name_zh", "featured", "country", "api", "api_anthropic",
        "api_style", "chat_path", "auth_header", "auth_prefix", "env", "doc",
        "release_url", "models_url", "notes", "pricing_schedule",
    }
    allowed_model = set(DEFAULT_PROFILE.keys()) | {"id", "name"}
    out = {k: copy.deepcopy(v) for k, v in provider.items() if k in allowed_provider}
    out["id"] = str(provider.get("id"))
    models = []
    for model in provider.get("models") or []:
        item = {k: copy.deepcopy(v) for k, v in model.items() if k in allowed_model}
        item["id"] = str(model.get("id"))
        models.append(item)
    if models:
        out["models"] = models
    return out


def save_patch(providers: List[Dict[str, Any]], source: str,
               warnings: Optional[List[str]] = None) -> Dict[str, Any]:
    clean = []
    errors = []
    warnings = list(warnings or [])
    for provider in providers or []:
        ok, message = _valid_provider(provider)
        if not ok and isinstance(provider, dict) and isinstance(provider.get("models"), list):
            # Keep the provider but drop only the malformed model entries.
            filtered = dict(provider)
            good_models = []
            for model in provider.get("models") or []:
                single = {"id": provider.get("id"), "models": [model]}
                valid, why = _valid_provider(single)
                if valid:
                    good_models.append(model)
                else:
                    warnings.append(f"{provider.get('id')}: 跳过无效模型（{why}）")
            filtered["models"] = good_models
            ok, message = _valid_provider(filtered)
            if ok:
                provider = filtered
        if ok:
            clean.append(_sanitize_provider(provider))
        else:
            errors.append(message)
    if not clean:
        return {"ok": False, "message": "没有可写入的有效厂商条目",
                "errors": errors[:20], "warnings": warnings[:40]}
    current = _read_json(override_path())
    if current:
        try:
            backup_path().write_text(
                json.dumps(current, ensure_ascii=False, indent=1), encoding="utf-8")
        except Exception:
            pass
    merged = {str(p.get("id")): p for p in current.get("providers", [])
              if isinstance(p, dict) and p.get("id")}
    for provider in clean:
        pid = str(provider["id"])
        merged[pid] = _merge_provider(merged.get(pid, {"id": pid}), provider)
    payload = {
        "version": "override",
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "source": source,
        "warnings": (warnings or [])[:40],
        "providers": list(merged.values()),
    }
    _write_json(override_path(), payload)
    return {"ok": True, "providers": len(clean), "warnings": warnings or [],
            "errors": errors[:20], "path": str(override_path())}


def rollback() -> Dict[str, Any]:
    if not backup_path().exists():
        return {"ok": False, "message": "没有可回滚的目录备份"}
    backup = _read_json(backup_path())
    if not backup:
        return {"ok": False, "message": "备份文件损坏"}
    _write_json(override_path(), backup)
    return {"ok": True, "message": "已恢复上一版厂商目录",
            "updated_at": backup.get("updated_at", "")}


def reset_override() -> Dict[str, Any]:
    path = override_path()
    if path.exists():
        try:
            backup_path().write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception:
            pass
        path.unlink()
    return {"ok": True, "message": "已恢复内置目录（原覆盖已备份）"}


# ---------------------------------------------------------------------------
# Public HTTP fetching
# ---------------------------------------------------------------------------

def _validate_public_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("只允许 http/https 地址")
    if not parsed.hostname:
        raise ValueError("缺少主机名")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    infos = socket.getaddrinfo(parsed.hostname, port, proto=socket.IPPROTO_TCP)
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_reserved
                or ip.is_link_local or ip.is_multicast or ip.is_unspecified):
            raise ValueError(f"{parsed.hostname} 解析到非公网地址，已拒绝")
    return url


class _PublicRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _validate_public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _fetch(url: str, timeout: int = 12, max_bytes: int = 3_000_000,
           headers: Optional[Dict[str, str]] = None) -> str:
    _validate_public_url(url)
    request = urllib.request.Request(
        url, headers={"User-Agent": "ImpedanceMatchingAI/4.3 (+catalog-update)",
                      "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
                      **(headers or {})})
    opener = urllib.request.build_opener(_PublicRedirectHandler())
    with opener.open(request, timeout=timeout) as response:
        raw = response.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raw = raw[:max_bytes]
    return raw.decode("utf-8", errors="replace")


def _strip_html(text: str) -> str:
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_model_ids(text: str) -> List[str]:
    found = []
    for match in _KNOWN_MODEL_RE.findall(text or ""):
        item = match.strip(".,;:()[]{}<>\"'")
        if 3 <= len(item) <= 90 and item.lower() not in {x.lower() for x in found}:
            found.append(item)
    return found[:80]


# ---------------------------------------------------------------------------
# Update sources
# ---------------------------------------------------------------------------

MODELS_DEV_URL = "https://models.dev/api.json"
PROVIDER_ALIASES = {
    "openai": ["openai"],
    "anthropic": ["anthropic"],
    "google": ["google", "google-vertex", "google-generative-ai"],
    "deepseek": ["deepseek"],
    "alibaba": ["alibaba", "dashscope", "qwen"],
    "zhipu": ["zhipuai", "zhipu", "bigmodel"],
    "moonshot": ["moonshot", "moonshotai"],
    "baidu": ["baidu", "qianfan"],
    "tencent": ["tencent", "hunyuan"],
    "bytedance": ["bytedance", "volcengine", "doubao"],
    "minimax": ["minimax"],
    "01ai": ["01ai", "lingyiwanwu", "yi"],
    "stepfun": ["stepfun"],
    "baichuan": ["baichuan"],
    "iflytek": ["iflytek", "spark"],
    "siliconflow": ["siliconflow"],
    "openrouter": ["openrouter"],
    "xai": ["xai", "x-ai"],
    "mistral": ["mistral"],
    "groq": ["groq"],
}


def _models_dev_index(data: Any) -> Dict[str, Dict[str, Any]]:
    """Normalise models.dev's provider/model JSON into a lookup map."""
    providers: Dict[str, Dict[str, Any]] = {}
    if isinstance(data, dict):
        for key, value in data.items():
            if not isinstance(value, dict):
                continue
            pid = str(value.get("id") or key)
            models_obj = value.get("models")
            ids: List[str] = []
            if isinstance(models_obj, dict):
                for mid, meta in models_obj.items():
                    if isinstance(meta, dict):
                        ids.append(str(meta.get("id") or mid))
                    else:
                        ids.append(str(mid))
            elif isinstance(models_obj, list):
                for meta in models_obj:
                    if isinstance(meta, dict) and meta.get("id"):
                        ids.append(str(meta["id"]))
                    elif isinstance(meta, str):
                        ids.append(meta)
            providers[pid.lower()] = {
                "id": pid,
                "name": value.get("name") or pid,
                "models": ids,
            }
    elif isinstance(data, list):
        for value in data:
            if isinstance(value, dict) and value.get("models"):
                providers[str(value.get("id") or "").lower()] = value
    return providers


def _match_models_dev(pid: str, index: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for alias in PROVIDER_ALIASES.get(pid, [pid]):
        if alias.lower() in index:
            return index[alias.lower()]
    for key, value in index.items():
        if pid.lower() in key or key in pid.lower():
            return value
    return None


def update_from_models_dev() -> Dict[str, Any]:
    warnings: List[str] = []
    try:
        raw = _fetch(MODELS_DEV_URL, timeout=15, max_bytes=6_000_000)
        data = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "message": f"读取 models.dev 失败：{exc}",
                "warnings": [str(exc)]}
    index = _models_dev_index(data)
    patches = []
    for provider in all():
        pid = str(provider.get("id"))
        match = _match_models_dev(pid, index)
        if not match or not match.get("models"):
            warnings.append(f"{pid}: models.dev 中未找到对应条目")
            continue
        existing = {str(m.get("id")) for m in provider.get("models", [])}
        new_models = [{"id": mid, "name": mid} for mid in match["models"]
                      if mid not in existing]
        if new_models:
            patches.append({"id": pid, "models": new_models})
    if not patches:
        return {"ok": True, "message": "目录已是最新，没有发现新模型",
                "added": 0, "warnings": warnings}
    result = save_patch(patches, source="models.dev",
                        warnings=warnings)
    result["added"] = sum(len(p.get("models", [])) for p in patches)
    result["message"] = f"已合并 {result['added']} 个新模型（保留原有能力与价格）"
    return result


def update_from_provider_api(cfg: Dict[str, Any]) -> Dict[str, Any]:
    from . import llm
    active = str((cfg.get("llm") or {}).get("provider") or "")
    key = str((cfg.get("llm") or {}).get("api_key") or "")
    if not active or not key:
        return {"ok": False, "message": "请先配置当前服务商与 API Key"}
    provider = find(active) or {}
    url = provider.get("models_url") or ""
    if not url:
        style = str((cfg.get("llm") or {}).get("api_style") or "openai")
        try:
            url = llm.models_url(cfg)
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "message": f"无法推导模型列表地址：{exc}"}
    try:
        _validate_public_url(url)
        headers = {}
        auth = str((cfg.get("llm") or {}).get("auth_header") or "Authorization")
        prefix = str((cfg.get("llm") or {}).get("auth_prefix") or "Bearer ")
        headers[auth] = prefix + key
        if (cfg.get("llm") or {}).get("api_style") == "anthropic":
            headers["anthropic-version"] = "2023-06-01"
        raw = _fetch(url, timeout=20, max_bytes=2_000_000, headers=headers)
        data = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "message": f"读取官方模型列表失败：{exc}"}
    items = data.get("data") if isinstance(data, dict) else data
    ids = []
    for item in items or []:
        if isinstance(item, dict) and item.get("id"):
            ids.append(str(item["id"]))
        elif isinstance(item, str):
            ids.append(item)
    ids = [x for x in ids if x][:400]
    if not ids:
        return {"ok": False, "message": "官方接口没有返回模型"}
    existing = {str(m.get("id")) for m in provider.get("models", [])}
    new_models = [{"id": mid, "name": mid} for mid in ids if mid not in existing]
    result = save_patch([{"id": active, "models": new_models}],
                        source=f"{active} /models endpoint")
    result["added"] = len(new_models)
    result["models"] = ids
    result["message"] = f"已读取 {len(ids)} 个官方模型，新增 {len(new_models)} 个"
    return result


def fetch_announcements(provider_id: str) -> Dict[str, Any]:
    provider = find(provider_id)
    if not provider:
        return {"ok": False, "message": "未知服务商"}
    texts = []
    warnings = []
    candidates: List[str] = []
    for key in ("release_url", "doc"):
        url = provider.get(key) or ""
        if not url:
            continue
        try:
            raw = _fetch(url, timeout=10, max_bytes=900_000)
            text = _strip_html(raw) if "<" in raw[:500] else raw
            if text:
                texts.append(f"[{key}] {url}\n{text[:12000]}")
                candidates.extend(_extract_model_ids(text))
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"{url}: {exc}")
    seen = set()
    unique = []
    for item in candidates:
        if item.lower() not in seen:
            seen.add(item.lower())
            unique.append(item)
    return {"ok": True, "provider": provider_id,
            "excerpt": "\n\n".join(texts)[:24000],
            "candidates": unique[:80], "warnings": warnings}


def ai_update(cfg: Dict[str, Any], provider_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    from . import llm
    if not (cfg.get("llm") or {}).get("api_key"):
        return {"ok": False, "message": "AI 校对更新需要先配置模型服务与 API Key"}
    ids = [p for p in (provider_ids or []) if find(p)]
    if not ids:
        active = (cfg.get("llm") or {}).get("provider")
        ids = [active] if active and find(active) else [
            p["id"] for p in all() if p.get("featured")][:8]
    excerpts = []
    warnings = []
    for pid in ids[:8]:
        info = fetch_announcements(pid)
        if not info.get("ok"):
            warnings.append(f"{pid}: {info.get('message')}")
            continue
        warnings.extend(info.get("warnings") or [])
        provider = find(pid) or {}
        models = [m.get("id") for m in provider.get("models", [])][:60]
        excerpts.append(
            f"### {pid}\n现有模型：{', '.join(str(m) for m in models)}\n"
            f"候选模型：{', '.join(info.get('candidates') or [])[:3000]}\n"
            f"公告摘录：{info.get('excerpt', '')[:6000]}")
    if not excerpts:
        return {"ok": False, "message": "没有抓取到可用的官方公告",
                "warnings": warnings}
    prompt = (
        "你是模型目录校对助手。根据下面的官方公告摘录与现有模型列表，输出严格 JSON："
        '{"providers":[{"id":"厂商id","models":[{"id":"模型id","name":"名称",'
        '"context":123456,"max_output":8192,"vision":true,"tool_call":true,'
        '"json_output":true,"reasoning":false,"pricing":{"currency":"CNY",'
        '"input_cache_hit":0.1,"input_cache_miss":1.0,"output":4.0}}]}]}。'
        "只输出新增或需要修正的模型；不要编造公告中没有的模型；不确定的价格留空。"
        "只输出 JSON，不要 Markdown。\n\n" + "\n\n".join(excerpts)[:20000]
    )
    try:
        resp = llm.chat(cfg, [
            {"role": "system", "content": "只输出严格 JSON，不要解释。"},
            {"role": "user", "content": prompt},
        ], timeout=180)
        raw = (resp.get("content") or "").strip()
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            return {"ok": False, "message": "模型没有返回 JSON", "warnings": warnings}
        data = json.loads(match.group(0))
        providers = data.get("providers") if isinstance(data, dict) else None
        if not isinstance(providers, list):
            return {"ok": False, "message": "JSON 缺少 providers 数组", "warnings": warnings}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "message": f"AI 校对失败：{exc}", "warnings": warnings}
    result = save_patch(providers, source="AI-assisted review",
                        warnings=warnings + ["AI 输出可能出错，请逐项核对后再使用"])
    result["message"] = ("AI 已生成目录补丁；请核对模型 ID、能力与价格。"
                         if result.get("ok") else result.get("message", "更新失败"))
    result["ai_model"] = resp.get("model") if isinstance(resp, dict) else ""
    return result


def update_summary() -> Dict[str, Any]:
    data = load()
    override = _read_json(override_path())
    return {
        "ok": True,
        "version": data.get("version", ""),
        "updated": data.get("updated", ""),
        "note": data.get("note", ""),
        "providers": len(data.get("providers") or []),
        "models": sum(len(p.get("models") or []) for p in data.get("providers") or []),
        "override": data.get("override") or {},
        "override_path": str(override_path()),
        "backup_available": backup_path().exists(),
        "override_updated_at": override.get("updated_at", ""),
    }
