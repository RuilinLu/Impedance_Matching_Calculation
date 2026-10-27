"""Generated media artefacts (Smith-chart SVGs) shared by chat and the UI.

Only files written by this module are served back to the WebView.  Names are
hashes plus a fixed extension, so a request can never escape the media folder.
"""

from __future__ import annotations

import hashlib
import html
import math
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import config

NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{8,80}\.(?:svg|png|jpg|jpeg|webp|gif|mp4|webm|mp3|wav|pdf|txt|csv)$")
MAX_SERVE_BYTES = 40 * 1024 * 1024


def _media_dir() -> Path:
    config.ensure_dirs()
    return config.MEDIA_DIR


def save_bytes(name: str, raw: bytes, suffix: str = "") -> Dict[str, Any]:
    """Persist generated media under the data directory and return a URL."""
    suffix = (suffix or Path(name).suffix or ".bin").lower()
    if not suffix.startswith("."):
        suffix = "." + suffix
    digest = hashlib.sha256(raw).hexdigest()[:20]
    safe_name = f"chat_{digest}{suffix}"
    path = _media_dir() / safe_name
    if not path.is_file():
        path.write_bytes(raw)
    return {
        "name": safe_name,
        "url": f"/api/media/{safe_name}",
        "bytes": len(raw),
        "mime": _mime_for(suffix),
    }


def _mime_for(suffix: str) -> str:
    return {
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".pdf": "application/pdf",
        ".txt": "text/plain; charset=utf-8",
        ".csv": "text/csv; charset=utf-8",
    }.get(suffix.lower(), "application/octet-stream")


def resolve(name: str) -> Optional[Path]:
    safe = Path(str(name or "")).name
    if not NAME_PATTERN.match(safe):
        return None
    for base in (_media_dir(), config.REPORT_DIR):
        target = (base / safe).resolve()
        try:
            target.relative_to(base.resolve())
        except ValueError:
            continue
        if target.is_file() and target.stat().st_size <= MAX_SERVE_BYTES:
            return target
    return None


def content_type(path: Path) -> str:
    return _mime_for(path.suffix)


def _escape(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def smith_chart_svg(trajectory: Dict[str, Any], width: int = 760,
                    height: int = 760) -> bytes:
    """Render a Smith chart plus the matching trajectory as a standalone SVG."""
    z0 = float(trajectory.get("z0") or 50.0)
    load = trajectory.get("load") or {}
    load_r = float(load.get("r") or 0.0)
    load_x = float(load.get("x") or 0.0)
    center = (width / 2.0, height / 2.0)
    radius = min(width, height) * 0.40
    palette = ["#22d3ee", "#34d399", "#fbbf24", "#f472b6", "#a78bfa", "#fb7185"]

    def to_xy(gamma: Dict[str, Any]) -> Tuple[float, float]:
        re = float(gamma.get("re") or 0.0)
        im = float(gamma.get("im") or 0.0)
        return center[0] + re * radius, center[1] - im * radius

    parts: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Smith chart trajectory">',
        '<defs><radialGradient id="bg" cx="50%" cy="45%" r="70%">'
        '<stop offset="0%" stop-color="#12233c"/><stop offset="100%" stop-color="#07111f"/>'
        '</radialGradient></defs>',
        f'<rect width="{width}" height="{height}" rx="18" fill="url(#bg)" '
        f'stroke="#1e3852"/>',
    ]
    # Resistance circles: |Γ - r/(1+r)| = 1/(1+r)
    for r_value in (0, 0.2, 0.5, 1, 2, 5, 10, 20, 50):
        cx = center[0] + radius * r_value / (1.0 + r_value)
        cr = radius / (1.0 + r_value)
        parts.append(f'<circle cx="{cx:.2f}" cy="{center[1]:.2f}" r="{cr:.2f}" '
                     f'fill="none" stroke="#2b4a69" stroke-width="1" opacity="0.75"/>')
    # Reactance arcs: circle centre (1, 1/x), radius 1/|x|
    for x_value in (0.2, 0.5, 1, 2, 5, 10):
        for sign in (1, -1):
            cx = center[0] + radius
            cy = center[1] - sign * radius / x_value
            cr = radius / x_value
            # Polar angles that keep the arc inside the unit circle.
            start = math.atan2(center[1] - cy, center[0] - cx)
            end = math.atan2(center[1] - cy, center[0] + radius - cx)
            sweep = 1 if sign > 0 else 0
            x1 = cx + cr * math.cos(start)
            y1 = cy + cr * math.sin(start)
            x2 = cx + cr * math.cos(end)
            y2 = cy + cr * math.sin(end)
            parts.append(f'<path d="M {x1:.2f} {y1:.2f} A {cr:.2f} {cr:.2f} 0 0 {sweep} '
                         f'{x2:.2f} {y2:.2f}" fill="none" stroke="#2b4a69" '
                         f'stroke-width="1" opacity="0.55"/>')
    parts.append(f'<circle cx="{center[0]:.2f}" cy="{center[1]:.2f}" r="{radius:.2f}" '
                 f'fill="none" stroke="#4fd1e0" stroke-width="1.4" opacity="0.9"/>')
    parts.append(f'<line x1="{center[0] - radius:.2f}" y1="{center[1]:.2f}" '
                 f'x2="{center[0] + radius:.2f}" y2="{center[1]:.2f}" '
                 f'stroke="#2b4a69" stroke-width="1"/>')

    legend: List[Tuple[str, str]] = []
    for index, step in enumerate(trajectory.get("steps") or []):
        points = step.get("points_gamma") or []
        if not points:
            continue
        color = palette[index % len(palette)]
        coords = [to_xy(point) for point in points if isinstance(point, dict)]
        if len(coords) < 2:
            continue
        d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in coords)
        parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3.2" '
                     f'stroke-linecap="round" opacity="0.95"/>')
        start = coords[0]
        parts.append(f'<circle cx="{start[0]:.2f}" cy="{start[1]:.2f}" r="3.6" '
                     f'fill="{color}" stroke="#07111f" stroke-width="1.2"/>')
        label = str(step.get("label") or step.get("element") or f"step {index + 1}")
        legend.append((color, label))

    load_gamma = trajectory.get("load_gamma") or {}
    if load_gamma:
        x, y = to_xy(load_gamma)
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="#f87171" '
                     f'stroke="#fff" stroke-width="1.6"/>')
    parts.append(f'<circle cx="{center[0]:.2f}" cy="{center[1]:.2f}" r="5" '
                 f'fill="#34d399" stroke="#07111f" stroke-width="1.4"/>')
    title = f'{trajectory.get("topology_name") or trajectory.get("topology") or "匹配网络"}'
    subtitle = (f'{float(trajectory.get("frequency_mhz") or 0):g} MHz · '
                f'Z0 = {z0:g} Ω · 负载 {load_r:g}{load_x:+g}j Ω')
    parts.append(f'<text x="28" y="38" fill="#e8f6ff" font-size="20" '
                 f'font-family="Segoe UI, Microsoft YaHei, sans-serif" font-weight="600">'
                 f'{_escape(title)}</text>')
    parts.append(f'<text x="28" y="62" fill="#8ba9c6" font-size="13" '
                 f'font-family="Segoe UI, Microsoft YaHei, sans-serif">{_escape(subtitle)}</text>')
    parts.append(f'<text x="{center[0]:.2f}" y="{center[1] + radius + 34:.2f}" '
                 f'text-anchor="middle" fill="#7f9ab5" font-size="12" '
                 f'font-family="Segoe UI, Microsoft YaHei, sans-serif">'
                 f'归一化阻抗圆图 · 红色为负载，绿色为匹配点</text>')
    legend_text = "  ".join(
        f'<tspan fill="{color}">●</tspan><tspan fill="#8ba9c6"> {_escape(label)}</tspan>'
        for color, label in legend[:6])
    parts.append(f'<text x="28" y="{height - 24}" fill="#8ba9c6" font-size="12" '
                 f'font-family="Segoe UI, Microsoft YaHei, sans-serif">'
                 f'{legend_text}</text>')
    parts.append("</svg>")
    return "".join(parts).encode("utf-8")


def trajectory_media(trajectory: Dict[str, Any]) -> Dict[str, Any]:
    """Create the SVG for a tool result and return an attachment descriptor."""
    raw = smith_chart_svg(trajectory)
    info = save_bytes("smith.svg", raw, ".svg")
    return {
        "type": "image",
        "url": info["url"],
        "name": info["name"],
        "mime": info["mime"],
        "title": f'{trajectory.get("topology_name") or "Smith"} 圆图轨迹',
        "bytes": info["bytes"],
    }
