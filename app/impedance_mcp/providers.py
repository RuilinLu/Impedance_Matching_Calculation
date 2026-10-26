"""Built-in provider catalog generated from models.dev.

The catalog is data-only: endpoints, model IDs, environment variable names and
documentation links.  It never contains API keys.  Users choose a provider in
the Settings dialog and supply their own credentials.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

PATH = Path(__file__).resolve().parent / "providers.json"


@lru_cache(maxsize=1)
def load() -> Dict[str, Any]:
    try:
        return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"version": "", "providers": []}


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


def defaults(provider_id: str) -> Dict[str, Any]:
    item = find(provider_id)
    if not item:
        return {}
    return {
        "provider": item.get("id", ""),
        "provider_name": item.get("name_zh") or item.get("name") or item.get("id"),
        "base_url": item.get("api", ""),
        "auth_header": item.get("auth_header", "Authorization"),
        "auth_prefix": item.get("auth_prefix", "Bearer "),
        "api_style": item.get("api_style", "openai"),
        "chat_path": item.get("chat_path", ""),
        "models": item.get("models", []),
        "doc": item.get("doc", ""),
        "env": item.get("env", []),
        "notes": item.get("notes", ""),
    }
