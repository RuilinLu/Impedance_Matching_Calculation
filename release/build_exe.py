"""Build the standalone Windows executable (standalone app + MCP in one file).

Usage (from the project root):
    python release/build_exe.py

Produces:
    dist/ImpedanceMCP.exe
    release/ImpedanceMCP_v4.1.0_Windows.exe

The exe supports:
    ImpedanceMCP.exe                   -> standalone web app
    ImpedanceMCP.exe --mcp             -> MCP stdio server
    ImpedanceMCP.exe --mcp --http 8790 -> MCP HTTP/SSE server
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "4.1.0"
ICON = ROOT / "release" / "icon.ico"


def _safe(path: Path) -> str:
    resolved = path.resolve()
    if ROOT.resolve() not in resolved.parents and resolved != ROOT.resolve():
        raise ValueError(f"path outside project: {resolved}")
    return str(resolved)


def main() -> int:
    try:
        from PyInstaller.__main__ import run as pyinstaller_run
    except ImportError as exc:
        raise SystemExit("PyInstaller is not installed: pip install pyinstaller") from exc

    cmd = [
        "--noconfirm", "--clean", "--onefile", "--console",
        "--name", "ImpedanceMCP",
        "--paths", _safe(ROOT / "app"),
        "--add-data", f"{_safe(ROOT / 'app' / 'impedance_mcp' / 'web')};impedance_mcp/web",
        "--add-data", f"{_safe(ROOT / 'app' / 'impedance_mcp' / 'providers.json')};impedance_mcp",
        "--add-data", f"{_safe(ROOT / 'app' / 'matlab' / 'mw_design.m')};matlab",
        "--add-data", f"{_safe(ROOT / 'app' / 'matlab' / 'mw_batch_entry.m')};matlab",
        "--hidden-import", "pypdf",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "openpyxl",
        "--exclude-module", "tkinter",
        _safe(ROOT / "app" / "launcher.py"),
    ]
    if ICON.exists():
        cmd += ["--icon", _safe(ICON)]
    print("PyInstaller " + " ".join(cmd))
    try:
        pyinstaller_run(cmd)
    except SystemExit as exc:
        if exc.code not in (0, None):
            raise
    src = ROOT / "dist" / "ImpedanceMCP.exe"
    dst = ROOT / "release" / f"ImpedanceMCP_v{VERSION}_Windows.exe"
    if not src.exists():
        raise SystemExit("build finished but dist/ImpedanceMCP.exe is missing")
    shutil.copy2(src, dst)
    print(f"\nBuilt: {src} ({src.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"Copy : {dst} ({dst.stat().st_size / 1024 / 1024:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
