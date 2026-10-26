"""Configuration, path discovery and runtime status."""

from __future__ import annotations

import copy
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PACKAGE_DIR = Path(__file__).resolve().parent
FROZEN = bool(getattr(sys, "frozen", False))
if FROZEN:
    # PyInstaller one-file: __file__ lives in the temporary _MEIPASS directory.
    # Keep user data next to the executable's user profile, not in the temp dir.
    APP_DIR = PACKAGE_DIR.parent
    EXE_DIR = Path(sys.executable).resolve().parent
    PROJECT_ROOT = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "ImpedanceMCP"
    DATA_DIR = PROJECT_ROOT / "data"
    WEB_DIR = PACKAGE_DIR / "web"
    MATLAB_DIR = APP_DIR / "matlab"
else:
    APP_DIR = PACKAGE_DIR.parent
    EXE_DIR = APP_DIR.parent
    PROJECT_ROOT = APP_DIR.parent
    DATA_DIR = PROJECT_ROOT / "data"
    WEB_DIR = PACKAGE_DIR / "web"
    MATLAB_DIR = APP_DIR / "matlab"
UPLOAD_DIR = DATA_DIR / "uploads"
REPORT_DIR = DATA_DIR / "reports"
CONFIG_PATH = DATA_DIR / "config.json"
if FROZEN:
    HELP_DIR = EXE_DIR / "docs" if (EXE_DIR / "docs").exists() else (APP_DIR / "docs")
else:
    HELP_DIR = PROJECT_ROOT / "docs"


VERSION = "4.3.0"
RELEASE_DATE = "2026-10-26"
TEAM = [
    {"name": "卢瑞林", "role": "项目负责人 / 算法与 MCP 架构", "initials": "LRL"},
    {"name": "卢柯吉", "role": "MATLAB 计算内核与仿真验证", "initials": "LKJ"},
    {"name": "林芷伊", "role": "交互设计、可视化与文档", "initials": "LZY"},
    {"name": "张昀蕾", "role": "测试、演示与用户研究", "initials": "ZYL"},
]
AUTHOR_EMAILS = ["radarlurui@gmail.com", "Lu_Skywalker2915@sjtu.edu.cn"]
PROJECT_URL = "https://github.com/RuilinLu/Impedance_Matching_Calculation"


def ensure_dirs() -> None:
    for p in (DATA_DIR, UPLOAD_DIR, REPORT_DIR):
        p.mkdir(parents=True, exist_ok=True)


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def default_config() -> Dict[str, Any]:
    return {
        "llm": {
            "provider": "",
            "provider_name": "",
            "base_url": "",
            "api_key": "",
            "model": "",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "api_style": "openai",
            "chat_path": "",
            "extra_headers": {},
            "temperature": 0.25,
            "max_tokens": 2600,
        },
        "engine": "python",
        "matlab": {
            "matlab_path": "",
            "classic_app_path": "",
        },
        "ui": {
            "last_topology": "l_right",
            "animation_speed": 45,
        },
    }


def deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    for k, v in (update or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
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
    # Optional generic environment overrides.  No vendor is selected by
    # default: the user chooses a provider in the Settings dialog.
    env_key = _env("LLM_API_KEY")
    env_base = _env("LLM_BASE_URL")
    env_model = _env("LLM_MODEL")
    if env_key and not cfg["llm"].get("api_key"):
        cfg["llm"]["api_key"] = env_key
    if env_base:
        cfg["llm"]["base_url"] = env_base
        if not cfg["llm"].get("provider"):
            cfg["llm"]["provider"] = "custom"
            cfg["llm"]["provider_name"] = "环境变量"
    if env_model:
        cfg["llm"]["model"] = env_model
    return cfg


def save_config(update: Dict[str, Any]) -> Dict[str, Any]:
    cfg = load_config()
    llm = (update or {}).get("llm", {})
    if isinstance(llm, dict):
        if llm.get("clear_key"):
            if not llm.get("api_key"):
                llm["api_key"] = ""
            llm.pop("clear_key", None)
        key = llm.get("api_key")
        if key in (None, "", "******", "***"):
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


# ---------------------------------------------------------------------------
# MATLAB / MCR discovery
# ---------------------------------------------------------------------------

def _version_key(path: str) -> tuple:
    m = re.search(r"R(\d{4})([ab])", path, re.I)
    if not m:
        return (0, 0)
    return (int(m.group(1)), 1 if m.group(2).lower() == "b" else 0)


def find_matlab() -> Optional[str]:
    cfg_path = load_config().get("matlab", {}).get("matlab_path")
    if cfg_path and Path(cfg_path).exists():
        return str(cfg_path)
    cands: List[str] = []
    for pattern in (
        r"C:\Program Files\MATLAB\R*\bin\matlab.exe",
        r"D:\Program Files\MATLAB\R*\bin\matlab.exe",
        r"E:\Program Files\MATLAB\R*\bin\matlab.exe",
        r"C:\MATLAB\R*\bin\matlab.exe",
        r"D:\MATLAB\R*\bin\matlab.exe",
        r"E:\MATLAB\R*\bin\matlab.exe",
    ):
        cands.extend(glob.glob(pattern))
    which = shutil.which("matlab")
    if which:
        cands.append(which)
    cands = [c for c in cands if Path(c).exists()]
    if not cands:
        return None
    cands.sort(key=_version_key, reverse=True)
    return cands[0]


def find_classic_app() -> Optional[str]:
    cfg_path = load_config().get("matlab", {}).get("classic_app_path")
    if cfg_path and Path(cfg_path).exists():
        return str(cfg_path)
    roots = [
        EXE_DIR / "APP_Release_Release_Version",
        EXE_DIR,
        EXE_DIR.parent / "APP_Release_Release_Version",
        EXE_DIR.parent,
        EXE_DIR.parent.parent / "APP_Release_Release_Version",
        EXE_DIR.parent.parent,
        PROJECT_ROOT / "APP_Release_Release_Version",
        PROJECT_ROOT,
        APP_DIR,
    ]
    seen = set()
    for root in roots:
        key = str(root.resolve()) if root.exists() else str(root)
        if key in seen:
            continue
        seen.add(key)
        if not root.exists():
            continue
        for pattern in (
            "**/for_redistribution_files_only/Impedance_Matching.exe",
            "**/for_testing/Impedance_Matching.exe",
            "**/Impedance_Matching.exe",
        ):
            hits = sorted(glob.glob(str(root / pattern), recursive=True),
                          key=lambda p: ("for_redistribution_files_only" not in p, len(p)))
            if hits:
                return hits[0]
    return None


def find_mcr() -> Optional[str]:
    patterns = [
        r"C:\Program Files\MATLAB\MATLAB Runtime\R2023b",
        r"D:\Program Files\MATLAB\MATLAB Runtime\R2023b",
        r"E:\Program Files\MATLAB\MATLAB Runtime\R2023b",
        r"C:\Program Files\MATLAB\MATLAB Runtime\R*",
    ]
    for p in patterns:
        hits = sorted(glob.glob(p), reverse=True)
        if hits:
            return hits[0]
    return None


def matlab_status() -> Dict[str, Any]:
    matlab = find_matlab()
    exe = find_classic_app()
    mcr = find_mcr()
    return {
        "matlab_path": matlab,
        "matlab_version": Path(matlab).parts[-3] if matlab else None,
        "classic_app_path": exe,
        "classic_app_available": bool(exe),
        "mcr_path": mcr,
        "mcr_installed": bool(mcr),
        "engine_mode": load_config().get("engine", "python"),
        "notes": {
            "mcr": "MyAppInstaller_mcr.exe 已内置 MATLAB Runtime R2023b，可直接安装。",
            "matlab": "若安装 MATLAB R2025b，可启用 MATLAB 批处理内核进行交叉复核。",
        },
    }


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
        "api_style": llm.get("api_style", "openai"),
    }


def mcp_launch() -> tuple:
    """Return the console executable that speaks MCP over stdio.

    The GUI executable is built as a Windows-subsystem binary, so MCP clients
    must launch the sibling console binary.  Source mode uses run_mcp.py.
    """
    if FROZEN:
        exe = Path(sys.executable).resolve()
        for name in ("ImpedanceMCP_MCP.exe", "ImpedanceMCP.exe"):
            candidate = exe.with_name(name)
            if candidate.exists():
                return str(candidate), ["--mcp"]
        return str(exe), ["--mcp"]
    return sys.executable, [str(PROJECT_ROOT / "app" / "run_mcp.py")]


def _mcp_launch() -> tuple:
    return mcp_launch()


def status() -> Dict[str, Any]:
    cfg = load_config()
    command, args = mcp_launch()
    return {
        "name": "智配芯生 · ImpedanceMCP",
        "version": VERSION,
        "release_date": RELEASE_DATE,
        "llm": llm_status(cfg),
        "matlab": matlab_status(),
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
    }


def mcp_client_config() -> Dict[str, Any]:
    command, args = _mcp_launch()
    return {
        "impedance-matching": {
            "type": "stdio",
            "command": command,
            "args": args,
            "env": {
                "PYTHONUNBUFFERED": "1",
                "PYTHONIOENCODING": "utf-8",
            },
            "timeoutMs": 120000,
        }
    }
