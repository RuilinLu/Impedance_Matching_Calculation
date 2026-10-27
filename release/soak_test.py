"""Long-running v4.5.0 stability and congestion soak test.

Runs HTTP API workers, MCP stdio batches, MCP Streamable HTTP workers and a
low-rate real-model chat loop for a configurable duration.  Writes a JSON
summary and periodically prints counters.

All network calls use ``http.client`` with a fixed loopback host/port; this is
a local stress harness, not a general-purpose HTTP client.

Usage:
    python release/soak_test.py --minutes 90 --workers 8 --pid <server-pid>
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import secrets
import socket
import statistics
import subprocess
import sys
import threading
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
REPORT = Path(os.environ.get("SOAK_REPORT", str(Path(os.environ.get("TEMP", ".")) / "ima_soak_report.json")))
MCP_SCRIPT = ROOT / "app" / "run_mcp.py"
HOST = "127.0.0.1"
API_PORT = 8766
MCP_PORT = 8791
RNG = secrets.SystemRandom()

TOKEN_POOL = ["Smith chart", "匹配网络", "reflection coefficient", "VSWR", "L型",
              "教材", "阻抗变换", "transmission line", "公式", "OCR", "MCP"]


def _available_port(start: int) -> int:
    for port in range(start, start + 30):
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            probe.bind((HOST, port))
            return port
        except OSError:
            continue
        finally:
            probe.close()
    raise RuntimeError("no free local port for the MCP HTTP soak")


class Counter:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.values: Dict[str, int] = {}
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[str] = []
        self.samples: List[Dict[str, Any]] = []

    def add(self, name: str, count: int = 1) -> None:
        with self.lock:
            self.values[name] = self.values.get(name, 0) + count

    def error(self, where: str, detail: str, status: Optional[int] = None) -> None:
        with self.lock:
            self.values["errors"] = self.values.get("errors", 0) + 1
            if len(self.errors) < 300:
                self.errors.append({"t": time.strftime("%H:%M:%S"), "where": where,
                                    "status": status, "detail": str(detail)[:500]})

    def warn(self, detail: str) -> None:
        with self.lock:
            self.values["warnings"] = self.values.get("warnings", 0) + 1
            if len(self.warnings) < 100:
                self.warnings.append(str(detail)[:500])


COUNTER = Counter()
STOP = threading.Event()
START = time.time()


def _connect(port: int, timeout: float = 60.0) -> http.client.HTTPConnection:
    return http.client.HTTPConnection(HOST, port, timeout=timeout)


def _socket_retryable(exc: BaseException) -> bool:
    return getattr(exc, "winerror", None) == 10048 or getattr(exc, "errno", None) == 10048


def post_json(path: str, payload: Any, timeout: float = 60.0,
              port: int = API_PORT, headers: Optional[Dict[str, str]] = None) -> Any:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    for attempt in range(3):
        conn = _connect(port, timeout)
        try:
            conn.request("POST", path, body=body, headers={
                "Content-Type": "application/json", **(headers or {})})
            response = conn.getresponse()
            raw = response.read()
            if response.status >= 400:
                raise RuntimeError(f"HTTP {response.status}: {raw[:300].decode('utf-8', 'replace')}")
            return json.loads(raw.decode("utf-8"))
        except OSError as exc:
            if attempt < 2 and _socket_retryable(exc):
                COUNTER.add("client-socket-retries")
                time.sleep(0.15 * (attempt + 1))
                continue
            raise
        finally:
            conn.close()
    raise RuntimeError("request retries exhausted")


def get_json(path: str, timeout: float = 60.0, port: int = API_PORT) -> Any:
    for attempt in range(3):
        conn = _connect(port, timeout)
        try:
            conn.request("GET", path, headers={"Accept": "application/json"})
            response = conn.getresponse()
            raw = response.read()
            if response.status >= 400:
                raise RuntimeError(f"HTTP {response.status}: {raw[:300].decode('utf-8', 'replace')}")
            return json.loads(raw.decode("utf-8"))
        except OSError as exc:
            if attempt < 2 and _socket_retryable(exc):
                COUNTER.add("client-socket-retries")
                time.sleep(0.15 * (attempt + 1))
                continue
            raise
        finally:
            conn.close()
    raise RuntimeError("request retries exhausted")


def random_design() -> Dict[str, Any]:
    return {
        "topology": RNG.choice(["auto", "l_right", "l_left", "t", "pi1", "pi2"]),
        "frequency_mhz": RNG.choice([13.56, 100, 433, 915, 1800, 2400, 3500, 5800, 10000]),
        "load_r": round(10 ** RNG.uniform(-0.6, 2.1), 3),
        "load_x": round(RNG.uniform(-250, 250), 3),
        "z0": RNG.choice([50.0, 50.0, 50.0, 75.0]),
        "power_w": RNG.choice([1.0, 10.0, 50.0]),
    }


def http_worker(index: int) -> None:
    while not STOP.is_set():
        op = RNG.choices(
            ["design", "evaluate", "docs", "library", "status", "bandwidth",
             "stress", "scan", "upload", "invalid"],
            weights=[28, 20, 13, 13, 8, 6, 5, 3, 2, 2], k=1)[0]
        try:
            if op == "design":
                payload = random_design()
                result = post_json("/api/design", payload)
                COUNTER.add("design")
                if result.get("ok"):
                    d = result
                    if not (d.get("vswr", 9) <= 1.02):
                        COUNTER.error("design-vswr", json.dumps(payload), None)
                    comps = d.get("components") or {}
                    ev = post_json("/api/evaluate", {
                        "topology": d["topology"], "frequency_mhz": d["frequency_mhz"],
                        "load_r": payload["load_r"], "load_x": payload["load_x"],
                        "z0": payload["z0"], "L_uh": comps.get("L_uH", 0),
                        "C1_pF": comps.get("C1_pF", 0), "C2_pF": comps.get("C2_pF", 0),
                        "C3_pF": comps.get("C3_pF", 0),
                    })
                    COUNTER.add("evaluate")
                    if ev.get("vswr", 9) > 1.02:
                        COUNTER.error("evaluate-vswr", json.dumps(payload), None)
                elif result.get("error_code") not in (
                        "no_solution", "topology_mismatch", "invalid_load",
                        "invalid_frequency", "special_case", "invalid_component"):
                    COUNTER.error("design", result.get("message", ""), None)
            elif op == "evaluate":
                result = post_json("/api/evaluate", {
                    "topology": "l_right", "frequency_mhz": 2400,
                    "load_r": 20, "load_x": 5, "L_uh": 0.001939,
                    "C1_pF": 1.6244, "C2_pF": 6.8033, "C3_pF": 0,
                })
                COUNTER.add("evaluate")
                if abs(result.get("vswr", 9) - 1.0) > 1e-3:
                    COUNTER.error("evaluate-fixed", json.dumps(result)[:300], None)
            elif op == "docs":
                query = RNG.choice(TOKEN_POOL + ["a" * 700])
                result = get_json("/api/docs/search?q=" +
                                  urllib.parse.quote(query) + "&limit=20")
                COUNTER.add("docs")
                if "results" not in result:
                    COUNTER.error("docs", json.dumps(result)[:300], None)
            elif op == "library":
                if RNG.random() < 0.5:
                    result = get_json("/api/library/status")
                    COUNTER.add("library-status")
                else:
                    query = RNG.choice(TOKEN_POOL)
                    result = get_json("/api/library/search?q=" +
                                      urllib.parse.quote(query) + "&limit=10")
                    COUNTER.add("library-search")
                if not isinstance(result, dict):
                    COUNTER.error("library", "not a dict", None)
            elif op == "status":
                result = get_json("/api/status")
                COUNTER.add("status")
                if result.get("version") != "4.5.0" or "library" not in result:
                    COUNTER.error("status", json.dumps(result)[:300], None)
                get_json("/api/providers")
                COUNTER.add("providers")
            elif op == "bandwidth":
                result = post_json("/api/bandwidth", {
                    "topology": "l_right", "frequency_mhz": 2400,
                    "load_r": 20, "load_x": 5, "L_uh": 0.001939,
                    "C1_pF": 1.6244, "C2_pF": 6.8033,
                    "span": 0.6, "vswr_limit": 2.0,
                })
                COUNTER.add("bandwidth")
                if not result.get("points"):
                    COUNTER.error("bandwidth", json.dumps(result)[:300], None)
            elif op == "stress":
                result = post_json("/api/stress", {
                    "topology": "l_right", "frequency_mhz": 2400,
                    "load_r": 20, "load_x": 5, "L_uh": 0.001939,
                    "C1_pF": 1.6244, "C2_pF": 6.8033, "power_w": 10,
                    "sweep": False,
                })
                COUNTER.add("stress")
                if result.get("solves") != 1:
                    COUNTER.error("stress", json.dumps(result)[:300], None)
            elif op == "scan":
                result = post_json("/api/scan", {
                    "topology": RNG.choice(["l_right", "l_left", "t", "pi1", "pi2"]),
                    "frequency_mhz": 2400, "z0": 50, "L_uh": 0.002,
                    "steps": 8,
                    "c1_range_pf": [0.5, 10], "c2_range_pf": [0.5, 10],
                    "c3_range_pf": [0.2, 10],
                })
                COUNTER.add("scan")
                if not result.get("ok"):
                    COUNTER.error("scan", json.dumps(result)[:300], None)
            elif op == "upload":
                result = post_json("/api/upload-text", {
                    "text": ("soak upload " + "x" * RNG.randint(10, 5000)),
                    "name": f"soak_{index}_{int(time.time() * 1000)}.txt",
                })
                COUNTER.add("upload")
                if not result.get("ok"):
                    COUNTER.error("upload", json.dumps(result)[:300], None)
                else:
                    try:
                        Path(result["path"]).unlink(missing_ok=True)
                    except Exception:
                        pass
            else:
                try:
                    post_json("/api/design", {"topology": "l_right"})
                    COUNTER.error("invalid-input", "expected 400 but succeeded", None)
                except RuntimeError as exc:
                    COUNTER.add("invalid-400")
                    if "HTTP 40" not in str(exc):
                        COUNTER.error("invalid-input", str(exc), None)
        except RuntimeError as exc:
            COUNTER.error(op, str(exc))
        except Exception as exc:  # noqa: BLE001
            COUNTER.error(op, repr(exc))
        time.sleep(RNG.uniform(0.01, 0.06))


def scan_stream() -> None:
    payload = json.dumps({
        "topology": RNG.choice(["l_right", "t", "pi1", "pi2"]),
        "frequency_mhz": 2400, "z0": 50, "L_uh": 0.002,
        "points_budget": 600,
        "c1_range_pf": [0.5, 10], "c2_range_pf": [0.5, 10],
        "c3_range_pf": [0.2, 10],
    }).encode("utf-8")
    conn = _connect(API_PORT, 60)
    try:
        conn.request("POST", "/api/scan/stream", body=payload,
                     headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        text = response.read().decode("utf-8", "replace")
    finally:
        conn.close()
    if "event: meta" not in text or "event: done" not in text:
        COUNTER.error("scan-stream", text[:300], None)
    else:
        done = json.loads(text.split("event: done")[-1].split("data:", 1)[1].strip())
        expected = 1
        for value in done.get("grid_steps") or []:
            expected *= int(value)
        if done.get("evaluated_count") != expected:
            COUNTER.error("scan-stream-count", json.dumps(done)[:300], None)
        COUNTER.add("scan-stream")


def stream_worker() -> None:
    while not STOP.is_set():
        try:
            scan_stream()
        except Exception as exc:  # noqa: BLE001
            COUNTER.error("scan-stream", repr(exc))
        STOP.wait(20)


def chat_worker() -> None:
    prompts = [
        "只回答两个字：稳定。",
        "用工具在 2.4 GHz 把 20+j5 Ω 匹配到 50 Ω，给出元件值与 VSWR。",
    ]
    index = 0
    while not STOP.is_set():
        prompt = prompts[index % len(prompts)]
        index += 1
        started = time.time()
        payload = json.dumps({
            "messages": [{"role": "user", "content": prompt}],
            "model": "deepseek-flash",
            "context": {"view": "agent"},
        }, ensure_ascii=False).encode("utf-8")
        conn = _connect(API_PORT, 240)
        try:
            conn.request("POST", "/api/chat", body=payload,
                         headers={"Content-Type": "application/json",
                                  "Accept": "text/event-stream"})
            response = conn.getresponse()
            text = response.read().decode("utf-8", "replace")
            elapsed = time.time() - started
            if "event: done" not in text or "event: error" in text:
                COUNTER.error("chat", text[-500:], None)
            else:
                data = json.loads(text.split("event: done")[-1].split("data:", 1)[1].strip())
                if not data.get("content"):
                    COUNTER.error("chat-empty", json.dumps(data)[:300], None)
                COUNTER.add("chat")
                with COUNTER.lock:
                    COUNTER.samples.append({"chat_s": round(elapsed, 2),
                                            "tokens": data.get("usage", {}).get("total_tokens")})
        except Exception as exc:  # noqa: BLE001
            COUNTER.error("chat", repr(exc))
        finally:
            conn.close()
        STOP.wait(240)


def mcp_stdio_batch(index: int) -> None:
    design = {
        "topology": RNG.choice(["l_right", "l_left", "t", "pi1", "pi2"]),
        "frequency_mhz": RNG.choice([433, 915, 2400, 5800]),
        "load_r": round(RNG.uniform(5, 200), 2),
        "load_x": round(RNG.uniform(-80, 80), 2),
    }
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                    "clientInfo": {"name": "soak", "version": "1.0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]
    next_id = 3
    for _ in range(40):
        kind = RNG.choices(
            ["design", "scan", "evaluate", "stress", "docs", "library", "status", "ping"],
            weights=[30, 10, 20, 10, 10, 5, 10, 5], k=1)[0]
        if kind == "design":
            messages.append({"jsonrpc": "2.0", "id": next_id, "method": "tools/call",
                             "params": {"name": "design_matching_network",
                                        "arguments": dict(design)}})
        elif kind == "scan":
            messages.append({"jsonrpc": "2.0", "id": next_id, "method": "tools/call",
                             "params": {"name": "scan_matching_range",
                                        "arguments": {"topology": "l_right",
                                                      "frequency_mhz": 2400,
                                                      "L_uh": 0.001939, "steps": 8}}})
        elif kind == "evaluate":
            messages.append({"jsonrpc": "2.0", "id": next_id, "method": "tools/call",
                             "params": {"name": "evaluate_network",
                                        "arguments": {"topology": "l_right",
                                                      "frequency_mhz": 2400,
                                                      "load_r": 20, "load_x": 5,
                                                      "L_uh": 0.001939, "C1_pF": 1.6244,
                                                      "C2_pF": 6.8033}}})
        elif kind == "stress":
            messages.append({"jsonrpc": "2.0", "id": next_id, "method": "tools/call",
                             "params": {"name": "compute_voltage_stress",
                                        "arguments": {"topology": "l_right",
                                                      "frequency_mhz": 2400,
                                                      "load_r": 20, "load_x": 5,
                                                      "L_uh": 0.001939, "C1_pF": 1.6244,
                                                      "C2_pF": 6.8033, "power_w": 10}}})
        elif kind == "docs":
            messages.append({"jsonrpc": "2.0", "id": next_id, "method": "tools/call",
                             "params": {"name": "search_docs",
                                        "arguments": {"query": RNG.choice(TOKEN_POOL)}}})
        elif kind == "library":
            messages.append({"jsonrpc": "2.0", "id": next_id, "method": "tools/call",
                             "params": {"name": "get_library_status", "arguments": {}}})
        elif kind == "status":
            messages.append({"jsonrpc": "2.0", "id": next_id, "method": "tools/call",
                             "params": {"name": "get_system_status", "arguments": {}}})
        else:
            messages.append({"jsonrpc": "2.0", "id": next_id, "method": "ping", "params": {}})
        next_id += 1
    payload = "".join(json.dumps(m, ensure_ascii=False) + "\n" for m in messages)
    try:
        proc = subprocess.run(
            [sys.executable, str(MCP_SCRIPT)], input=payload, text=True,
            capture_output=True, timeout=120, cwd=str(ROOT),
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"},
            encoding="utf-8", errors="replace")
        responses = {}
        for line in proc.stdout.splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and "id" in obj:
                responses[obj["id"]] = obj
        missing = [i for i in range(1, next_id) if i not in responses]
        if missing:
            COUNTER.error("mcp-stdio-missing", f"batch {index} missing {missing[:10]} "
                                               f"rc={proc.returncode} {proc.stderr[-300:]}")
        for rid in range(3, next_id):
            obj = responses.get(rid, {})
            if "error" in obj:
                COUNTER.error("mcp-stdio-error", json.dumps(obj)[:300])
        COUNTER.add("mcp-stdio-batches")
        COUNTER.add("mcp-stdio-calls", next_id - 3)
    except Exception as exc:  # noqa: BLE001
        COUNTER.error("mcp-stdio", repr(exc))


class MCPHttpClient:
    def __init__(self) -> None:
        self.session = ""
        self.next_id = 1

    def post(self, message: Dict[str, Any], timeout: float = 60.0) -> Dict[str, Any]:
        body = json.dumps(message, ensure_ascii=False).encode("utf-8")
        conn = _connect(MCP_PORT, timeout)
        try:
            conn.request("POST", "/mcp", body=body, headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                **({"Mcp-Session-Id": self.session} if self.session else {}),
            })
            response = conn.getresponse()
            sid = response.headers.get("Mcp-Session-Id")
            if sid:
                self.session = sid
            raw = response.read()
            if response.status >= 400:
                raise RuntimeError(f"HTTP {response.status}: {raw[:300].decode('utf-8', 'replace')}")
            return json.loads(raw.decode("utf-8")) if raw else {}
        finally:
            conn.close()

    def call(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        rid = self.next_id
        self.next_id += 1
        return self.post({"jsonrpc": "2.0", "id": rid, "method": "tools/call",
                          "params": {"name": name, "arguments": args}})


def mcp_http_worker(index: int) -> None:
    client = MCPHttpClient()
    try:
        client.post({"jsonrpc": "2.0", "id": 0, "method": "initialize",
                     "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                "clientInfo": {"name": f"soak{index}", "version": "1"}}})
        COUNTER.add("mcp-http-init")
    except Exception as exc:  # noqa: BLE001
        COUNTER.error("mcp-http-init", repr(exc))
        return
    while not STOP.is_set():
        kind = RNG.choices(["design", "evaluate", "docs", "status", "ping"],
                           weights=[35, 25, 15, 15, 10], k=1)[0]
        try:
            if kind == "design":
                result = client.call("design_matching_network", random_design())
            elif kind == "evaluate":
                result = client.call("evaluate_network", {
                    "topology": "l_right", "frequency_mhz": 2400,
                    "load_r": 20, "load_x": 5, "L_uh": 0.001939,
                    "C1_pF": 1.6244, "C2_pF": 6.8033})
            elif kind == "docs":
                result = client.call("search_docs", {"query": RNG.choice(TOKEN_POOL)})
            elif kind == "status":
                result = client.call("get_system_status", {})
            else:
                result = client.post({"jsonrpc": "2.0", "id": 999999,
                                      "method": "ping", "params": {}})
            if "error" in result:
                COUNTER.error("mcp-http-tool", json.dumps(result)[:300])
            else:
                COUNTER.add(f"mcp-http-{kind}")
        except Exception as exc:  # noqa: BLE001
            COUNTER.error("mcp-http", repr(exc))
            client.session = ""
            try:
                client.post({"jsonrpc": "2.0", "id": 0, "method": "initialize",
                             "params": {"protocolVersion": "2025-06-18",
                                        "capabilities": {},
                                        "clientInfo": {"name": f"soak{index}", "version": "1"}}})
            except Exception:
                pass
        time.sleep(RNG.uniform(0.1, 0.4))


def memory_worker(pid: int) -> None:
    try:
        import psutil
        process = psutil.Process(pid)
    except Exception:
        return
    while not STOP.is_set():
        try:
            info = process.memory_info()
            with COUNTER.lock:
                COUNTER.samples.append({
                    "t": round(time.time() - START, 1),
                    "rss_mb": round(info.rss / 1024 / 1024, 1),
                    "handles": process.num_handles() if hasattr(process, "num_handles") else None,
                })
            COUNTER.add("memory-samples")
        except Exception as exc:  # noqa: BLE001
            COUNTER.error("memory", repr(exc))
        STOP.wait(30)


def report_worker() -> None:
    while not STOP.is_set():
        STOP.wait(60)
        write_report(partial=True)


def write_report(partial: bool = False) -> None:
    with COUNTER.lock:
        values = dict(COUNTER.values)
        errors = list(COUNTER.errors)
        warnings = list(COUNTER.warnings)
        samples = list(COUNTER.samples)
    memory = [s for s in samples if "rss_mb" in s]
    chats = [s for s in samples if "chat_s" in s]
    report = {
        "partial": partial,
        "elapsed_s": round(time.time() - START, 1),
        "values": values,
        "error_count": len(errors),
        "errors": errors,
        "warnings": warnings,
        "memory": {
            "samples": len(memory),
            "first_mb": memory[0]["rss_mb"] if memory else None,
            "last_mb": memory[-1]["rss_mb"] if memory else None,
            "max_mb": max((m["rss_mb"] for m in memory), default=None),
        },
        "chat": {
            "count": len(chats),
            "avg_s": round(statistics.mean(c["chat_s"] for c in chats), 2) if chats else None,
            "min_s": min((c["chat_s"] for c in chats), default=None),
            "max_s": max((c["chat_s"] for c in chats), default=None),
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("partial", "elapsed_s", "values",
                                             "error_count", "memory")},
                     ensure_ascii=False), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=float, default=90)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--pid", type=int, default=0)
    parser.add_argument("--no-chat", action="store_true")
    parser.add_argument("--no-mcp", action="store_true")
    args = parser.parse_args()
    global MCP_PORT
    MCP_PORT = _available_port(MCP_PORT)
    try:
        health = get_json("/api/health", timeout=10)
        if not health.get("ok"):
            raise RuntimeError(str(health))
    except Exception as exc:  # noqa: BLE001
        print(f"server not ready: {exc}", file=sys.stderr)
        return 2
    duration = max(1.0, args.minutes * 60)
    threads: List[threading.Thread] = []
    for i in range(args.workers):
        threads.append(threading.Thread(target=http_worker, args=(i,), daemon=True))
    threads.append(threading.Thread(target=stream_worker, daemon=True))
    if not args.no_chat:
        threads.append(threading.Thread(target=chat_worker, daemon=True))
    mcp_http_proc = None
    if not args.no_mcp:
        env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
        try:
            mcp_http_proc = subprocess.Popen(
                [sys.executable, str(MCP_SCRIPT), "--http", str(MCP_PORT)],
                cwd=str(ROOT), env=env, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            for _ in range(40):
                try:
                    conn = _connect(MCP_PORT, 2)
                    conn.request("GET", "/health")
                    if conn.getresponse().status == 200:
                        conn.close()
                        break
                    conn.close()
                except Exception:
                    time.sleep(0.25)
            for i in range(2):
                threads.append(threading.Thread(target=mcp_http_worker, args=(i,), daemon=True))
        except Exception as exc:  # noqa: BLE001
            COUNTER.error("mcp-http-start", repr(exc))

    def mcp_stdio_loop() -> None:
        index = 0
        while not STOP.is_set():
            index += 1
            mcp_stdio_batch(index)
            STOP.wait(45)

    if not args.no_mcp:
        threads.append(threading.Thread(target=mcp_stdio_loop, daemon=True))
    if args.pid:
        threads.append(threading.Thread(target=memory_worker, args=(args.pid,), daemon=True))
    threads.append(threading.Thread(target=report_worker, daemon=True))
    for thread in threads:
        thread.start()
    try:
        STOP.wait(duration)
    except KeyboardInterrupt:
        pass
    STOP.set()
    for thread in threads:
        thread.join(timeout=30)
    if mcp_http_proc is not None:
        try:
            mcp_http_proc.terminate()
            mcp_http_proc.wait(timeout=10)
        except Exception:
            mcp_http_proc.kill()
    write_report(partial=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
