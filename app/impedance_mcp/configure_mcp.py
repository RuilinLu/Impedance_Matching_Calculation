"""One-click MCP configuration helpers used by the installer and the app.

The helper only writes local client configuration files, always creates a
timestamped backup first, and never touches API keys.  It is intentionally
limited to clients with a stable JSON/TOML config location.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from . import config


def _launch_spec() -> Tuple[str, List[str]]:
    exe = Path(sys.executable).resolve()
    if getattr(sys, "frozen", False):
        return str(exe), ["--mcp"]
    return str(exe), [str(config.PROJECT_ROOT / "app" / "run_mcp.py")]


def _backup(path: Path) -> Path:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(f"{path.name}.bak_{stamp}")
    backup.write_bytes(path.read_bytes())
    return backup


def _write_json(path: Path, data: Dict[str, Any], key: str,
                command: str, args: List[str]) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        backup = _backup(path)
    else:
        backup = None
    root = data.setdefault(key, {})
    root["impedance-matching"] = {
        "command": command,
        "args": args,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "path": str(path), "backup": str(backup) if backup else ""}


def configure_zcode(command: str, args: List[str]) -> Dict[str, Any]:
    path = Path.home() / ".zcode" / "cli" / "config.json"
    if not path.exists():
        return {"ok": False, "path": str(path), "reason": "ZCode 配置不存在，已跳过"}
    data = json.loads(path.read_text(encoding="utf-8"))
    backup = _backup(path)
    servers = data.setdefault("mcp", {}).setdefault("servers", {})
    servers["impedance-matching"] = {
        "type": "stdio",
        "command": command,
        "args": args,
        "env": {"PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"},
        "timeoutMs": 120000,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "path": str(path), "backup": str(backup)}


def configure_claude(command: str, args: List[str]) -> Dict[str, Any]:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return {"ok": False, "reason": "APPDATA 不可用"}
    path = Path(appdata) / "Claude" / "claude_desktop_config.json"
    if not path.exists():
        return {"ok": False, "path": str(path), "reason": "未安装 Claude Desktop，已跳过"}
    return _write_json(path, {}, "mcpServers", command, args)


def configure_codex(command: str, args: List[str]) -> Dict[str, Any]:
    path = Path.home() / ".codex" / "config.toml"
    if not path.exists():
        return {"ok": False, "path": str(path), "reason": "未找到 Codex 配置，已跳过"}
    text = path.read_text(encoding="utf-8")
    if "[mcp_servers.impedance-matching]" in text:
        return {"ok": True, "path": str(path), "reason": "已存在，未修改"}
    backup = _backup(path)
    escaped = command.replace("\\", "\\\\").replace('"', '\\"')
    args_toml = ", ".join('"' + a.replace("\\", "\\\\").replace('"', '\\"') + '"' for a in args)
    block = (
        "\n[mcp_servers.impedance-matching]\n"
        f'command = "{escaped}"\n'
        f"args = [{args_toml}]\n"
        "startup_timeout_sec = 30\n"
        "tool_timeout_sec = 120\n"
    )
    path.write_text(text.rstrip() + "\n" + block, encoding="utf-8")
    return {"ok": True, "path": str(path), "backup": str(backup)}


def configure(targets: List[str]) -> Dict[str, Any]:
    command, args = _launch_spec()
    out: Dict[str, Any] = {"command": command, "args": args, "results": {}}
    if "zcode" in targets or "all" in targets:
        out["results"]["zcode"] = configure_zcode(command, args)
    if "claude" in targets or "all" in targets:
        out["results"]["claude"] = configure_claude(command, args)
    if "codex" in targets or "all" in targets:
        out["results"]["codex"] = configure_codex(command, args)
    return out


def main(argv: List[str]) -> int:
    args = [a.lower() for a in argv if not a.startswith("-")]
    targets = args or ["zcode"]
    result = configure(targets)
    for name, item in result["results"].items():
        status = "OK" if item.get("ok") else "SKIP"
        print(f"[{status}] {name}: {item.get('path') or item.get('reason')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
