# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: one onedir build with a GUI exe and a console MCP exe."""

from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent
APP = ROOT / "app"
WEB = APP / "impedance_mcp" / "web"
PROVIDERS = APP / "impedance_mcp" / "providers.json"
ICON = ROOT / "release" / "icon.ico"
VERSION_FILE = ROOT / "release" / "version_info.txt"
MCP_VERSION_FILE = ROOT / "release" / "version_info_mcp.txt"

a = Analysis(
    [str(APP / "launcher.py")],
    pathex=[str(APP)],
    binaries=[],
    datas=[
        (str(WEB), "impedance_mcp/web"),
        (str(PROVIDERS), "impedance_mcp"),
        (str(APP / "matlab" / "mw_design.m"), "matlab"),
        (str(APP / "matlab" / "mw_batch_entry.m"), "matlab"),
    ],
    hiddenimports=[
        "webview",
        "webview.platforms.edgechromium",
        "webview.platforms.winforms",
        "clr",
        "pythonnet",
        "pypdf",
        "openpyxl",
        "PIL",
        "PIL.Image",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe_gui = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ImpedanceMCP",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=str(ICON) if ICON.exists() else None,
    version=str(VERSION_FILE) if VERSION_FILE.exists() else None,
)

exe_mcp = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ImpedanceMCP_MCP",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    icon=str(ICON) if ICON.exists() else None,
    version=str(MCP_VERSION_FILE) if MCP_VERSION_FILE.exists() else None,
)

coll = COLLECT(
    exe_gui,
    exe_mcp,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ImpedanceMCP",
)
