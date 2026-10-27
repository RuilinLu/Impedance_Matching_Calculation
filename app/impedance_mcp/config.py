"""Configuration, path discovery and runtime status.

v4.4.0 separates three locations that used to be conflated:

``INSTALL_DIR``  directory that contains the executable (or the source tree)
``DATA_ROOT``    directory that stores config / uploads / reports / library DB
``PROJECT_ROOT`` alias of ``DATA_ROOT`` kept for backward compatibility

The data root defaults to ``%LOCALAPPDATA%\\ImpedanceMatchingAI`` for the frozen
build and to the project directory for source runs.  A ``data_root.txt`` file
next to the executable can point it elsewhere, which makes a copied installation
keep all of its data together.  Textbook folders are resolved dynamically so
moving the program to another directory automatically moves its bundled
``TextBook`` folder without rewriting stored paths.
"""

from __future__ import annotations

import copy
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PACKAGE_DIR = Path(__file__).resolve().parent
FROZEN = bool(getattr(sys, "frozen", False))

if FROZEN:
    # PyInstaller one-file: __file__ lives in the temporary _MEIPASS directory.
    APP_DIR = PACKAGE_DIR.parent
    EXE_DIR = Path(sys.executable).resolve().parent
    INSTALL_DIR = EXE_DIR
    _DEFAULT_DATA_ROOT = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "ImpedanceMatchingAI"
else:
    APP_DIR = PACKAGE_DIR.parent
    EXE_DIR = APP_DIR.parent
    INSTALL_DIR = APP_DIR.parent
    _DEFAULT_DATA_ROOT = APP_DIR.parent

DATA_ROOT_FILE = INSTALL_DIR / "data_root.txt"


def _read_data_root_file() -> Optional[Path]:
    """Read an optional ``data_root.txt`` placed next to the executable."""
    try:
        if not DATA_ROOT_FILE.is_file():
            return None
        for line in DATA_ROOT_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
            value = line.strip().strip('"')
            if not value or value.startswith("#") or value.startswith(";"):
                continue
            candidate = Path(os.path.expandvars(value)).expanduser()
            if not candidate.is_absolute():
                candidate = INSTALL_DIR / candidate
            return candidate.resolve()
    except Exception:
        return None
    return None


def _resolve_data_root() -> Path:
    env_value = os.environ.get("IMPEDANCE_DATA_ROOT", "").strip()
    if env_value:
        try:
            return Path(os.path.expandvars(env_value)).expanduser().resolve()
        except Exception:
            pass
    marker = _read_data_root_file()
    if marker is not None:
        return marker
    return _DEFAULT_DATA_ROOT


PROJECT_ROOT = _resolve_data_root()
DATA_DIR = PROJECT_ROOT / "data"
WEB_DIR = PACKAGE_DIR / "web"

UPLOAD_DIR = DATA_DIR / "uploads"
REPORT_DIR = DATA_DIR / "reports"
LIBRARY_DIR = DATA_DIR / "library"
CATALOG_DIR = DATA_DIR / "catalog"
CONFIG_PATH = DATA_DIR / "config.json"
USAGE_PATH = DATA_DIR / "usage.jsonl"
UPDATE_CACHE_PATH = DATA_DIR / "update_cache.json"
UPLOAD_CHUNK_DIR = UPLOAD_DIR / "chunks"

# Built-in textbook locations.  They are resolved on every call so relocating the
# installation or changing ``data_root.txt`` is reflected immediately.
BUILTIN_SOURCES = (
    ("install_textbook", "程序目录 TextBook", lambda: INSTALL_DIR / "TextBook"),
    ("data_textbook", "用户数据 TextBook", lambda: PROJECT_ROOT / "TextBook"),
    ("library_books", "应用内添加教材", lambda: LIBRARY_DIR / "books"),
)

# Backward-compatible snapshot.  New code should call library_source_paths().
LIBRARY_SOURCE_DIRS: List[Path] = []
for _kind, _label, _resolver in BUILTIN_SOURCES:
    try:
        LIBRARY_SOURCE_DIRS.append(_resolver())
    except Exception:
        pass

VERSION = "4.4.0"
RELEASE_DATE = "2026-10-27"
SETTINGS_VERSION = 4
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
                 LIBRARY_DIR / "books", LIBRARY_DIR / "cache", CATALOG_DIR,
                 UPLOAD_CHUNK_DIR):
        path.mkdir(parents=True, exist_ok=True)


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def default_search_dirs() -> List[Dict[str, Any]]:
    return [{"kind": kind, "enabled": True} for kind, _label, _resolver in BUILTIN_SOURCES]


def default_config() -> Dict[str, Any]:
    return {
        "settings_version": SETTINGS_VERSION,
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
            "show_thinking": False,
            "show_citations": False,
            "library_split": 300,
            "library_text_height": 220,
            "scan_points": 10000,
            "stress_sweep_enabled": True,
            "stress_sweep_points": 21,
            "stress_freq_span": 0.2,
        },
        "library": {
            "ocr_first_pages": 2,
            "search_limit": 24,
            "auto_index": True,
            "search_dirs": default_search_dirs(),
            "sources_seeded": True,
        },
        "update": {
            "auto_check": True,
            "use_model": True,
            "repo": PROJECT_URL,
            "skipped_version": "",
            "last_check": "",
            "last_version": "",
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


def _clean_source_entry(entry: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(entry, dict):
        return None
    kind = str(entry.get("kind") or "").strip().lower()
    path = str(entry.get("path") or "").strip()
    enabled = entry.get("enabled", True) is not False
    if kind in {item[0] for item in BUILTIN_SOURCES}:
        return {"kind": kind, "enabled": enabled}
    if not path or len(path) > 520:
        return None
    if re.search(r"[\x00-\x1f\x7f]", path):
        return None
    return {"kind": "custom", "path": path, "enabled": enabled}


def normalize_search_dirs(values: Any) -> List[Dict[str, Any]]:
    """Validate and de-duplicate an ordered list of textbook search folders."""
    out: List[Dict[str, Any]] = []
    seen = set()
    if not isinstance(values, (list, tuple)):
        return out
    for raw in list(values)[:60]:
        entry = _clean_source_entry(raw)
        if not entry:
            continue
        key = entry["kind"] if entry["kind"] != "custom" else os.path.normcase(
            os.path.abspath(entry.get("path", "")))
        if key in seen:
            continue
        seen.add(key)
        out.append(entry)
    return out


def _migrate_config(cfg: Dict[str, Any], stored: Dict[str, Any]) -> Dict[str, Any]:
    """Apply non-destructive migrations from 4.3.x and earlier."""
    library = cfg.setdefault("library", {})
    stored_library = stored.get("library") if isinstance(stored.get("library"), dict) else {}

    if not stored_library.get("sources_seeded"):
        seeded = normalize_search_dirs(stored_library.get("search_dirs"))
        if not seeded:
            seeded = default_search_dirs()
        # v4.3.x offered no path UI; import any previously configured extras.
        legacy = stored_library.get("source_dirs") or stored_library.get("library_dirs")
        if isinstance(legacy, list):
            builtin_paths = {os.path.normcase(str(path)) for path in LIBRARY_SOURCE_DIRS}
            extras = []
            for item in legacy:
                text = str(item or "").strip()
                if not text or os.path.normcase(text) in builtin_paths:
                    continue
                extras.append({"kind": "custom", "path": text, "enabled": True})
            seeded = normalize_search_dirs(list(seeded) + extras) or seeded
        library["search_dirs"] = seeded
        library["sources_seeded"] = True

    ui = cfg.setdefault("ui", {})
    if ui.get("show_thinking") is None:
        ui["show_thinking"] = False
    if ui.get("show_citations") is None:
        ui["show_citations"] = False
    # 4.3.x stored the library zoom only; new layout values get sane defaults.
    try:
        ui["library_split"] = max(220, min(620, int(ui.get("library_split", 300))))
    except (TypeError, ValueError):
        ui["library_split"] = 300
    try:
        ui["library_text_height"] = max(90, min(520, int(ui.get("library_text_height", 220))))
    except (TypeError, ValueError):
        ui["library_text_height"] = 220

    update = cfg.setdefault("update", {})
    update.setdefault("auto_check", True)
    update.setdefault("use_model", True)
    update.setdefault("repo", PROJECT_URL)
    update.setdefault("skipped_version", "")
    cfg["settings_version"] = SETTINGS_VERSION
    return cfg


def load_config() -> Dict[str, Any]:
    ensure_dirs()
    cfg = default_config()
    if CONFIG_PATH.exists():
        try:
            stored = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(stored, dict):
                cfg = deep_merge(cfg, stored)
                cfg = _migrate_config(cfg, stored)
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
    if isinstance((update or {}).get("library"), dict):
        lib = update["library"]
        if "search_dirs" in lib:
            lib["search_dirs"] = normalize_search_dirs(lib.get("search_dirs"))
            lib["sources_seeded"] = True
    merged = deep_merge(cfg, update)
    merged = _migrate_config(merged, merged)
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
    cfg["paths"] = path_summary()
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


def _builtin_path(kind: str) -> Optional[Path]:
    for item_kind, _label, resolver in BUILTIN_SOURCES:
        if item_kind == kind:
            try:
                return resolver()
            except Exception:
                return None
    return None


def resolve_library_sources(cfg: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return every configured textbook folder in priority order.

    Built-in entries are resolved dynamically, so an installation that is moved
    to another directory automatically points at the new ``TextBook`` folder.
    """
    cfg = cfg or load_config()
    entries = cfg.get("library", {}).get("search_dirs")
    if not isinstance(entries, list):
        entries = default_search_dirs()
    out: List[Dict[str, Any]] = []
    seen = set()
    for raw in entries[:60]:
        entry = _clean_source_entry(raw)
        if not entry:
            continue
        if entry["kind"] == "custom":
            path = Path(entry["path"])
            label = path.name or str(path)
            builtin = False
        else:
            path = _builtin_path(entry["kind"])
            if path is None:
                continue
            label = next((item[1] for item in BUILTIN_SOURCES if item[0] == entry["kind"]),
                         entry["kind"])
            builtin = True
        try:
            resolved = path.resolve()
        except Exception:
            resolved = path
        key = os.path.normcase(str(resolved))
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "kind": entry["kind"],
            "path": str(resolved),
            "label": label,
            "enabled": bool(entry.get("enabled", True)),
            "builtin": builtin,
            "exists": resolved.is_dir(),
        })
    return out


def library_source_paths(cfg: Optional[Dict[str, Any]] = None) -> List[Path]:
    return [Path(item["path"]) for item in resolve_library_sources(cfg)
            if item["enabled"] and item["exists"]]


def save_library_sources(values: Any) -> List[Dict[str, Any]]:
    entries = normalize_search_dirs(values)
    cfg = save_config({"library": {"search_dirs": entries, "sources_seeded": True}})
    return resolve_library_sources(cfg)


def path_summary() -> Dict[str, Any]:
    sources = resolve_library_sources()
    current = next((item["path"] for item in sources if item["enabled"] and item["exists"]), "")
    return {
        "install_dir": str(INSTALL_DIR),
        "data_dir": str(PROJECT_ROOT),
        "data_root_file": str(DATA_ROOT_FILE),
        "textbook_default": str(INSTALL_DIR / "TextBook"),
        "current_library": current,
        "source_dirs": sources,
        "frozen": FROZEN,
        "portable": bool(_read_data_root_file() is not None),
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
    sources = resolve_library_sources(cfg)
    current = next((item["path"] for item in sources if item["enabled"] and item["exists"]), "")
    return {
        "name": APP_NAME,
        "name_zh": APP_NAME_ZH,
        "version": VERSION,
        "release_date": RELEASE_DATE,
        "settings_version": SETTINGS_VERSION,
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
        "data_dir": str(PROJECT_ROOT),
        "install_dir": str(INSTALL_DIR),
        "executable": str(Path(sys.executable).resolve()),
        "data_root_file": str(DATA_ROOT_FILE),
        "current_library": current,
        "library_sources": sources,
        "library_dirs": [str(p) for p in library_source_paths(cfg)],
        "frozen": FROZEN,
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
