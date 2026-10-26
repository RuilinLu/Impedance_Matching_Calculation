"""Build the native Windows GUI, the console MCP executable and installer payload.

Usage (from the project root):
    python release/build_exe.py

Produces:
    dist/ImpedanceMCP_Portable.exe          one-file native GUI (no browser)
    release/ImpedanceMCP_v4.3.0_Portable.exe
    dist/ImpedanceMCP_MCP_Portable.exe      one-file MCP stdio console
    release/ImpedanceMCP_v4.3.0_Portable_MCP.exe
    dist/ImpedanceMCP/                      one-folder app (installer payload)
    release/ImpedanceMCP_v4.3.0_App/
        ImpedanceMCP.exe                    native window (Windows subsystem)
        ImpedanceMCP_MCP.exe                MCP stdio/HTTP (console subsystem)

The one-folder build is what Inno Setup packages.  Two executables share one
_internal directory: the GUI is windowed so double-clicking never opens a
console or a browser, while the console binary keeps stdout/stdin available for
MCP clients.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "4.3.0"
ICON = ROOT / "release" / "icon.ico"
VERSION_FILE = ROOT / "release" / "version_info.txt"
SPEC = ROOT / "release" / "ImpedanceMCP.spec"


def _safe(path: Path) -> str:
    resolved = path.resolve()
    if ROOT.resolve() not in resolved.parents and resolved != ROOT.resolve():
        raise ValueError(f"path outside project: {resolved}")
    return str(resolved)


def _pyi(args: list) -> None:
    from PyInstaller.__main__ import run as pyinstaller_run
    print("PyInstaller " + " ".join(args))
    try:
        pyinstaller_run(args)
    except SystemExit as exc:
        if exc.code not in (0, None):
            raise


def _common(name: str, windowed: bool, entry: Path) -> list:
    cmd = [
        "--noconfirm", "--clean", "--onefile",
        "--windowed" if windowed else "--console",
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
        "--hidden-import", "webview",
        "--hidden-import", "webview.platforms.edgechromium",
        "--hidden-import", "webview.platforms.winforms",
        "--hidden-import", "clr",
        "--hidden-import", "pythonnet",
        "--exclude-module", "tkinter",
        _safe(entry),
    ]
    if ICON.exists():
        cmd += ["--icon", _safe(ICON)]
    if VERSION_FILE.exists():
        cmd += ["--version-file", _safe(VERSION_FILE)]
    return cmd


def build_portable_gui() -> Path:
    _pyi(_common("ImpedanceMCP_Portable", True, ROOT / "app" / "launcher.py"))
    portable = ROOT / "dist" / "ImpedanceMCP_Portable.exe"
    if not portable.exists():
        raise SystemExit("one-file GUI build missing")
    dst = ROOT / "release" / f"ImpedanceMCP_v{VERSION}_Portable.exe"
    shutil.copy2(portable, dst)
    shutil.copy2(portable, ROOT / "release" / f"ImpedanceMCP_v{VERSION}_Windows.exe")
    return dst


def build_portable_mcp() -> Path:
    _pyi(_common("ImpedanceMCP_MCP_Portable", False, ROOT / "app" / "run_mcp.py"))
    portable = ROOT / "dist" / "ImpedanceMCP_MCP_Portable.exe"
    if not portable.exists():
        raise SystemExit("one-file MCP build missing")
    dst = ROOT / "release" / f"ImpedanceMCP_v{VERSION}_Portable_MCP.exe"
    shutil.copy2(portable, dst)
    return dst


def build_onedir() -> Path:
    if not SPEC.exists():
        raise SystemExit(f"spec missing: {SPEC}")
    _pyi([str(SPEC), "--noconfirm", "--clean"])
    app_dir = ROOT / "dist" / "ImpedanceMCP"
    if not (app_dir / "ImpedanceMCP.exe").exists():
        raise SystemExit("one-folder GUI build missing")
    if not (app_dir / "ImpedanceMCP_MCP.exe").exists():
        raise SystemExit("one-folder MCP build missing")
    dst_app = ROOT / "release" / f"ImpedanceMCP_v{VERSION}_App"
    if dst_app.exists():
        shutil.rmtree(dst_app)
    shutil.copytree(app_dir, dst_app)
    return dst_app


def main() -> int:
    try:
        import PyInstaller  # noqa: F401
    except ImportError as exc:
        raise SystemExit("PyInstaller is not installed: pip install pyinstaller") from exc
    try:
        import webview  # noqa: F401
    except ImportError as exc:
        raise SystemExit("pywebview is not installed: pip install pywebview") from exc

    portable = build_portable_gui()
    portable_mcp = build_portable_mcp()
    app_dir = build_onedir()

    print(f"\nPortable GUI: {portable} ({portable.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"Portable MCP: {portable_mcp} ({portable_mcp.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"App dir     : {app_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
