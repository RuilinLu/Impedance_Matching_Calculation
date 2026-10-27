"""Startup release check against the project's GitHub repository.

Version comparison is deterministic (GitHub API).  When a model is configured,
the release notes are also sent to that model for a short compatibility review;
the model never decides whether an update exists.

Outbound HTTP is restricted to GitHub hosts with scheme/host/resolved-IP checks
and validated redirects.  Downloads use a file descriptor created by tempfile in
the application's own update directory, so no user-controlled path is opened.
"""

from __future__ import annotations

import ipaddress
import json
import os
import re
import socket
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from . import config, llm

CACHE_TTL_SECONDS = 6 * 3600
USER_AGENT = "ImpedanceMatchingAI-Updater/" + config.VERSION
ALLOWED_HOSTS = {"api.github.com", "github.com", "objects.githubusercontent.com",
                 "release-assets.githubusercontent.com"}
REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,80}/[A-Za-z0-9_.-]{1,120}$")
UPDATE_BASE = config.DATA_DIR / "updates"
UPDATE_FILES = {
    "exe": "ImpedanceMatchingAI_update_setup.exe",
    "msi": "ImpedanceMatchingAI_update_setup.msi",
}


def _repo_slug(cfg: Dict[str, Any]) -> str:
    raw = str((cfg.get("update") or {}).get("repo") or config.PROJECT_URL)
    match = re.search(r"github\.com[/:]([^/]+)/([^/#?]+)", raw)
    if not match:
        return "SkywalkerHolmes/Impedance_Matching_Calculation"
    owner, name = match.group(1), match.group(2)
    slug = f"{owner}/{name.removesuffix('.git')}"
    return slug if REPO_PATTERN.match(slug) else "SkywalkerHolmes/Impedance_Matching_Calculation"


# ---------------------------------------------------------------------------
# Restricted HTTP
# ---------------------------------------------------------------------------

def _validate_target(target: str) -> str:
    parsed = urllib.parse.urlparse(str(target or ""))
    if parsed.scheme != "https":
        raise ValueError("只允许 https 更新地址")
    if parsed.username or parsed.password:
        raise ValueError("更新地址不能包含凭据")
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise ValueError("更新地址不属于 GitHub 官方域名")
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError(f"无法解析更新主机：{exc}") from exc
    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if (address.is_private or address.is_loopback or address.is_link_local
                or address.is_reserved or address.is_multicast or address.is_unspecified):
            raise ValueError("更新主机解析到非公网地址，已拒绝请求")
    return parsed.geturl()


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        safe = _validate_target(newurl)
        return super().redirect_request(req, fp, code, msg, headers, safe)


def _safe_urlopen(target: str, timeout: float = 9.0):
    safe = _validate_target(target)
    opener = urllib.request.build_opener(_SafeRedirectHandler())
    request = urllib.request.Request(safe, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json, application/octet-stream",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    return opener.open(request, timeout=timeout)


# ---------------------------------------------------------------------------
# Version comparison and release lookup
# ---------------------------------------------------------------------------

def version_tuple(value: str) -> Tuple[int, ...]:
    parts = re.findall(r"\d+", str(value or ""))
    return tuple(int(part) for part in parts[:4]) + (0,) * (4 - len(parts[:4]))


def is_newer(latest: str, current: str) -> bool:
    return version_tuple(latest) > version_tuple(current)


def _cache_read() -> Dict[str, Any]:
    try:
        data = json.loads(config.UPDATE_CACHE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _cache_write(payload: Dict[str, Any]) -> None:
    try:
        config.ensure_dirs()
        config.UPDATE_CACHE_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def fetch_latest(repo: str, timeout: float = 9.0) -> Dict[str, Any]:
    if not REPO_PATTERN.match(str(repo)):
        raise RuntimeError("仓库标识无效")
    api = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        with _safe_urlopen(api, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise RuntimeError("仓库尚未发布任何正式版本") from exc
        raise RuntimeError(f"GitHub 返回 HTTP {exc.code}") from exc
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"无法连接 GitHub：{exc}") from exc
    assets = []
    for item in data.get("assets") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "")
        asset_url = str(item.get("browser_download_url") or "")
        if not name or not asset_url:
            continue
        assets.append({"name": name, "url": asset_url,
                       "size": int(item.get("size") or 0),
                       "downloads": int(item.get("download_count") or 0)})
    return {
        "tag": str(data.get("tag_name") or "").strip(),
        "name": str(data.get("name") or data.get("tag_name") or "").strip(),
        "body": str(data.get("body") or ""),
        "html_url": str(data.get("html_url") or ""),
        "published_at": str(data.get("published_at") or ""),
        "prerelease": bool(data.get("prerelease")),
        "assets": assets,
    }


def _model_review(cfg: Dict[str, Any], current: str, latest: Dict[str, Any],
                  timeout: int = 60) -> Optional[Dict[str, Any]]:
    status = config.llm_status(cfg)
    if not status.get("configured"):
        return None
    notes = latest.get("body") or ""
    if len(notes) > 6000:
        notes = notes[:6000] + "…"
    messages = [
        {"role": "system",
         "content": ("你是软件更新审查助手。只根据给定的版本说明判断兼容性，"
                     "用简体中文输出一个 JSON 对象，不要 Markdown。字段："
                     "summary（两句话以内）、highlights（最多 4 条字符串数组）、"
                     "compatibility（对旧版本用户数据的兼容性说明）、"
                     "recommendation（strongly_recommended / recommended / optional / caution）。"
                     "如果说明中没有兼容性信息，请明确写“未提及”。")},
        {"role": "user",
         "content": (f"当前版本：{current}\n最新版本：{latest.get('tag')}\n"
                     f"版本说明：\n{notes or '（发布说明为空）'}")},
    ]
    try:
        response = llm.chat(cfg, messages, tools=None, timeout=timeout)
    except Exception:
        return None
    text = str(response.get("content") or "").strip()
    if not text:
        return None
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        text = match.group(0)
    try:
        data = json.loads(text)
    except Exception:
        return {"summary": text[:800], "highlights": [], "compatibility": "",
                "recommendation": "optional"}
    if not isinstance(data, dict):
        return None
    return {
        "summary": str(data.get("summary") or "")[:800],
        "highlights": [str(item)[:240] for item in (data.get("highlights") or [])][:4],
        "compatibility": str(data.get("compatibility") or "")[:800],
        "recommendation": str(data.get("recommendation") or "optional")[:40],
        "model": status.get("model") or "",
    }


def check(cfg: Optional[Dict[str, Any]] = None, force: bool = False,
          use_model: Optional[bool] = None) -> Dict[str, Any]:
    cfg = cfg or config.load_config()
    update_cfg = cfg.get("update") or {}
    repo = _repo_slug(cfg)
    current = config.VERSION
    cached = _cache_read()
    cached_at = float(cached.get("checked_at") or 0)
    fresh = ((time.time() - cached_at) < CACHE_TTL_SECONDS
             and cached.get("current") == current)
    if not force and fresh and cached.get("repo") == repo and cached.get("latest"):
        result = dict(cached["latest"])
        result["from_cache"] = True
        result["has_update"] = is_newer(result.get("version", ""), current)
        result["skipped"] = str(update_cfg.get("skipped_version") or "") == result.get("version")
        return {"ok": True, "current": current, "repo": repo,
                "checked_at": cached.get("checked_at_iso", ""), **result}
    try:
        release = fetch_latest(repo)
    except (RuntimeError, ValueError) as exc:
        if cached.get("latest"):
            result = dict(cached["latest"])
            result["from_cache"] = True
            result["has_update"] = is_newer(result.get("version", ""), current)
            result["skipped"] = str(update_cfg.get("skipped_version") or "") == result.get("version")
            return {"ok": True, "current": current, "repo": repo,
                    "warning": str(exc), "checked_at": cached.get("checked_at_iso", ""),
                    **result}
        return {"ok": False, "current": current, "repo": repo,
                "error": str(exc), "hint": "可以稍后在“关于/设置”中手动检查。"}
    version = release["tag"].lstrip("vV")
    if not version:
        return {"ok": False, "current": current, "repo": repo,
                "error": "最新发布没有可识别的版本号"}
    has_update = is_newer(version, current)
    if use_model is None:
        use_model = bool(update_cfg.get("use_model", True))
    review = None
    if has_update and use_model:
        review = _model_review(cfg, current, release)
    payload = {
        "version": version,
        "tag": release["tag"],
        "name": release["name"],
        "notes": release["body"][:12000],
        "html_url": release["html_url"],
        "published_at": release["published_at"],
        "prerelease": release["prerelease"],
        "assets": release["assets"],
        "setup_asset": next((item for item in release["assets"]
                             if item["name"].lower().endswith(("setup.exe", ".msi"))), None),
        "has_update": has_update,
        "from_cache": False,
        "ai_review": review,
    }
    try:
        _cache_write({"checked_at": time.time(),
                      "checked_at_iso": time.strftime("%Y-%m-%d %H:%M:%S"),
                      "current": current,
                      "repo": repo,
                      "latest": {key: value for key, value in payload.items()
                                 if key not in ("has_update",)}})
    except Exception:
        pass
    payload["skipped"] = str(update_cfg.get("skipped_version") or "") == version
    return {"ok": True, "current": current, "repo": repo,
            "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"), **payload}


def skip_version(version: str) -> None:
    config.save_config({"update": {"skipped_version": str(version or "")}})


# ---------------------------------------------------------------------------
# Update download (tempfile descriptor, fixed destination)
# ---------------------------------------------------------------------------

_DOWNLOAD = {"state": "idle", "downloaded": 0, "total": 0, "kind": "exe", "error": ""}
_DOWNLOAD_LOCK = threading.Lock()
_DOWNLOAD_THREAD: Optional[threading.Thread] = None


def _update_dir() -> Path:
    base = (config.DATA_DIR / "updates").resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def download_path(kind: str = "exe") -> Path:
    base = _update_dir()
    name = UPDATE_FILES.get(str(kind).lower(), UPDATE_FILES["exe"])
    candidate = (base / name).resolve()
    if candidate.parent != base or candidate.name != name:
        raise ValueError("更新包路径越界")
    return candidate


def download_progress() -> Dict[str, Any]:
    with _DOWNLOAD_LOCK:
        data = dict(_DOWNLOAD)
    total = int(data.get("total") or 0)
    data["percent"] = round(100.0 * data["downloaded"] / total, 1) if total else 0.0
    data["path"] = str(download_path(data.get("kind", "exe"))) if data.get("state") == "done" else ""
    return data


def start_download(asset_url: str) -> Dict[str, Any]:
    global _DOWNLOAD_THREAD
    safe = _validate_target(asset_url)
    with _DOWNLOAD_LOCK:
        if _DOWNLOAD_THREAD and _DOWNLOAD_THREAD.is_alive():
            return download_progress()
        kind = "msi" if urllib.parse.urlparse(safe).path.lower().endswith(".msi") else "exe"
        _DOWNLOAD.update({"state": "running", "downloaded": 0, "total": 0,
                          "kind": kind, "error": ""})
    target = download_path(kind)

    def worker() -> None:
        temp_name = ""
        try:
            base = str(_update_dir())
            with tempfile.NamedTemporaryFile(mode="wb", prefix="ima_update_",
                                             suffix=".part", dir=base,
                                             delete=False) as handle:
                temp_name = handle.name
                with _safe_urlopen(safe, timeout=60) as response:
                    total = int(response.headers.get("Content-Length") or 0)
                    with _DOWNLOAD_LOCK:
                        _DOWNLOAD["total"] = total
                    read = 0
                    while True:
                        chunk = response.read(1024 * 512)
                        if not chunk:
                            break
                        handle.write(chunk)
                        read += len(chunk)
                        with _DOWNLOAD_LOCK:
                            _DOWNLOAD["downloaded"] = read
            if os.path.dirname(os.path.abspath(temp_name)) != base:
                raise ValueError("临时更新包不在下载目录内")
            os.replace(temp_name, str(target))
            size = target.stat().st_size
            with _DOWNLOAD_LOCK:
                _DOWNLOAD.update({"state": "done", "downloaded": size, "total": size})
        except Exception as exc:  # noqa: BLE001
            if temp_name:
                try:
                    if os.path.isfile(temp_name):
                        os.unlink(temp_name)
                except Exception:
                    pass
            with _DOWNLOAD_LOCK:
                _DOWNLOAD.update({"state": "error", "error": str(exc)})

    _DOWNLOAD_THREAD = threading.Thread(target=worker, name="update-download", daemon=True)
    _DOWNLOAD_THREAD.start()
    return download_progress()


def install_downloaded() -> Dict[str, Any]:
    with _DOWNLOAD_LOCK:
        kind = str(_DOWNLOAD.get("kind") or "exe")
        state = str(_DOWNLOAD.get("state") or "idle")
    if state != "done":
        raise ValueError("更新包尚未下载完成")
    target = download_path(kind)
    if not target.is_file():
        raise ValueError("更新包文件不存在")
    try:
        os.startfile(str(target))  # type: ignore[attr-defined]
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"无法启动安装程序：{exc}") from exc
    return {"ok": True, "path": str(target)}
