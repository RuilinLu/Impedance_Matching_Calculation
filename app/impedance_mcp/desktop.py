"""Native desktop window for Impedance Matching AI (WebView2, no external browser).

The existing HTML UI is served by the local HTTP API on 127.0.0.1 and rendered
inside a WebView2 window created with pywebview.  The window has a normal
Windows frame, icon, taskbar entry and Alt+F4 handling; no browser tab or
command prompt is opened.
"""

from __future__ import annotations

import argparse
import ctypes
import sys
import threading
import traceback
from pathlib import Path
from typing import List, Optional

from . import config, web_server

TITLE = f"Impedance Matching AI v{config.VERSION}"


def _message_box(text: str, title: str = TITLE, error: bool = True) -> None:
    flags = 0x10 if error else 0x40  # MB_ICONERROR / MB_ICONINFORMATION
    try:
        ctypes.windll.user32.MessageBoxW(None, text, title, flags | 0x40000)
    except Exception:
        pass


def _webview2_runtime_hint() -> str:
    return (
        "未检测到 Microsoft Edge WebView2 Runtime，无法创建原生窗口。\n\n"
        "请重新运行 Impedance Matching AI 安装程序（会自动安装 WebView2），"
        "或从 Microsoft 官网安装 Evergreen WebView2 Runtime 后重试。\n\n"
        "如需临时使用浏览器界面，可运行：\n"
        "ImpedanceMatchingAI.exe --browser"
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Impedance Matching AI native window")
    parser.add_argument("--port", type=int, default=0,
                        help="固定本地端口；0 表示自动选择空闲端口")
    parser.add_argument("--debug", action="store_true", help="启用 WebView 调试")
    args = parser.parse_args(argv)

    try:
        import webview
    except Exception as exc:  # noqa: BLE001
        _message_box(
            "原生窗口组件未安装。\n\n"
            f"{exc}\n\n"
            "源码运行请执行：pip install pywebview pythonnet\n"
            "安装版请重新运行安装程序。",
        )
        return 1

    httpd = None
    try:
        httpd = web_server.create_server("127.0.0.1", args.port)
    except OSError as exc:
        _message_box(f"无法启动本地计算服务：{exc}")
        return 1

    port = httpd.server_address[1]
    url = f"http://127.0.0.1:{port}/"
    url_root = url
    server_thread = threading.Thread(
        target=httpd.serve_forever,
        kwargs={"poll_interval": 0.2},
        name="impedance-http",
        daemon=True,
    )
    server_thread.start()

    storage = config.PROJECT_ROOT / "webview"
    try:
        storage.mkdir(parents=True, exist_ok=True)
        icon = config.WEB_DIR / "icon.ico"

        class NativeApi:
            """Small JS bridge so reports/help open in native child windows."""

            def open_window(self, url: str) -> bool:
                if not isinstance(url, str) or not url.startswith(url_root):
                    return False
                try:
                    webview.create_window(
                        "Impedance Matching AI · 文档 / 报告",
                        url=url,
                        width=1200,
                        height=850,
                        min_size=(900, 600),
                        resizable=True,
                        text_select=True,
                        background_color="#0b1220",
                    )
                    return True
                except Exception:
                    return False

        window = webview.create_window(
            TITLE,
            url=url,
            width=1440,
            height=900,
            min_size=(1100, 700),
            resizable=True,
            text_select=True,
            confirm_close=False,
            background_color="#0b1220",
            js_api=NativeApi(),
        )
        webview.start(
            gui="edgechromium",
            debug=bool(args.debug),
            private_mode=False,
            storage_path=str(storage),
            icon=str(icon) if icon.exists() else None,
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        detail = str(exc)
        if "webview2" in detail.lower() or "edge" in detail.lower():
            _message_box(_webview2_runtime_hint())
        else:
            _message_box(
                "原生窗口启动失败。\n\n"
                f"{detail}\n\n"
                "可运行 ImpedanceMatchingAI.exe --browser 使用浏览器界面，"
                "并把上述错误信息反馈给开发者。"
            )
        if args.debug:
            traceback.print_exc()
        return 1
    finally:
        try:
            httpd.shutdown()
            httpd.server_close()
            server_thread.join(timeout=3)
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
