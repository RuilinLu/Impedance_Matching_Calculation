#!/usr/bin/env python
"""Single launcher used by the Windows executable and by `python app/launcher.py`.

    ImpedanceMCP.exe                 -> start the standalone web app
    ImpedanceMCP.exe --mcp           -> start the MCP stdio server
    ImpedanceMCP.exe --mcp --http 8790 -> start the MCP HTTP server
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
    if "--mcp" in args:
        args = [a for a in args if a != "--mcp"]
        from impedance_mcp.mcp_server import main as mcp_main
        return mcp_main(args)
    from impedance_mcp.web_server import main as web_main
    return web_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
