#!/usr/bin/env python3
"""Isolated GGUF ROCm smoke tests (not the 900-question RAG experiment).

Launches one llama-server child per variant, verifies health and chat, samples GPU
VRAM, saves raw responses and SHA256, and terminates only its own server process.
Requires six registered, hash-verified GGUFs and a free local TCP port.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from register_experiment import BASE, MODEL_ORDER, MODEL_PREFIX, MODEL_SHA256, digest

QUESTION = "¿Cuál es la función de setup() y loop() en Arduino?"
FIELDS = [
    "variant", "status", "model_sha256", "model_bytes", "server_pid",
    "started_utc", "load_seconds", "baseline_vram_bytes", "loaded_vram_bytes",
    "peak_vram_bytes_observed", "vram_delta_bytes", "response_sha256",
    "prompt_tokens", "completion_tokens", "finish_reason",
    "prompt_ms", "predicted_ms", "tokens_per_second", "wall_seconds", "error",
]


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def free_port(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) != 0


def vram_bytes() -> int | None:
    tool = shutil.which("rocm-smi")
    if not tool:
        tool = "/opt/rocm/core-10.0/bin/rocm-smi"
    try:
        output = subprocess.run([tool, "--showmeminfo", "vram"], capture_output=True,
                                text=True, timeout=12, check=True).stdout
        match = re.search(r"VRAM Total Used Memory \(B\):\s*(\d+)", output)
        return int(match.group(1)) if match else None
    except (OSError, subprocess.SubprocessError):
        return None


def request(url: str, payload: dict | None = None, timeout: float = 5) -> dict:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"} if data is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def check_ready(url: str, proc: subprocess.Popen, deadline: float) -> float:
    start = time.monotonic()
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"llama-server exited during model load with status {proc.returncode}")
        try:
            health = request(url + "/health", timeout=3)
            if health.get("status") == "ok":
                return time.monotonic() - start
        except (OSError, ValueError, urllib.error.HTTPError):
            pass
        time.sleep(1.5)
    raise TimeoutError("llama-server health check deadline exceeded")


def run_variant(args: argparse.Namespace, variant: str, folder: Path) -> dict:
    model = args.base / "models" / "gguf" / f"{MODEL_PREFIX}{variant}.gguf"
    if not model.is_file():
        raise FileNotFoundError(model)
    observed_sha = digest(model)
    if observed_sha != MODEL_SHA256[variant]:
        raise ValueError(f"Model hash mismatch: {model.name} actual={observed_sha}")
    if not free_port("127.0.0.1", args.port):
        raise RuntimeError(f"Port 127.0.0.1:{args.port} already in use; refusing to start a server")
    folder.mkdir(parents=True, exist_ok=False)
    base = vram_bytes()
    row = {field: "" for field in FIELDS}
    row.update(variant=variant, status="error", model_sha256=observed_sha,
               model_bytes=model.stat().st_size, started_utc=utc(),
               baseline_vram_bytes=base if base is not None else "")
    env = os.environ.copy()
    rocm_lib = "/opt/rocm/core-10.0/lib"
    env["ROCM_PATH"] = "/opt/rocm/core-10.0"
    env["LD_LIBRARY_PATH"] = rocm_lib + (":" + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")
    cmd = [
        str(args.server), "--model", str(model), "--alias", "qwen3-4b-" + variant.lower(),
        "--host", "127.0.0.1", "--port", str(args.port),
        "--ctx-size", str(args.ctx_size), "--n-gpu-layers", "99",
        "--parallel", "1", "--flash-attn", "on", "--no-webui",
    ]
    (folder / "server_command.json").write_text(json.dumps(cmd, indent=2) + "\n", encoding="utf-8")
    proc = None
    try:
        with (folder / "server.log").open("wb") as logfile:
            proc = subprocess.Popen(cmd, stdout=logfile, stderr=subprocess.STDOUT,
                                    env=env, start_new_session=True)
            row["server_pid"] = proc.pid
            url = f"http://127.0.0.1:{args.port}"
            row["load_seconds"] = round(check_ready(url, proc, time.monotonic() + args.load_timeout), 3)
            loaded = vram_bytes()
            row["loaded_vram_bytes"] = loaded if loaded is not None else ""
            if base is not None and loaded is not None:
                row["vram_delta_bytes"] = loaded - base
            payload = {
                "model": "qwen3-4b-" + variant.lower(),
                "messages": [
                    {"role": "system", "content": "Responde en español, con precisión y de manera concisa."},
                    {"role": "user", "content": QUESTION},
                ],
                "temperature": 0,
                "max_tokens": 200,
                "stream": False,
            }
            (folder / "request.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            start = time.monotonic()
            response = request(url + "/v1/chat/completions", payload, timeout=args.infer_timeout)
            row["wall_seconds"] = round(time.monotonic() - start, 3)
            raw = (json.dumps(response, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
            (folder / "response.json").write_bytes(raw)
            row["response_sha256"] = hashlib.sha256(raw).hexdigest()
            peak = vram_bytes()
            vals = [v for v in (loaded, peak) if v is not None]
            row["peak_vram_bytes_observed"] = max(vals) if vals else ""
            usage = response.get("usage") or {}
            timings = response.get("timings") or {}
            row["prompt_tokens"] = usage.get("prompt_tokens", "")
            row["completion_tokens"] = usage.get("completion_tokens", "")
            row["finish_reason"] = ((response.get("choices") or [{}])[0]).get("finish_reason", "")
            row["prompt_ms"] = timings.get("prompt_ms", "")
            row["predicted_ms"] = timings.get("predicted_ms", "")
            row["tokens_per_second"] = timings.get("predicted_per_second", "")
            message = ((response.get("choices") or [{}])[0]).get("message") or {}
            if not isinstance(message.get("content"), str) or not message["content"].strip():
                raise ValueError("Empty or missing assistant content")
            row["status"] = "ok"
    except Exception as exc:
        row["error"] = type(exc).__name__ + ": " + str(exc)
    finally:
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=10)
        (folder / "result.json").write_text(
            json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", type=Path, default=BASE)
    p.add_argument("--server", type=Path, default=Path.home() / "llama.cpp/build-rocm/bin/llama-server")
    p.add_argument("--port", type=int, default=18182)
    p.add_argument("--ctx-size", type=int, default=8192)
    p.add_argument("--load-timeout", type=float, default=180)
    p.add_argument("--infer-timeout", type=float, default=120)
    p.add_argument("--variants", nargs="+", choices=MODEL_ORDER, default=list(MODEL_ORDER))
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    args.base = args.base.resolve()
    args.server = args.server.expanduser().resolve()
    if not args.server.is_file():
        p.error("llama-server executable not found: " + str(args.server))
    if len(args.variants) != len(set(args.variants)):
        p.error("Duplicate variants are not allowed")
    out = args.out or args.base / "runs" / ("SMOKE-QWEN-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    out = out.resolve()
    if out.exists():
        p.error("Output path already exists: " + str(out))
    out.mkdir(parents=True)
    rows = []
    for variant in args.variants:
        print("Testing", variant, flush=True)
        try:
            row = run_variant(args, variant, out / variant)
        except Exception as exc:
            row = {field: "" for field in FIELDS}
            row.update(variant=variant, status="error", error=type(exc).__name__ + ": " + str(exc))
        rows.append(row)
        print(variant, row["status"], row["error"], flush=True)
    with (out / "smoke_results.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "benchmark": "BENCH-QUANT-RAG-001", "phase": "smoke-not-rag",
        "created_utc": utc(), "variants": args.variants,
        "gguf_sha256": {r["variant"]: r["model_sha256"] for r in rows},
        "csv_sha256": digest(out / "smoke_results.csv"),
        "parameters": {"ctx_size": args.ctx_size, "port": args.port,
                       "temperature": 0, "max_tokens": 200},
        "successes": sum(r["status"] == "ok" for r in rows),
        "failures": sum(r["status"] != "ok" for r in rows),
        "notes": "VRAM values are total GPU snapshots (not per-process, nor sampled continuous peak).",
    }
    (out / "smoke_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out), "successes": manifest["successes"],
                      "failures": manifest["failures"]}, indent=2), flush=True)
    return 0 if manifest["failures"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
