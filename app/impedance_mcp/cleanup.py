"""Deep uninstall cleanup: remove program data, MCP entries and app registry keys.

This runs from the generated uninstaller *before* Inno removes the installation
directory.  It intentionally does not touch shared system components such as the
Microsoft Edge WebView2 Runtime, and it only removes MCP entries whose command
points at this application.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    import winreg  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - non-Windows source runs
    winreg = None  # type: ignore[assignment]

APP_DIR_NAME = "ImpedanceMatchingAI"
OLD_APP_DIR_NAMES = ("ImpedanceMCP", "ImpedanceMCP_App")
MCP_SERVER_NAMES = ("impedance-matching-ai", "impedance-matching")
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\{A4C1E2D3-5B6F-4A7E-9C8D-1E2F3A4B5C6D}_is1"


def _say(message: str, dry_run: bool) -> None:
    prefix = "[dry-run] " if dry_run else ""
    try:
        sys.stdout.write(prefix + message + "\n")
        sys.stdout.flush()
    except Exception:
        pass


def _remove_tree(path: Path, dry_run: bool) -> bool:
    import time

    try:
        if not path.exists():
            return False
        _say(f"remove {path}", dry_run)
        if dry_run:
            return True
        last_error = None
        for attempt in range(4):
            try:
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=False)
                else:
                    path.unlink()
                return True
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                time.sleep(0.6 + attempt * 0.4)
        _say(f"skip {path}: {last_error}", dry_run)
        return False
    except Exception as exc:  # noqa: BLE001
        _say(f"skip {path}: {exc}", dry_run)
        return False


def _profiles() -> Iterable[Path]:
    seen = set()

    def add(path: Optional[str]) -> Iterable[Path]:
        if not path:
            return
        try:
            target = Path(path)
        except Exception:
            return
        key = str(target).lower()
        if key not in seen and target.exists():
            seen.add(key)
            yield target

    home = Path.home()
    yield from add(str(home))
    if winreg is not None:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList") as key:
                index = 0
                while True:
                    try:
                        sub = winreg.EnumKey(key, index)
                    except OSError:
                        break
                    index += 1
                    try:
                        with winreg.OpenKey(key, sub) as item:
                            value, _ = winreg.QueryValueEx(item, "ProfileImagePath")
                        yield from add(os.path.expandvars(str(value)))
                    except OSError:
                        continue
        except OSError:
            pass
    users = Path(os.environ.get("SystemDrive", "C:") + r"\Users")
    try:
        for child in users.iterdir():
            if child.is_dir():
                yield from add(str(child))
    except OSError:
        pass


def _is_ours(entry: Any, app_dir: Optional[Path]) -> bool:
    try:
        blob = json.dumps(entry, ensure_ascii=False).lower()
    except Exception:
        blob = str(entry).lower()
    markers = ("impedancemcp", "impedance_matching", "impedance-matching", "run_mcp.py")
    if any(marker in blob for marker in markers):
        return True
    if app_dir is not None and str(app_dir).lower() in blob:
        return True
    return False


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".imp_tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def _remove_json_entry(path: Path, parents: List[str], app_dir: Optional[Path],
                       dry_run: bool) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    container: Any = data
    for key in parents:
        if not isinstance(container, dict):
            return False
        container = container.get(key)
        if container is None:
            return False
    if not isinstance(container, dict):
        return False
    removed = False
    for name in MCP_SERVER_NAMES:
        if name not in container:
            continue
        entry = container[name]
        if not _is_ours(entry, app_dir):
            continue
        _say(f"remove MCP entry {'.'.join(parents)}.{name} from {path}", dry_run)
        removed = True
        if not dry_run:
            del container[name]
    if removed and not dry_run:
        _atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return removed


def _remove_toml_section(path: Path, section: str, app_dir: Optional[Path],
                         dry_run: bool) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    lines = text.splitlines()
    header = f"[{section}]"
    start = None
    for i, line in enumerate(lines):
        if line.strip() == header:
            start = i
            break
    if start is None:
        return False
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].lstrip().startswith("["):
            end = j
            break
    block = "\n".join(lines[start:end])
    if not _is_ours(block, app_dir):
        return False
    _say(f"remove MCP section [{section}] from {path}", dry_run)
    if not dry_run:
        remaining = lines[:start] + lines[end:]
        while remaining and not remaining[-1].strip():
            remaining.pop()
        _atomic_write(path, "\n".join(remaining).rstrip() + "\n")
    return True


def _clean_mcp_configs(profile: Path, app_dir: Optional[Path], dry_run: bool) -> None:
    json_targets = [
        (profile / ".zcode" / "cli" / "config.json", ["mcp", "servers"]),
        (profile / ".claude" / "claude_desktop_config.json", ["mcpServers"]),
        (profile / ".claude.json", ["mcpServers"]),
        (profile / ".cursor" / "mcp.json", ["mcpServers"]),
        (profile / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
         ["mcpServers"]),
    ]
    for path, parents in json_targets:
        try:
            if path.is_file():
                _remove_json_entry(path, parents, app_dir, dry_run)
        except Exception as exc:  # noqa: BLE001
            _say(f"skip MCP config {path}: {exc}", dry_run)
    codex = profile / ".codex" / "config.toml"
    try:
        if codex.is_file():
            for name in MCP_SERVER_NAMES:
                _remove_toml_section(codex, f"mcp_servers.{name}", app_dir, dry_run)
    except Exception as exc:  # noqa: BLE001
        _say(f"skip Codex config {codex}: {exc}", dry_run)


def _delete_reg_tree(root: int, path: str, dry_run: bool) -> None:
    if winreg is None:
        return
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            children = []
            index = 0
            while True:
                try:
                    children.append(winreg.EnumKey(key, index))
                except OSError:
                    break
                index += 1
        for child in children:
            _delete_reg_tree(root, path + "\\" + child, dry_run)
        _say(f"remove registry HKEY {root}\\{path}", dry_run)
        if not dry_run:
            winreg.DeleteKey(root, path)
    except FileNotFoundError:
        return
    except OSError as exc:
        _say(f"skip registry {path}: {exc}", dry_run)


def _clean_registry(dry_run: bool) -> None:
    if winreg is None:
        return
    targets = [
        (winreg.HKEY_CURRENT_USER, r"Software\ImpedanceMCP"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\ImpedanceMCP"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\ImpedanceMCP"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\App Paths\ImpedanceMCP.exe"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\App Paths\ImpedanceMCP.exe"),
        (winreg.HKEY_CURRENT_USER, r"Software\Classes\Applications\ImpedanceMCP.exe"),
    ]
    for root, path in targets:
        _delete_reg_tree(root, path, dry_run)
    for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(root, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                winreg.KEY_READ | winreg.KEY_WRITE) as key:
                try:
                    winreg.QueryValueEx(key, "ImpedanceMCP")
                except FileNotFoundError:
                    continue
            _say(f"remove Run value HKEY {root}\\...\\Run\\ImpedanceMCP", dry_run)
            if not dry_run:
                with winreg.OpenKey(root, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                    winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, "ImpedanceMCP")
        except OSError:
            pass


def _clean_shortcuts(profiles: List[Path], app_dir: Optional[Path], dry_run: bool) -> None:
    names = [
        "ImpedanceMatchingAI.lnk", "一键卸载 ImpedanceMatchingAI.lnk",
        "ImpedanceMCP.lnk", "一键卸载 ImpedanceMCP.lnk",
    ]
    common = [
        Path(os.environ.get("ProgramData", r"C:\ProgramData"))
        / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Impedance Matching AI",
        Path(os.environ.get("ProgramData", r"C:\ProgramData"))
        / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "智配芯生 ImpedanceMCP",
        Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "Desktop" / "ImpedanceMatchingAI.lnk",
        Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "Desktop" / "一键卸载 ImpedanceMatchingAI.lnk",
        Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "Desktop" / "ImpedanceMCP.lnk",
        Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "Desktop" / "一键卸载 ImpedanceMCP.lnk",
    ]
    for path in common:
        _remove_tree(path, dry_run)
    for profile in profiles:
        for base in (
            profile / "Desktop",
            profile / "OneDrive" / "Desktop",
            profile / "OneDrive" / "桌面",
            profile / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            / "Impedance Matching AI",
            profile / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            / "智配芯生 ImpedanceMCP",
        ):
            if base.suffix.lower() == ".lnk":
                if base.is_file():
                    _remove_tree(base, dry_run)
                continue
            for name in names:
                _remove_tree(base / name, dry_run)
            if base.is_dir() and "Start Menu" in str(base):
                _remove_tree(base, dry_run)


def _preserve_textbook(app_dir: Optional[Path], dry_run: bool) -> str:
    """Copy the install-directory TextBook into the persistent data root."""
    if app_dir is None:
        return ""
    source = app_dir / "TextBook"
    if not source.is_dir():
        return ""
    try:
        from . import config
        target = config.PROJECT_ROOT / "TextBook"
    except Exception:
        target = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / APP_DIR_NAME / "TextBook"
    try:
        if source.resolve() == target.resolve():
            return ""
    except OSError:
        pass
    _say(f"preserve {source} -> {target}", dry_run)
    if dry_run:
        return str(target)
    try:
        target.mkdir(parents=True, exist_ok=True)
        count = 0
        for item in source.rglob("*"):
            if not item.is_file() or item.name.startswith("."):
                continue
            relative = item.relative_to(source)
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, destination)
            count += 1
        _say(f"preserved {count} textbook file(s)", dry_run)
        return str(target)
    except Exception as exc:  # noqa: BLE001
        _say(f"skip textbook preservation: {exc}", dry_run)
        return ""


def _remove_data_root(dry_run: bool) -> List[str]:
    """Delete application data without wiping an unrelated custom directory."""
    removed: List[str] = []
    try:
        from . import config
        data_root = config.PROJECT_ROOT
    except Exception:
        data_root = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / APP_DIR_NAME
    # Refuse to touch a custom root that does not look like our own data tree.
    looks_ours = ((data_root / "data" / "config.json").is_file()
                  or (data_root / "data" / "library").is_dir())
    if not looks_ours:
        _say(f"skip data root {data_root}: not an application data directory", dry_run)
        return removed
    for sub in ("data", "webview", "TextBook"):
        target = data_root / sub
        if _remove_tree(target, dry_run):
            removed.append(str(target))
    if data_root.name.lower() == APP_DIR_NAME.lower() and _remove_tree(data_root, dry_run):
        removed.append(str(data_root))
    return removed


def cleanup(app_dir: Optional[Path] = None, dry_run: bool = False,
            keep_mcp_config: bool = False, keep_user_data: bool = False,
            preserve_textbook: bool = False,
            delete_user_data: bool = False) -> Dict[str, Any]:
    """Remove program integration; personal data is kept unless explicitly deleted.

    ``delete_user_data`` must be supplied by the caller.  This fail-safe default
    prevents an uninstaller/check-function mistake from wiping user settings.
    """
    profiles = list(_profiles())
    removed: List[str] = []
    preserved = ""
    if preserve_textbook and not delete_user_data:
        preserved = _preserve_textbook(app_dir, dry_run)
    if delete_user_data:
        for profile in profiles:
            for dir_name in (APP_DIR_NAME, *OLD_APP_DIR_NAMES):
                for base in (profile / "AppData" / "Local" / dir_name,
                             profile / "AppData" / "Roaming" / dir_name):
                    if _remove_tree(base, dry_run):
                        removed.append(str(base))
        removed.extend(_remove_data_root(dry_run))
        if app_dir is not None:
            textbook = app_dir / "TextBook"
            if _remove_tree(textbook, dry_run):
                removed.append(str(textbook))
    for profile in profiles:
        if not keep_mcp_config:
            _clean_mcp_configs(profile, app_dir, dry_run)
    _clean_registry(dry_run)
    _clean_shortcuts(profiles, app_dir, dry_run)
    temp = Path(os.environ.get("TEMP", str(Path.home() / "AppData" / "Local" / "Temp")))
    for pattern in ("ImpedanceMatchingAI*", "ImpedanceMCP*"):
        for item in temp.glob(pattern):
            _remove_tree(item, dry_run)
    for item in temp.glob("imp_install*.log"):
        _remove_tree(item, dry_run)
    return {"ok": True, "profiles": len(profiles), "removed": removed,
            "dry_run": dry_run, "keep_user_data": not delete_user_data,
            "deleted_user_data": delete_user_data,
            "preserved_textbook": preserved}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="ImpedanceMCP deep uninstall cleanup")
    parser.add_argument("--app-dir", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-mcp-config", action="store_true")
    parser.add_argument("--keep-user-data", action="store_true")
    parser.add_argument("--preserve-textbook", action="store_true")
    parser.add_argument("--delete-user-data", action="store_true")
    args = parser.parse_args(argv)
    app_dir = Path(args.app_dir).resolve() if args.app_dir else None
    result = cleanup(app_dir=app_dir, dry_run=args.dry_run,
                     keep_mcp_config=args.keep_mcp_config,
                     keep_user_data=args.keep_user_data,
                     preserve_textbook=args.preserve_textbook,
                     delete_user_data=args.delete_user_data)
    _say(json.dumps(result, ensure_ascii=False), args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
