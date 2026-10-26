"""Bridge to the original MATLAB application and to MATLAB R2025b batch mode.

Safety notes
------------
* The classic GUI is started with ``os.startfile`` after validating that the
  executable lives inside the project tree.  No shell string is ever built.
* MATLAB batch mode uses an argument list (``shell=False``); the executable is
  discovered from a fixed set of MATLAB install roots and every path passed to
  it is a temporary file created by this module.  User data only travels inside
  those JSON files.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import config, engine


def _safe_classic_path(exe: str) -> Path:
    path = Path(exe).resolve()
    root = config.PROJECT_ROOT.resolve()
    if root not in path.parents:
        raise ValueError("可执行文件不在项目目录内，已拒绝启动")
    if path.suffix.lower() != ".exe" or path.name.lower() != "impedance_matching.exe":
        raise ValueError("不是受信任的 Impedance_Matching.exe")
    if not path.is_file():
        raise ValueError("可执行文件不存在")
    return path


def _safe_matlab_path(matlab: str) -> Path:
    path = Path(matlab).resolve()
    if not path.is_file() or path.name.lower() != "matlab.exe":
        raise ValueError("不是受信任的 matlab.exe")
    # The executable must sit in a .../MATLAB/R20xx/bin/ directory.
    if not re.search(r"MATLAB[\\/]R\d{4}[ab][\\/]bin$", str(path.parent), re.I):
        raise ValueError("matlab.exe 不在标准 MATLAB 安装目录中")
    return path


def launch_classic_app() -> Dict[str, Any]:
    exe = config.find_classic_app()
    if not exe:
        return {
            "ok": False,
            "error_code": "app_not_found",
            "message": "未找到 Impedance_Matching.exe",
            "hint": "请先运行 Main_Installation/MyAppInstaller_mcr.exe 安装原版软件，"
                    "或在设置中指定 exe 路径。",
            "summary": "未找到原版 MATLAB 可执行文件。",
        }
    try:
        safe = _safe_classic_path(exe)
        if os.name != "nt":
            return {"ok": False, "error_code": "unsupported_os",
                    "message": "原版 exe 仅支持 Windows", "summary": "仅支持 Windows。"}
        os.startfile(str(safe))  # type: ignore[attr-defined]
        return {
            "ok": True,
            "path": str(safe),
            "summary": f"已启动原版 MATLAB 界面：{safe.name}",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "error_code": "launch_failed",
            "message": str(exc),
            "hint": "请确认已安装 MATLAB Runtime R2023b 与 VC++ 运行库。",
            "summary": f"启动失败：{exc}",
        }


def _run_matlab(statement: str, cwd: Path, timeout: int) -> subprocess.CompletedProcess:
    matlab = config.find_matlab()
    if not matlab:
        raise FileNotFoundError("未检测到 MATLAB 安装")
    safe = _safe_matlab_path(matlab)
    # Argument list, no shell.  ``statement`` only contains trusted temp paths.
    argv = [str(safe), "-nosplash", "-nodesktop", "-batch", statement]
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True,
                          timeout=timeout, encoding="utf-8", errors="replace",
                          shell=False, check=False)


def run_matlab_design(
    topology: str,
    frequency_mhz: float,
    load_r: float,
    load_x: float,
    L_uh: Optional[float],
    c3_pf: Optional[float],
    z0: float = 50.0,
    timeout: int = 240,
) -> Dict[str, Any]:
    """Run one design in MATLAB R2025b and return its JSON result."""
    matlab = config.find_matlab()
    if not matlab:
        return {
            "ok": False,
            "error_code": "matlab_not_found",
            "message": "未检测到 MATLAB 安装",
            "hint": "安装 MATLAB R2025b，或在设置中填写 matlab.exe 路径。",
            "summary": "MATLAB 不可用。",
        }
    src = config.MATLAB_DIR
    driver = src / "mw_batch_entry.m"
    engine_file = src / "mw_design.m"
    if not driver.exists() or not engine_file.exists():
        return {
            "ok": False,
            "error_code": "driver_missing",
            "message": f"缺少 MATLAB 驱动文件：{driver}",
            "summary": "MATLAB 驱动文件缺失。",
        }
    work = Path(tempfile.mkdtemp(prefix="impedance_mcp_"))
    try:
        shutil.copy2(driver, work / driver.name)
        shutil.copy2(engine_file, work / engine_file.name)
        case = {
            "op": "design",
            "topology": engine.canonical_topology(topology),
            "frequency_mhz": float(frequency_mhz),
            "load_r": float(load_r),
            "load_x": float(load_x),
            "z0": float(z0),
            "L_uh": L_uh,
            "c3_pf": c3_pf,
        }
        inp = work / "input.json"
        out = work / "output.json"
        inp.write_text(json.dumps({"cases": [case]}, ensure_ascii=False), encoding="utf-8")
        stmt = f"mw_batch_entry('{inp.as_posix()}','{out.as_posix()}')"
        started = time.time()
        proc = _run_matlab(stmt, work, timeout)
        elapsed = time.time() - started
        if not out.exists():
            return {
                "ok": False,
                "error_code": "matlab_failed",
                "message": (proc.stderr or proc.stdout or "MATLAB 未生成输出")[-1200:],
                "hint": "检查 MATLAB 许可证与 mw_design.m 是否可运行。",
                "elapsed_s": elapsed,
                "summary": "MATLAB 计算失败。",
            }
        data = json.loads(out.read_text(encoding="utf-8"))
        item = data[0] if isinstance(data, list) and data else data
        item["ok"] = bool(item.get("ok", True))
        item["engine"] = "matlab-r2025b"
        item["elapsed_s"] = elapsed
        item["summary"] = (
            f"MATLAB 复核完成：Zin={item.get('input_impedance_display', '—')} Ω，"
            f"VSWR={item.get('vswr', float('nan')):.6f}，耗时 {elapsed:.1f}s。"
        )
        return item
    except subprocess.TimeoutExpired:
        return {"ok": False, "error_code": "matlab_timeout",
                "message": f"MATLAB 超时（>{timeout}s）", "summary": "MATLAB 计算超时。"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error_code": "matlab_error", "message": str(exc),
                "summary": f"MATLAB 调用失败：{exc}"}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def cross_check(cases: List[Dict[str, Any]], timeout: int = 300) -> Dict[str, Any]:
    """Run a batch of design cases in MATLAB and compare with the Python engine."""
    matlab = config.find_matlab()
    if not matlab:
        return {"ok": False, "message": "未检测到 MATLAB", "results": []}
    src = config.MATLAB_DIR
    work = Path(tempfile.mkdtemp(prefix="impedance_mcp_verify_"))
    try:
        shutil.copy2(src / "mw_batch_entry.m", work / "mw_batch_entry.m")
        shutil.copy2(src / "mw_design.m", work / "mw_design.m")
        inp = work / "input.json"
        out = work / "output.json"
        inp.write_text(json.dumps({"cases": cases}, ensure_ascii=False), encoding="utf-8")
        stmt = f"mw_batch_entry('{inp.as_posix()}','{out.as_posix()}')"
        proc = _run_matlab(stmt, work, timeout)
        if not out.exists():
            return {"ok": False, "message": (proc.stderr or proc.stdout)[-1500:], "results": []}
        matlab_results = json.loads(out.read_text(encoding="utf-8"))
        compared = []
        for case, m in zip(cases, matlab_results):
            py = engine.design_network(
                case["topology"], case["frequency_mhz"], case["load_r"],
                case.get("load_x", 0.0), case.get("z0", 50.0),
                L_uh=case.get("L_uh"), c3_pf=case.get("c3_pf"),
            )
            dv = abs(complex(py["input_impedance"]["re"], py["input_impedance"]["im"]) -
                     complex(m.get("zin_re", 0), m.get("zin_im", 0)))
            compared.append({
                "topology": case["topology"],
                "python": {
                    "L_uH": py["components"]["L_uH"],
                    "C1_pF": py["components"]["C1_pF"],
                    "C2_pF": py["components"]["C2_pF"],
                    "C3_pF": py["components"]["C3_pF"],
                    "vswr": py["vswr"],
                },
                "matlab": m,
                "zin_delta": dv,
                "pass": bool(m.get("ok")) and dv < 1e-3,
            })
        passed = sum(1 for c in compared if c["pass"])
        return {
            "ok": passed == len(compared),
            "passed": passed,
            "total": len(compared),
            "results": compared,
            "summary": f"MATLAB 交叉验证：{passed}/{len(compared)} 通过。",
        }
    finally:
        shutil.rmtree(work, ignore_errors=True)


def status() -> Dict[str, Any]:
    s = config.matlab_status()
    s["ok"] = True
    s["summary"] = (
        f"MATLAB：{s['matlab_version'] or '未安装'}；"
        f"原版 exe：{'已找到' if s['classic_app_available'] else '未找到'}；"
        f"Runtime：{'已安装' if s['mcr_installed'] else '未检测到'}。"
    )
    return s
