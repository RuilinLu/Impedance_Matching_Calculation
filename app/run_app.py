#!/usr/bin/env python
"""Start the ImpedanceMCP desktop shell (local web UI + AI agent + REST API)."""

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

from impedance_mcp.web_server import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
