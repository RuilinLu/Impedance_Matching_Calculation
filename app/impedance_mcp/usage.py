"""Token, cache, context and cost accounting for model calls."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import config

_LOCK = threading.Lock()
_UNIT = 1_000_000.0


def normalize_usage(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalise OpenAI / Anthropic / DeepSeek usage payloads."""
    raw = raw or {}
    prompt = int(raw.get("prompt_tokens") or raw.get("input_tokens") or 0)
    completion = int(raw.get("completion_tokens") or raw.get("output_tokens") or 0)
    total = int(raw.get("total_tokens") or (prompt + completion))
    cached = int(raw.get("cached_tokens") or 0)
    details = raw.get("prompt_tokens_details")
    if isinstance(details, dict):
        cached = max(cached, int(details.get("cached_tokens") or 0))
    cached = max(cached, int(raw.get("prompt_cache_hit_tokens") or 0))
    cached = max(cached, int(raw.get("cache_read_input_tokens") or 0))
    cache_creation = int(raw.get("cache_creation_input_tokens") or 0)
    reasoning = 0
    comp_details = raw.get("completion_tokens_details")
    if isinstance(comp_details, dict):
        reasoning = int(comp_details.get("reasoning_tokens") or 0)
    cached = max(0, min(cached, prompt))
    return {
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": total,
        "cached_tokens": cached,
        "cache_creation_tokens": max(0, cache_creation),
        "reasoning_tokens": max(0, reasoning),
        "prompt_uncached_tokens": max(0, prompt - cached),
    }


def add_usage(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a or {})
    for key in ("prompt_tokens", "completion_tokens", "total_tokens",
                "cached_tokens", "cache_creation_tokens", "reasoning_tokens",
                "prompt_uncached_tokens"):
        out[key] = int(out.get(key, 0) or 0) + int((b or {}).get(key, 0) or 0)
    return out


def _minutes(value: str, default: int) -> int:
    try:
        hour, minute = str(value).split(":", 1)
        return int(hour) * 60 + int(minute)
    except Exception:
        return default


def _in_off_peak(schedule: Dict[str, Any], when: Optional[datetime] = None) -> bool:
    if not isinstance(schedule, dict):
        return False
    when = when or datetime.now()
    start = _minutes(schedule.get("off_peak_start", ""), 30)
    end = _minutes(schedule.get("off_peak_end", ""), 510)
    now = when.hour * 60 + when.minute
    if start <= end:
        return start <= now < end
    return now >= start or now < end


def _pick_price(profile: Dict[str, Any], when: Optional[datetime] = None,
                auto_peak: bool = True) -> tuple:
    pricing = profile.get("pricing") or {}
    base = {
        "input_cache_hit": float(pricing.get("input_cache_hit", 0) or 0),
        "input_cache_miss": float(pricing.get("input_cache_miss", 0) or 0),
        "output": float(pricing.get("output", 0) or 0),
    }
    schedule = profile.get("pricing_schedule") or {}
    if auto_peak and schedule and isinstance(pricing.get("peak"), dict):
        off = _in_off_peak(schedule, when)
        bucket = pricing.get("off_peak") if off else pricing.get("peak")
        if isinstance(bucket, dict):
            return {
                "input_cache_hit": float(bucket.get("input_cache_hit", base["input_cache_hit"]) or 0),
                "input_cache_miss": float(bucket.get("input_cache_miss", base["input_cache_miss"]) or 0),
                "output": float(bucket.get("output", base["output"]) or 0),
            }, ("off_peak" if off else "peak")
    return base, "base"


def compute_cost(profile: Dict[str, Any], usage: Dict[str, Any],
                 when: Optional[datetime] = None,
                 auto_peak: bool = True) -> Dict[str, Any]:
    usage = normalize_usage(usage)
    price, bucket = _pick_price(profile or {}, when, auto_peak)
    cached = usage["cached_tokens"]
    uncached = usage["prompt_uncached_tokens"]
    output = usage["completion_tokens"]
    cache_cost = cached * price["input_cache_hit"] / _UNIT
    input_cost = uncached * price["input_cache_miss"] / _UNIT
    output_cost = output * price["output"] / _UNIT
    context = int((profile or {}).get("context", 0) or 0)
    prompt = usage["prompt_tokens"]
    return {
        "currency": str(((profile or {}).get("pricing") or {}).get("currency", "CNY")),
        "price_bucket": bucket,
        "price": price,
        "cache_cost": round(cache_cost, 8),
        "input_cost": round(input_cost, 8),
        "output_cost": round(output_cost, 8),
        "total_cost": round(cache_cost + input_cost + output_cost, 8),
        "cache_hit_rate": round(cached / prompt, 6) if prompt else 0.0,
        "context_pct": round(prompt / context, 6) if context else 0.0,
        "pricing_configured": bool(price["input_cache_miss"] or price["output"]),
        **usage,
    }


def record(profile: Dict[str, Any], usage: Dict[str, Any], model: str,
           elapsed_s: float = 0.0, source: str = "chat",
           cost: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    stats = cost or compute_cost(profile, usage)
    row = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "provider": (profile or {}).get("provider", ""),
        "model": model or (profile or {}).get("id", ""),
        "source": source,
        "elapsed_s": round(float(elapsed_s or 0), 3),
        "prompt_tokens": stats["prompt_tokens"],
        "completion_tokens": stats["completion_tokens"],
        "cached_tokens": stats["cached_tokens"],
        "total_tokens": stats["total_tokens"],
        "cache_hit_rate": stats["cache_hit_rate"],
        "context_pct": stats["context_pct"],
        "cost": stats["total_cost"],
        "currency": stats["currency"],
        "price_bucket": stats["price_bucket"],
    }
    try:
        config.ensure_dirs()
        with _LOCK:
            with config.USAGE_PATH.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass
    return row


def _rows() -> List[Dict[str, Any]]:
    path = config.USAGE_PATH
    if not path.exists():
        return []
    rows = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except Exception:
                continue
            if isinstance(item, dict):
                rows.append(item)
    except Exception:
        return []
    return rows


def _aggregate(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    out = {
        "requests": len(rows),
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cached_tokens": 0,
        "total_tokens": 0,
        "cost": 0.0,
        "currencies": {},
        "last": rows[-1] if rows else None,
    }
    for row in rows:
        for key in ("prompt_tokens", "completion_tokens", "cached_tokens", "total_tokens"):
            out[key] += int(row.get(key, 0) or 0)
        cost = float(row.get("cost", 0) or 0)
        currency = str(row.get("currency", "CNY"))
        out["cost"] += cost
        out["currencies"][currency] = out["currencies"].get(currency, 0.0) + cost
    out["cache_hit_rate"] = (round(out["cached_tokens"] / out["prompt_tokens"], 6)
                             if out["prompt_tokens"] else 0.0)
    for key in ("cost",):
        out[key] = round(out[key], 6)
    out["currencies"] = {k: round(v, 6) for k, v in out["currencies"].items()}
    return out


def summary(days: Optional[int] = None) -> Dict[str, Any]:
    rows = _rows()
    now = datetime.now()
    today = now.date().isoformat()
    week = (now - timedelta(days=7)).isoformat(timespec="seconds")
    today_rows = [r for r in rows if str(r.get("time", "")).startswith(today)]
    week_rows = [r for r in rows if str(r.get("time", "")) >= week]
    return {
        "ok": True,
        "today": _aggregate(today_rows),
        "week": _aggregate(week_rows),
        "all": _aggregate(rows),
        "recent": rows[-20:][::-1],
        "log_path": str(config.USAGE_PATH),
        "days": days,
    }


def clear() -> Dict[str, Any]:
    path = config.USAGE_PATH
    if path.exists():
        try:
            path.write_text("", encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "message": f"清空失败：{exc}"}
    return {"ok": True, "message": "用量日志已清空"}
