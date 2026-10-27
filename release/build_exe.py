"""Build the Windows portable executables and the clean source archive.

Usage (from the project root):
    python release/build_exe.py              # source zip + GUI + MCP exe
    python release/build_exe.py --source-only

Outputs:
    release/Impedance_Matching_AI_v4.3.0_Source.zip
    release/Impedance_Matching_AI_v4.3.0_Portable.exe
    release/Impedance_Matching_AI_v4.3.0_MCP.exe
    release/SHA256SUMS.txt
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release"
DIST = ROOT / "dist"
VERSION = "4.3.0"
APP_NAME = "ImpedanceMatchingAI"
ICON = RELEASE / "icon.ico"
VERSION_FILE = RELEASE / "version_info.txt"

SOURCE_SKIP_DIRS = {".git", "TextBook", "data", "dist", "build", "__pycache__",
                    ".mimosa", ".pytest_cache", ".venv", "venv"}
SOURCE_SKIP_SUFFIXES = {".pyc", ".pyo", ".exe", ".zip", ".7z", ".log"}
SOURCE_SKIP_NAMES = {"SHA256SUMS.txt"}


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
        "--add-data", f"{_safe(ROOT / 'app' / 'impedance_mcp' / 'docs_content')};impedance_mcp/docs_content",
        "--add-data", f"{_safe(ROOT / 'app' / 'impedance_mcp' / 'providers.json')};impedance_mcp",
        "--add-data", f"{_safe(ROOT / 'app' / 'impedance_mcp')};app_src/impedance_mcp",
        "--hidden-import", "pymupdf",
        "--hidden-import", "fitz",
        "--hidden-import", "rapidocr_onnxruntime",
        "--hidden-import", "onnxruntime",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "docx",
        "--hidden-import", "pptx",
        "--hidden-import", "openpyxl",
        "--hidden-import", "webview",
        "--hidden-import", "webview.platforms.edgechromium",
        "--hidden-import", "webview.platforms.winforms",
        "--hidden-import", "clr",
        "--hidden-import", "pythonnet",
        "--collect-data", "rapidocr_onnxruntime",
        "--collect-all", "rapidocr_onnxruntime",
        "--collect-all", "pymupdf",
        "--collect-all", "fitz",
        "--exclude-module", "tkinter",
        "--exclude-module", "pytest",
        _safe(entry),
    ]
    if ICON.exists():
        cmd += ["--icon", _safe(ICON)]
    version_file = RELEASE / ("version_info_mcp.txt" if "MCP" in name else "version_info.txt")
    if version_file.exists():
        cmd += ["--version-file", _safe(version_file)]
    return cmd


def build_source_zip() -> Path:
    target = RELEASE / f"Impedance_Matching_AI_v{VERSION}_Source.zip"
    arcbase = f"Impedance_Matching_AI_{VERSION.replace('.', '_')}"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            parts = set(rel.parts)
            if parts & SOURCE_SKIP_DIRS:
                continue
            if path.suffix.lower() in SOURCE_SKIP_SUFFIXES:
                continue
            if path.name in SOURCE_SKIP_NAMES:
                continue
            if path.name.startswith("~$") or path.name.startswith(".DS_Store"):
                continue
            archive.write(path, f"{arcbase}/{rel.as_posix()}")
    return target


def build_portable() -> Path:
    DIST.mkdir(exist_ok=True)
    _pyi(_common(APP_NAME, True, ROOT / "app" / "launcher.py"))
    source = DIST / f"{APP_NAME}.exe"
    if not source.exists():
        raise SystemExit("GUI build missing")
    target = RELEASE / f"Impedance_Matching_AI_v{VERSION}_Portable.exe"
    shutil.copy2(source, target)
    return target


def build_mcp() -> Path:
    DIST.mkdir(exist_ok=True)
    _pyi(_common(f"{APP_NAME}_MCP", False, ROOT / "app" / "run_mcp.py"))
    source = DIST / f"{APP_NAME}_MCP.exe"
    if not source.exists():
        raise SystemExit("MCP build missing")
    target = RELEASE / f"Impedance_Matching_AI_v{VERSION}_MCP.exe"
    shutil.copy2(source, target)
    return target


def write_checksums() -> Path:
    target = RELEASE / "SHA256SUMS.txt"
    lines = []
    for path in sorted(RELEASE.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            lines.append(f"{digest}  {path.name}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Impedance Matching AI releases")
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    RELEASE.mkdir(exist_ok=True)
    source = build_source_zip()
    print(f"Source: {source} ({source.stat().st_size / 1024 / 1024:.1f} MB)")
    if not args.source_only:
        try:
            import PyInstaller  # noqa: F401
            import webview  # noqa: F401
        except ImportError as exc:
            print(f"Skip executable build: {exc}")
            print("Install with: pip install pyinstaller pywebview pythonnet")
        else:
            portable = build_portable()
            mcp = build_mcp()
            print(f"Portable: {portable} ({portable.stat().st_size / 1024 / 1024:.1f} MB)")
            print(f"MCP     : {mcp} ({mcp.stat().st_size / 1024 / 1024:.1f} MB)")
    checksums = write_checksums()
    print(f"Checksums: {checksums}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
