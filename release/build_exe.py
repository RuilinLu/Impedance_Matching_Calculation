"""Build the standalone Windows executable(s) and the installer payload.

Usage (from the project root):
    python release/build_exe.py

Produces:
    dist/ImpedanceMCP_Portable.exe          one-file portable
    release/ImpedanceMCP_v4.2.0_Portable.exe
    dist/ImpedanceMCP/                      one-folder app (installer payload)
    release/ImpedanceMCP_v4.2.0_App/
    release/ImpedanceMCP_v4.2.0_Windows.exe (portable copy, kept for convenience)

The one-folder build is what the Inno Setup installer packages: it avoids the
self-extracting one-file behaviour that some antivirus engines treat as
suspicious, and starts faster.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "4.2.0"
ICON = ROOT / "release" / "icon.ico"
VERSION_FILE = ROOT / "release" / "version_info.txt"


def _safe(path: Path) -> str:
    resolved = path.resolve()
    if ROOT.resolve() not in resolved.parents and resolved != ROOT.resolve():
        raise ValueError(f"path outside project: {resolved}")
    return str(resolved)


def _common(name: str) -> list:
    cmd = [
        "--noconfirm", "--clean", "--console",
        "--name", name,
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
    if VERSION_FILE.exists():
        cmd += ["--version-file", _safe(VERSION_FILE)]
    return cmd


def build(name: str, onefile: bool) -> None:
    from PyInstaller.__main__ import run as pyinstaller_run
    cmd = _common(name)
    cmd.insert(3, "--onefile" if onefile else "--onedir")
    print("PyInstaller " + " ".join(cmd))
    try:
        pyinstaller_run(cmd)
    except SystemExit as exc:
        if exc.code not in (0, None):
            raise


def main() -> int:
    try:
        import PyInstaller  # noqa: F401
    except ImportError as exc:
        raise SystemExit("PyInstaller is not installed: pip install pyinstaller") from exc

    build("ImpedanceMCP_Portable", onefile=True)
    portable = ROOT / "dist" / "ImpedanceMCP_Portable.exe"
    dst_portable = ROOT / "release" / f"ImpedanceMCP_v{VERSION}_Portable.exe"
    if not portable.exists():
        raise SystemExit("one-file build missing")
    shutil.copy2(portable, dst_portable)
    shutil.copy2(portable, ROOT / "release" / f"ImpedanceMCP_v{VERSION}_Windows.exe")

    build("ImpedanceMCP", onefile=False)
    app_dir = ROOT / "dist" / "ImpedanceMCP"
    dst_app = ROOT / "release" / f"ImpedanceMCP_v{VERSION}_App"
    if not (app_dir / "ImpedanceMCP.exe").exists():
        raise SystemExit("one-folder build missing")
    if dst_app.exists():
        shutil.rmtree(dst_app)
    shutil.copytree(app_dir, dst_app)

    print(f"\nPortable: {dst_portable} ({dst_portable.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"App dir : {dst_app}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
