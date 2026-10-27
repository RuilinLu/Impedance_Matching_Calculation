#!/usr/bin/env python
"""Single launcher used by the Windows executable and by `python app/launcher.py`.

    ImpedanceMatchingAI.exe            -> native desktop window (WebView2)
    ImpedanceMatchingAI.exe --browser  -> local browser UI (debug only)
    ImpedanceMatchingAI_MCP.exe --mcp  -> MCP stdio server
    ImpedanceMatchingAI_MCP.exe --mcp --http 8790 -> MCP HTTP/SSE server
"""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass


def main() -> int:
    args = list(sys.argv[1:])
    if "--init-data" in args:
        from impedance_mcp import config, library
        config.ensure_dirs()
        library.init_db()
        for directory in (config.INSTALL_DIR / "TextBook",
                          config.PROJECT_ROOT / "TextBook",
                          config.LIBRARY_DIR / "books"):
            directory.mkdir(parents=True, exist_ok=True)
            readme = directory / "README.txt"
            if not readme.exists():
                readme.write_text(
                    "Place textbooks here (PDF, DOCX, PPTX, XLSX, TXT, Markdown).\n"
                    "The application indexes them locally; files are never uploaded.\n",
                    encoding="utf-8",
                )
        print(f"Initialized data directory: {config.DATA_DIR}")
        return 0
    if "--cleanup" in args:
        args = [a for a in args if a != "--cleanup"]
        from impedance_mcp.cleanup import main as cleanup_main
        return cleanup_main(args)
    if "--configure-mcp" in args:
        i = args.index("--configure-mcp")
        targets = [a for a in args[i + 1:] if not a.startswith("--")]
        from impedance_mcp.configure_mcp import main as configure_main
        return configure_main(targets or ["zcode"])
    if "--mcp" in args:
        args = [a for a in args if a != "--mcp"]
        from impedance_mcp.mcp_server import main as mcp_main
        return mcp_main(args)
    if "--browser" in args or "--web" in args:
        args = [a for a in args if a not in ("--browser", "--web")]
        from impedance_mcp.web_server import main as web_main
        return web_main(args)
    from impedance_mcp.desktop import main as desktop_main
    return desktop_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
