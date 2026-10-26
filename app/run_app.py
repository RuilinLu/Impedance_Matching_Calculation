#!/usr/bin/env python
"""Start ImpedanceMCP in a native window (or `--browser` for the legacy UI)."""

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

if "--browser" in sys.argv or "--web" in sys.argv:
    from impedance_mcp.web_server import main  # noqa: E402
    sys.argv = [a for a in sys.argv if a not in ("--browser", "--web")]
else:
    from impedance_mcp.desktop import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
