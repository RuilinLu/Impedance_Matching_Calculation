"""Configuration, path discovery and runtime status."""

from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PACKAGE_DIR = Path(__file__).resolve().parent
FROZEN = bool(getattr(sys, "frozen", False))

if FROZEN:
    # PyInstaller one-file: __file__ lives in the temporary _MEIPASS directory.
    # User data lives under %LOCALAPPDATA%\ImpedanceMatchingAI.
    APP_DIR = PACKAGE_DIR.parent
    EXE_DIR = Path(sys.executable).resolve().parent
    PROJECT_ROOT = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "ImpedanceMatchingAI"
    DATA_DIR = PROJECT_ROOT / "data"
    WEB_DIR = PACKAGE_DIR / "web"
else:
    APP_DIR = PACKAGE_DIR.parent
    EXE_DIR = APP_DIR.parent
    PROJECT_ROOT = APP_DIR.parent
    DATA_DIR = PROJECT_ROOT / "data"
    WEB_DIR = PACKAGE_DIR / "web"

UPLOAD_DIR = DATA_DIR / "uploads"
REPORT_DIR = DATA_DIR / "reports"
LIBRARY_DIR = DATA_DIR / "library"
CATALOG_DIR = DATA_DIR / "catalog"
CONFIG_PATH = DATA_DIR / "config.json"
USAGE_PATH = DATA_DIR / "usage.jsonl"

# Textbooks are user-supplied and deliberately not part of the repository.
LIBRARY_SOURCE_DIRS: List[Path] = []
for _candidate in (
    PROJECT_ROOT / "TextBook",
    EXE_DIR / "TextBook",
    APP_DIR / "TextBook",
    APP_DIR.parent / "TextBook",
):
    if _candidate not in LIBRARY_SOURCE_DIRS:
        LIBRARY_SOURCE_DIRS.append(_candidate)

VERSION = "4.3.0"
RELEASE_DATE = "2026-10-27"
APP_NAME = "Impedance Matching AI"
APP_NAME_ZH = "阻抗匹配智能计算与仿真"
PROJECT_URL = "https://github.com/SkywalkerHolmes/Impedance_Matching_Calculation"
TEAM = [
    {"name": "Nova（诺瓦）", "role": "项目负责人 / 计算内核与智能体架构"},
    {"name": "Echo（回声）", "role": "数值算法与仿真验证"},
    {"name": "Iris（鸢尾）", "role": "交互设计、可视化与文档"},
    {"name": "Lumen（流明）", "role": "测试、教材整理与用户研究"},
]
AUTHOR_EMAILS: List[str] = []


def ensure_dirs() -> None:
    for path in (DATA_DIR, UPLOAD_DIR, REPORT_DIR, LIBRARY_DIR,
                 LIBRARY_DIR / "books", LIBRARY_DIR / "cache", CATALOG_DIR):
        path.mkdir(parents=True, exist_ok=True)


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def default_config() -> Dict[str, Any]:
    return {
        "llm": {
            "provider": "",
            "provider_name": "",
            "protocol": "openai",
            "base_url": "",
            "base_url_openai": "",
            "base_url_anthropic": "",
            "api_key": "",
            "model": "",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "api_style": "openai",
            "chat_path": "",
            "extra_headers": {},
            "temperature": 0.25,
            "max_tokens": 16384,
            "reasoning_effort": "",
            "thinking_budget": 0,
            "model_profile": {},
            "profiles": {},
        },
        "ui": {
            "lang": "zh",
            "last_topology": "l_right",
            "animation_speed": 45,
            "assistant_open": False,
            "library_zoom": 1.2,
        },
        "library": {
            "ocr_first_pages": 2,
            "search_limit": 24,
            "auto_index": True,
        },
        "usage": {
            "auto_peak": True,
            "currency_display": "auto",
        },
    }


def deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    for key, value in (update or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config() -> Dict[str, Any]:
    ensure_dirs()
    cfg = default_config()
    if CONFIG_PATH.exists():
        try:
            stored = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            cfg = deep_merge(cfg, stored)
        except Exception:
            pass
    env_key = _env("LLM_API_KEY")
    env_base = _env("LLM_BASE_URL")
    env_model = _env("LLM_MODEL")
    if env_key and not cfg["llm"].get("api_key"):
        cfg["llm"]["api_key"] = env_key
    if env_base:
        cfg["llm"]["base_url"] = env_base
        if not cfg["llm"].get("provider"):
            cfg["llm"]["provider"] = "custom"
            cfg["llm"]["provider_name"] = "Custom"
    if env_model:
        cfg["llm"]["model"] = env_model
    return cfg


def save_config(update: Dict[str, Any]) -> Dict[str, Any]:
    cfg = load_config()
    llm = (update or {}).get("llm", {})
    if isinstance(llm, dict):
        if llm.get("clear_key") and not llm.get("api_key"):
            llm["api_key"] = ""
        llm.pop("clear_key", None)
        if llm.get("api_key") in (None, "", "******", "***"):
            llm.pop("api_key", None)
        pid = str(llm.get("provider") or "")
        if pid and pid != "custom":
            from . import providers as provider_catalog
            meta = provider_catalog.defaults(pid)
            if meta:
                llm.setdefault("provider_name", meta["provider_name"])
                if not llm.get("base_url"):
                    llm["base_url"] = meta["base_url"]
                for field in ("auth_header", "auth_prefix", "api_style", "chat_path"):
                    if not llm.get(field):
                        llm[field] = meta[field]
    merged = deep_merge(cfg, update)
    ensure_dirs()
    CONFIG_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        os.chmod(CONFIG_PATH, 0o600)
    except Exception:
        pass
    return merged


def public_config(cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cfg = copy.deepcopy(cfg or load_config())
    key = cfg.get("llm", {}).get("api_key", "")
    cfg["llm"]["api_key"] = ""
    cfg["llm"]["has_key"] = bool(key)
    cfg["llm"]["key_hint"] = (key[:4] + "…" + key[-4:]) if len(key) >= 10 else ("已配置" if key else "")
    return cfg


def llm_status(cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cfg = cfg or load_config()
    llm = cfg.get("llm", {})
    return {
        "configured": bool(llm.get("provider") and llm.get("base_url")
                           and llm.get("api_key") and llm.get("model")),
        "base_url": llm.get("base_url"),
        "model": llm.get("model"),
        "provider": llm.get("provider"),
        "provider_name": llm.get("provider_name"),
        "protocol": llm.get("protocol", "openai"),
        "api_style": llm.get("api_style", "openai"),
        "has_key": bool(llm.get("api_key")),
    }


def mcp_launch() -> tuple:
    """Return the console executable that speaks MCP over stdio."""
    if FROZEN:
        exe = Path(sys.executable).resolve()
        for name in ("ImpedanceMatchingAI_MCP.exe", "ImpedanceMatchingAI.exe"):
            candidate = exe.with_name(name)
            if candidate.exists():
                return str(candidate), ["--mcp"]
        return str(exe), ["--mcp"]
    return sys.executable, [str(PROJECT_ROOT / "app" / "run_mcp.py")]


def status() -> Dict[str, Any]:
    cfg = load_config()
    command, args = mcp_launch()
    return {
        "name": APP_NAME,
        "name_zh": APP_NAME_ZH,
        "version": VERSION,
        "release_date": RELEASE_DATE,
        "llm": llm_status(cfg),
        "mcp": {
            "transport": "stdio",
            "command": command,
            "args": args,
            "script": args[0] if not FROZEN and args else "",
            "http": "http://127.0.0.1:8790/mcp",
            "legacy_sse": "http://127.0.0.1:8790/sse",
        },
        "team": TEAM,
        "contacts": AUTHOR_EMAILS,
        "project_url": PROJECT_URL,
        "python": sys.version.split()[0],
        "project_root": str(PROJECT_ROOT),
        "frozen": FROZEN,
        "executable": str(Path(sys.executable).resolve()),
        "library_dirs": [str(p) for p in LIBRARY_SOURCE_DIRS],
    }


def mcp_client_config() -> Dict[str, Any]:
    command, args = mcp_launch()
    return {
        "impedance-matching-ai": {
            "type": "stdio",
            "command": command,
            "args": args,
            "env": {
                "PYTHONUNBUFFERED": "1",
                "PYTHONIOENCODING": "utf-8",
            },
            "timeoutMs": 180000,
        }
    }
