"""Build one downloadable bundle for the GitHub Release.

Everything needed for a fresh Windows x64 machine is included except the
MATLAB Runtime itself (the official ZIP is larger than GitHub's 2 GiB
per-asset limit).  The bundle contains a link file for the official Runtime
page and the original V3.0 MATLAB executable + VC++ redistributable.
"""

from __future__ import annotations

import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "4.3.0"
RELEASE = ROOT / "release"
APP_RELEASE = ROOT / "APP_Release_Release_Version"
BUNDLE = RELEASE / f"ImpedanceMCP_v{VERSION}_Full_Bundle.zip"

FILES = [
    (RELEASE / f"ImpedanceMCP_Setup_v{VERSION}.exe", f"Installer/ImpedanceMCP_Setup_v{VERSION}.exe"),
    (RELEASE / f"ImpedanceMCP_v{VERSION}_Portable.exe", f"Portable/ImpedanceMCP_v{VERSION}_Portable.exe"),
    (RELEASE / f"ImpedanceMCP_v{VERSION}_Portable_MCP.exe", f"Portable/ImpedanceMCP_v{VERSION}_Portable_MCP.exe"),
    (RELEASE / f"ImpedanceMCP_v{VERSION}_Source.zip", f"Source/ImpedanceMCP_v{VERSION}_Source.zip"),
    (RELEASE / f"User_Manual_v{VERSION}.pdf", f"Docs/User_Manual_v{VERSION}.pdf"),
    (RELEASE / f"White_Paper_v{VERSION}.pdf", f"Docs/White_Paper_v{VERSION}.pdf"),
    (RELEASE / f"Competition_Dossier_v{VERSION}.pdf", f"Docs/Competition_Dossier_v{VERSION}.pdf"),
    (RELEASE / f"MCP_Compatibility_v{VERSION}.pdf", f"Docs/MCP_Compatibility_v{VERSION}.pdf"),
    (RELEASE / f"Calculation_Audit_v{VERSION}.pdf", f"Docs/Calculation_Audit_v{VERSION}.pdf"),
    (RELEASE / f"Installation_And_Antivirus_v{VERSION}.pdf", f"Docs/Installation_And_Antivirus_v{VERSION}.pdf"),
    (APP_RELEASE / "ReadMe" / "Readme_First_Installation_Instruction.pdf", "Docs/Readme_First_Installation_Instruction.pdf"),
    (APP_RELEASE / "Reference" / "My_APP_Introduction.pdf", "Docs/My_APP_Introduction.pdf"),
    (RELEASE / "RELEASE_NOTES.md", "Docs/RELEASE_NOTES.md"),
    (ROOT / "installer" / "LICENSE.txt", "LICENSE.txt"),
    (ROOT / "installer" / "README.txt", "README.txt"),
    (ROOT / "installer" / "vendor" / "classic" / "Impedance_Matching.exe",
     "Classic/Impedance_Matching.exe"),
    (ROOT / "installer" / "vendor" / "classic" / "readme.txt",
     "Classic/readme.txt"),
    (APP_RELEASE / "Problem_Solution" / "VC_redist.x64.exe",
     "Prerequisites/VC_redist.x64.exe"),
    (ROOT / "installer" / "vendor" / "MicrosoftEdgeWebview2Setup.exe",
     "Prerequisites/MicrosoftEdgeWebview2Setup.exe"),
]

START = f"""智配芯生 · ImpedanceMCP v{VERSION} 一键下载包
================================================

推荐顺序
--------
1. Installer/ImpedanceMCP_Setup_v{VERSION}.exe
   双击安装。程序是原生 Windows 窗口，不需要 Python / MATLAB / Node.js。
   安装器会自动安装 Microsoft Edge WebView2 Runtime（缺失时）。

2. Portable/
   免安装便携版：ImpedanceMCP_v{VERSION}_Portable.exe（原生窗口）。
   MCP 客户端请使用：ImpedanceMCP_v{VERSION}_Portable_MCP.exe --mcp

3. Source/
   完整源码、测试、文档与构建脚本。

原版 MATLAB 经典界面（可选）
----------------------------
Classic/Impedance_Matching.exe 是原 V3.0 程序，运行需要：
  - Prerequisites/VC_redist.x64.exe
  - MATLAB Runtime R2023b Update 10

MATLAB Runtime 没有放进本压缩包：
  - 官方完整 Windows ZIP 约 4.64 GB，超过 GitHub 单文件 2 GiB 限制；
  - 项目内的 MyAppInstaller_mcr.exe（约 974 MB）也未放入，以控制包体积；
  - 新版 ImpedanceMCP 与 MCP 不需要 Runtime，只有 Classic 需要。
请按 Prerequisites/MATLAB_Runtime_Download.txt 的官方链接下载。

一键彻底卸载
------------
开始菜单 / 桌面「一键卸载 ImpedanceMCP（清除全部数据）」，或安装目录
unins000.exe。会关闭运行中的程序，并删除程序、用户数据、API Key、上传、
报告、WebView2 缓存、MCP 配置、快捷方式和注册表项。

校验
----
SHA256SUMS.txt 列出本包内所有文件的 SHA-256。
Windows 可用：
  certutil -hashfile Installer\\ImpedanceMCP_Setup_v{VERSION}.exe SHA256

联系
----
radarlurui@gmail.com ｜ Lu_Skywalker2915@sjtu.edu.cn
https://github.com/RuilinLu/Impedance_Matching_Calculation
"""

RUNTIME = """MATLAB Runtime R2023b Update 10（仅原版 Classic 需要）
=========================================================

官方下载页面：
https://ww2.mathworks.cn/products/compiler/matlab-runtime.html

请选择：
  - Release: R2023b
  - Update: Update 10（或更高兼容更新）
  - Platform: Windows 64-bit
  - 下载 Runtime Installer / ZIP 后安装

为什么没有放进 GitHub Release：
  - 官方完整 ZIP 为 4,643,967,798 bytes（约 4.32 GiB）
  - GitHub Release 单个文件上限为 2 GiB，无法上传
  - 项目内 MyAppInstaller_mcr.exe 约 974 MB，也未放入本包
  - 新版 ImpedanceMCP 与 MCP 不需要 Runtime；只有
    Classic/Impedance_Matching.exe 需要
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    missing = [str(src) for src, _ in FILES if not src.is_file()]
    if missing:
        raise SystemExit("missing bundle inputs:\n" + "\n".join(missing))

    with tempfile.TemporaryDirectory(prefix="impedance_bundle_") as tmp:
        stage = Path(tmp)
        (stage / "START_HERE.txt").write_text(START, encoding="utf-8", newline="\n")
        (stage / "Prerequisites").mkdir(parents=True, exist_ok=True)
        (stage / "Prerequisites" / "MATLAB_Runtime_Download.txt").write_text(
            RUNTIME, encoding="utf-8", newline="\n")

        rows = []
        for src, rel in FILES:
            dst = stage / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            rows.append((rel.replace("\\", "/"), sha256(dst)))

        rows.append(("START_HERE.txt", sha256(stage / "START_HERE.txt")))
        rows.append(("Prerequisites/MATLAB_Runtime_Download.txt",
                     sha256(stage / "Prerequisites" / "MATLAB_Runtime_Download.txt")))
        rows.sort()
        (stage / "SHA256SUMS.txt").write_text(
            "".join(f"{h} *{name}\n" for name, h in rows), encoding="utf-8", newline="\n")

        if BUNDLE.exists():
            BUNDLE.unlink()
        with zipfile.ZipFile(BUNDLE, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(stage).as_posix())
    size_mb = BUNDLE.stat().st_size / 1024 / 1024
    print(f"bundle: {BUNDLE} ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
