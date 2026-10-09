#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.cookiejar
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
from pathlib import Path
from typing import Any


def run_logged(cmd: list[str], cwd: Path | None, stdout_path: Path, stderr_path: Path, env: dict[str, str] | None = None) -> int:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("w", encoding="utf-8", errors="replace") as out, stderr_path.open("w", encoding="utf-8", errors="replace") as err:
        p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, stdout=out, stderr=err, env=env, text=True)
    return p.returncode


def cmd_name(base: str) -> str:
    if os.name == "nt":
        if base.lower() == "npm":
            return "npm.cmd"
        if base.lower() == "node":
            return "node.exe"
        if base.lower() == "docker":
            return "docker.exe"
    return base


def tcp_ready(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def wait_tcp(port: int, proc: subprocess.Popen[Any] | None, seconds: float = 30.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if tcp_ready("127.0.0.1", port):
            return True
        if proc is not None and proc.poll() is not None:
            return False
        time.sleep(0.4)
    return False


def stop_process_tree(proc: subprocess.Popen[Any] | None) -> None:
    if not proc or proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(["taskkill.exe", "/PID", str(proc.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    except Exception:
        pass


def read_text_files(root: Path, suffixes: tuple[str, ...]) -> str:
    parts: list[str] = []
    if not root.exists():
        return ""
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in suffixes and "node_modules" not in p.parts:
            try:
                parts.append(p.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    return "\n".join(parts)


def static_checks(workspace: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    frontend = read_text_files(workspace / "frontend", (".html", ".js", ".jsx", ".ts", ".tsx", ".css"))
    backend_routes = read_text_files(workspace / "backend" / "src" / "routes", (".js", ".ts"))
    backend_models = read_text_files(workspace / "backend" / "src" / "models", (".js", ".ts"))

    required_testids = [
        "vehicles-section", "vehicle-new", "vehicle-form", "vehicle-transporter",
        "vehicle-matricula", "vehicle-marca", "vehicle-modelo", "vehicle-save",
        "vehicle-cancel", "vehicle-row", "vehicle-edit", "vehicle-delete",
    ]
    missing = [x for x in required_testids if f'data-testid="{x}"' not in frontend and f"data-testid='{x}'" not in frontend]
    checks.append({
        "id": "STATIC_FRONTEND_TESTIDS",
        "pass": not missing,
        "critical": True,
        "detail": {"missing": missing, "required": required_testids},
    })

    # These are source-level guards only. Dynamic HTTP checks below are authoritative for reachability.
    patterns = {
        "STATIC_ROUTE_POST": r"\.post\s*\(\s*['\"][^'\"]*vehicles",
        "STATIC_ROUTE_LIST": r"\.get\s*\(\s*['\"][^'\"]*vehicles['\"]",
        "STATIC_ROUTE_GET_ID": r"\.get\s*\(\s*['\"][^'\"]*vehicles/:id",
        "STATIC_ROUTE_PUT_ID": r"\.put\s*\(\s*['\"][^'\"]*vehicles/:id",
        "STATIC_ROUTE_DELETE_ID": r"\.delete\s*\(\s*['\"][^'\"]*vehicles/:id",
    }
    for cid, pat in patterns.items():
        ok = re.search(pat, backend_routes, re.IGNORECASE | re.MULTILINE) is not None
        checks.append({"id": cid, "pass": ok, "critical": True, "detail": {"pattern": pat}})

    field_missing = [x for x in ("transportista_id", "matricula", "marca", "modelo", "activo") if x.lower() not in backend_models.lower()]
    checks.append({
        "id": "STATIC_MODEL_FIELDS",
        "pass": not field_missing,
        "critical": True,
        "detail": {"missing": field_missing},
    })
    return checks


class HttpClient:
    def __init__(self, base: str):
        self.base = base.rstrip("/")
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def req(self, method: str, path: str, data: dict[str, Any] | None = None, authenticated: bool = True) -> tuple[int, Any]:
        opener = self.opener if authenticated else urllib.request.build_opener()
        body = None if data is None else json.dumps(data).encode("utf-8")
        req = urllib.request.Request(self.base + path, data=body, method=method)
        if body is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with opener.open(req, timeout=8) as r:
                raw = r.read().decode("utf-8", errors="replace")
                try:
                    obj: Any = json.loads(raw)
                except Exception:
                    obj = {"_raw": raw}
                return r.status, obj
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            try:
                obj = json.loads(raw)
            except Exception:
                obj = {"_raw": raw}
            return e.code, obj


def add_check(checks: list[dict[str, Any]], cid: str, critical: bool, ok: bool, detail: Any) -> None:
    checks.append({"id": cid, "pass": bool(ok), "critical": critical, "detail": detail})


def dynamic_checks(base: str) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    c = HttpClient(base)

    s, o = c.req("GET", "/api/admin/vehicles", authenticated=False)
    add_check(checks, "HTTP_AUTH_REQUIRED", True, s in (401, 403), [s, o])

    s, o = c.req("POST", "/api/admin/login", {"usuario": "admin", "contrasena": "AdminBench2026!"})
    add_check(checks, "HTTP_ADMIN_LOGIN", True, s == 200, [s, o])
    if s != 200:
        return checks

    transporter = {
        "empresa": "AGENT001 Transportes",
        "nombre_chofer": "Chofer AGENT001",
        "documento": "AGENT001DOC",
        "matricula": "TRAG001",
        "activo": True,
    }
    s, o = c.req("POST", "/api/admin/transporters", transporter)
    add_check(checks, "REGRESSION_CREATE_TRANSPORTER", True, s in (200, 201), [s, o])

    s, o = c.req("GET", "/api/admin/transporters")
    lst = o.get("transportistas", []) if isinstance(o, dict) else []
    tid = next((x.get("id") for x in lst if x.get("empresa") == "AGENT001 Transportes"), None)
    add_check(checks, "REGRESSION_LIST_TRANSPORTERS", True, s == 200 and tid is not None, [s, o, tid])

    vehicle = {"transportista_id": tid, "matricula": "AG001A", "marca": "MarcaA", "modelo": "ModeloA", "activo": True}
    s1, o1 = c.req("POST", "/api/admin/vehicles", vehicle)
    vid = None
    if isinstance(o1, dict):
        candidate = o1.get("vehiculo") or o1.get("vehicle") or o1
        if isinstance(candidate, dict):
            vid = candidate.get("id")
    add_check(checks, "HTTP_CREATE_VEHICLE", True, s1 in (200, 201) and vid is not None, [s1, o1, vid])

    s2, o2 = c.req("GET", "/api/admin/vehicles")
    add_check(checks, "HTTP_LIST_VEHICLES", True, s2 == 200, [s2, o2])
    add_check(checks, "HTTP_LIST_CONTAINS_CREATED", True, s2 == 200 and "AG001A" in json.dumps(o2), [s2, o2])

    s3, o3 = c.req("GET", f"/api/admin/vehicles/{vid or 999999}")
    add_check(checks, "HTTP_GET_VEHICLE_BY_ID", True, s3 == 200 and "AG001A" in json.dumps(o3), [s3, o3])

    sd, od = c.req("POST", "/api/admin/vehicles", vehicle)
    add_check(checks, "HTTP_DUPLICATE_MATRICULA_4XX", True, 400 <= sd < 500, [sd, od])

    bad = dict(vehicle)
    bad["matricula"] = "AG001BAD"
    bad["transportista_id"] = 99999999
    sf, of = c.req("POST", "/api/admin/vehicles", bad)
    add_check(checks, "HTTP_INVALID_TRANSPORTER_4XX", True, 400 <= sf < 500, [sf, of])

    upd = {"transportista_id": tid, "matricula": "AG001A", "marca": "MarcaB", "modelo": "ModeloB", "activo": False}
    su, ou = c.req("PUT", f"/api/admin/vehicles/{vid or 999999}", upd)
    add_check(checks, "HTTP_UPDATE_VEHICLE", True, su == 200, [su, ou])
    sg, og = c.req("GET", f"/api/admin/vehicles/{vid or 999999}")
    add_check(checks, "HTTP_UPDATE_PERSISTED", True, sg == 200 and "MarcaB" in json.dumps(og) and "ModeloB" in json.dumps(og), [sg, og])

    for method, cid in (("GET", "HTTP_MISSING_GET_404"), ("PUT", "HTTP_MISSING_PUT_404"), ("DELETE", "HTTP_MISSING_DELETE_404")):
        payload = upd if method == "PUT" else None
        sm, om = c.req(method, "/api/admin/vehicles/99999999", payload)
        add_check(checks, cid, False, sm == 404, [sm, om])

    v2 = dict(vehicle)
    v2["matricula"] = "AG001DEL"
    sc, oc = c.req("POST", "/api/admin/vehicles", v2)
    v2id = None
    if isinstance(oc, dict):
        candidate = oc.get("vehiculo") or oc.get("vehicle") or oc
        if isinstance(candidate, dict):
            v2id = candidate.get("id")
    sx, ox = c.req("DELETE", f"/api/admin/vehicles/{v2id or 999999}")
    add_check(checks, "HTTP_DELETE_VEHICLE", True, sx == 200, [sx, ox])
    sy, oy = c.req("GET", f"/api/admin/vehicles/{v2id or 999999}")
    add_check(checks, "HTTP_DELETED_IS_404", True, sy == 404, [sy, oy])

    sr, orr = c.req("GET", "/api/admin/users")
    add_check(checks, "REGRESSION_USERS_LIST", True, sr == 200, [sr, orr])
    return checks


def write_report(out: Path, status: str, stage: str, checks: list[dict[str, Any]], extra: dict[str, Any] | None = None) -> None:
    critical = [x for x in checks if x.get("critical")]
    report: dict[str, Any] = {
        "verifier": "BENCH-AGENT-001-public-verifier-v1",
        "status": status,
        "stage": stage,
        "checks_passed": sum(bool(x.get("pass")) for x in checks),
        "checks_total": len(checks),
        "critical_passed": sum(bool(x.get("pass")) for x in critical),
        "critical_total": len(critical),
        "failures": [x for x in checks if not x.get("pass")],
        "checks": checks,
    }
    if extra:
        report.update(extra)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--logs", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--mysql-port", type=int, default=3310)
    ap.add_argument("--backend-port", type=int, default=3013)
    args = ap.parse_args()

    workspace = Path(args.workspace).resolve()
    backend = workspace / "backend"
    out = Path(args.out).resolve()
    logs = Path(args.logs).resolve()
    logs.mkdir(parents=True, exist_ok=True)
    checks = static_checks(workspace)
    container = "agentv-" + re.sub(r"[^a-z0-9-]", "-", args.run_id.lower())[:45]
    docker = cmd_name("docker")
    npm = cmd_name("npm")
    node = cmd_name("node")
    backend_proc: subprocess.Popen[Any] | None = None

    def finish(status: str, stage: str, extra: dict[str, Any] | None = None, rc: int = 1) -> int:
        write_report(out, status, stage, checks, extra)
        return rc

    try:
        subprocess.run([docker, "rm", "-f", container], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p = subprocess.run([
            docker, "run", "--name", container,
            "-e", "MYSQL_ROOT_PASSWORD=benchroot",
            "-e", "MYSQL_DATABASE=tabacalera_agent001",
            "-e", "MYSQL_USER=bench_user",
            "-e", "MYSQL_PASSWORD=bench_pass",
            "-p", f"127.0.0.1:{args.mysql_port}:3306",
            "-d", "mysql:8.4",
        ], capture_output=True, text=True)
        if p.returncode != 0:
            return finish("INFRA_ERROR", "docker_start", {"stderr": p.stderr[-4000:]}, 3)

        healthy = False
        for _ in range(60):
            ping = subprocess.run([
                docker, "exec", "-e", "MYSQL_PWD=bench_pass", container,
                "mysqladmin", "ping", "-h", "127.0.0.1", "-u", "bench_user", "--silent",
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ping.returncode == 0:
                healthy = True
                break
            time.sleep(1)
        if not healthy:
            return finish("INFRA_ERROR", "mysql_health", rc=3)

        install_exit = run_logged([npm, "install", "--prefix", "backend", "--no-package-lock"], workspace, logs / "npm-install.stdout.log", logs / "npm-install.stderr.log")
        if install_exit != 0:
            return finish("CANDIDATE_FAIL", "npm_install", {"exit_code": install_exit}, 2)

        hash_out = logs / "bcrypt.stdout.txt"
        hash_exit = run_logged([node, "-e", "console.log(require('./backend/node_modules/bcryptjs').hashSync('AdminBench2026!',10))"], workspace, hash_out, logs / "bcrypt.stderr.txt")
        if hash_exit != 0:
            return finish("INFRA_ERROR", "bcrypt", {"exit_code": hash_exit}, 3)
        password_hash = hash_out.read_text(encoding="utf-8", errors="ignore").strip()
        if not password_hash:
            return finish("INFRA_ERROR", "bcrypt_empty", rc=3)

        env_text = f"""DB_HOST=127.0.0.1\nDB_PORT={args.mysql_port}\nDB_USER=bench_user\nDB_PASS=bench_pass\nDB_NAME=tabacalera_agent001\nJWT_SECRET=agent001_jwt_secret\nJWT_EXPIRES_IN=14d\nPORT={args.backend_port}\nNODE_ENV=test\nSESSION_SECRET=agent001_session_secret\nADMIN_USER=admin\nADMIN_PASSWORD_HASH={password_hash}\n"""
        (backend / ".env").write_text(env_text, encoding="ascii")

        migrate_exit = run_logged([npm, "--prefix", "backend", "run", "db:migrate"], workspace, logs / "db-migrate.stdout.log", logs / "db-migrate.stderr.log")
        if migrate_exit != 0:
            add_check(checks, "STARTUP_DB_MIGRATE", True, False, {"exit_code": migrate_exit})
            return finish("CANDIDATE_FAIL", "db_migrate", {"exit_code": migrate_exit}, 2)
        add_check(checks, "STARTUP_DB_MIGRATE", True, True, {"exit_code": migrate_exit})

        if tcp_ready("127.0.0.1", args.backend_port, 0.2):
            return finish("INFRA_ERROR", "backend_port_already_in_use", {"port": args.backend_port}, 3)

        backend_stdout = (logs / "backend.stdout.log").open("w", encoding="utf-8", errors="replace")
        backend_stderr = (logs / "backend.stderr.log").open("w", encoding="utf-8", errors="replace")
        backend_proc = subprocess.Popen([npm, "--prefix", "backend", "start"], cwd=str(workspace), stdout=backend_stdout, stderr=backend_stderr, text=True)
        if not wait_tcp(args.backend_port, backend_proc, 30):
            add_check(checks, "STARTUP_BACKEND_LISTEN", True, False, {"port": args.backend_port, "exit_code": backend_proc.poll()})
            backend_stdout.close(); backend_stderr.close()
            return finish("CANDIDATE_FAIL", "backend_start", rc=2)
        add_check(checks, "STARTUP_BACKEND_LISTEN", True, True, {"port": args.backend_port})

        checks.extend(dynamic_checks(f"http://127.0.0.1:{args.backend_port}"))
        backend_stdout.close(); backend_stderr.close()

        all_ok = all(bool(x.get("pass")) for x in checks if x.get("critical"))
        return finish("PASS" if all_ok else "FAIL", "complete", rc=0 if all_ok else 1)
    except FileNotFoundError as e:
        return finish("INFRA_ERROR", "missing_executable", {"error": str(e)}, 3)
    except Exception as e:
        return finish("INFRA_ERROR", "unexpected", {"error": repr(e)}, 3)
    finally:
        stop_process_tree(backend_proc)
        try:
            subprocess.run([docker, "rm", "-f", container], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
