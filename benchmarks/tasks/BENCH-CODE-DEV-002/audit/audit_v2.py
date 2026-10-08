#!/usr/bin/env python3
"""
BENCH-CODE-DEV-002 - Complementary Semantic Audit v2

Audits existing benchmark artifacts only:
- does NOT rerun any model
- does NOT modify candidate workspaces
- does NOT overwrite official evaluator results

It removes vacuous PASS cases where a generic 404 can satisfy a negative test
even though /api/admin/vehicles was never mounted.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
from typing import Any

DEFAULT_RUNS = [
    "DEV002-CODER-NEXT-Q3",
    "DEV002-CODER30-Q3",
    "DEV002-CODER30-Q4",
    "DEV002-QWEN36-35B-Q4-R2",
]

MAIN_DEPENDENCIES = {
    "vehicle_list_contains_created": ["vehicle_create", "vehicle_list"],
    "duplicate_matricula_rejected": ["vehicle_create"],
    "invalid_transporter_rejected": ["vehicle_create"],
    "vehicle_update_persisted": ["vehicle_update", "vehicle_get_by_id"],
    "vehicle_missing_get_404": ["vehicle_get_by_id"],
    "vehicle_missing_put_404": ["vehicle_update"],
    "vehicle_missing_delete_404": ["vehicle_delete"],
    "vehicle_deleted_is_404": ["vehicle_delete", "vehicle_get_by_id"],
}

REJECTION_TESTS = {
    "duplicate_matricula_rejected",
    "invalid_transporter_rejected",
}

EXPECTED_404_TESTS = {
    "vehicle_missing_get_404",
    "vehicle_missing_put_404",
    "vehicle_missing_delete_404",
    "vehicle_deleted_is_404",
}

def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)

def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        return " ".join(flatten_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(v) for v in value)
    return str(value)

def first_status(detail: Any):
    if isinstance(detail, list) and detail:
        x = detail[0]
        if isinstance(x, int):
            return x
        if isinstance(x, str) and x.isdigit():
            return int(x)
    if isinstance(detail, dict):
        for key in ("status", "status_code", "code"):
            x = detail.get(key)
            if isinstance(x, int):
                return x
            if isinstance(x, str) and x.isdigit():
                return int(x)
    return None

def is_generic_route_404(detail: Any) -> bool:
    status = first_status(detail)
    text = flatten_text(detail).lower()
    return status == 404 and (
        "ruta no encontrada" in text
        or "route not found" in text
        or "cannot " in text
    )

def test_map(evaluation):
    if not evaluation:
        return {}
    return {t.get("name"): t for t in evaluation.get("tests", []) if t.get("name")}

def audit_main(evaluation):
    if not evaluation:
        return [], {
            "tests_passed": None, "tests_total": None,
            "critical_passed": None, "critical_total": None,
        }

    tests = evaluation.get("tests", [])
    tmap = test_map(evaluation)
    audited = []

    for t in tests:
        name = t.get("name")
        official_pass = bool(t.get("pass"))
        critical = bool(t.get("critical"))
        detail = t.get("detail")
        audited_pass = official_pass
        reasons = []

        deps = MAIN_DEPENDENCIES.get(name, [])
        failed_deps = [d for d in deps if not bool(tmap.get(d, {}).get("pass"))]

        if official_pass and failed_deps:
            audited_pass = False
            reasons.append("vacuous_pass: failed_dependencies=" + ",".join(failed_deps))

        if name in REJECTION_TESTS and official_pass:
            status = first_status(detail)
            if status == 404 or is_generic_route_404(detail):
                audited_pass = False
                reasons.append("generic_404_is_not_validation_evidence")

        if name in EXPECTED_404_TESTS and official_pass:
            status = first_status(detail)
            if status != 404:
                audited_pass = False
                reasons.append(f"expected_404_observed={status!r}")

        audited.append({
            "name": name,
            "critical": critical,
            "official_pass": official_pass,
            "audited_pass": audited_pass,
            "detail": detail,
            "audit_reasons": reasons,
        })

    return audited, {
        "tests_passed": sum(t["audited_pass"] for t in audited),
        "tests_total": len(audited),
        "critical_passed": sum(t["critical"] and t["audited_pass"] for t in audited),
        "critical_total": sum(t["critical"] for t in audited),
    }

def audit_restart(restart_eval, main_map):
    if not restart_eval:
        return [], {
            "tests_passed": None, "tests_total": None,
            "critical_passed": None, "critical_total": None,
        }

    audited = []
    for t in restart_eval.get("tests", []):
        name = t.get("name")
        official_pass = bool(t.get("pass"))
        audited_pass = official_pass
        reasons = []

        if name == "vehicle_persists_after_restart" and official_pass:
            deps = ["vehicle_create", "vehicle_list"]
            failed_deps = [d for d in deps if not bool(main_map.get(d, {}).get("pass"))]
            if failed_deps:
                audited_pass = False
                reasons.append("vacuous_persistence_pass: failed_dependencies=" + ",".join(failed_deps))

        audited.append({
            "name": name,
            "critical": bool(t.get("critical")),
            "official_pass": official_pass,
            "audited_pass": audited_pass,
            "detail": t.get("detail"),
            "audit_reasons": reasons,
        })

    return audited, {
        "tests_passed": sum(t["audited_pass"] for t in audited),
        "tests_total": len(audited),
        "critical_passed": sum(t["critical"] and t["audited_pass"] for t in audited),
        "critical_total": sum(t["critical"] for t in audited),
    }

def score(a, b):
    return "" if a is None or b is None else f"{a}/{b}"

def classify(harness_error, main_summary):
    if harness_error and not main_summary.get("tests_total"):
        err = str(harness_error.get("error", "")).lower()
        status = str(harness_error.get("status", "")).lower()
        if "db:migrate" in err or "candidate_startup_failure" in status:
            return "FAIL_STARTUP"
        return "NO_EVALUATION"
    if main_summary.get("tests_total") is None:
        return "NO_EVALUATION"
    if main_summary["tests_passed"] == main_summary["tests_total"]:
        return "PASS_AUDITED_MAIN"
    return "FAIL"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--runs", nargs="*", default=DEFAULT_RUNS)
    ap.add_argument("--out", default="audit-v2")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    reports = []

    for run_id in args.runs:
        rd = root / "runs" / run_id
        result = load_json(rd / "result.json") or {}
        ev = load_json(rd / "evaluation" / "evaluation.json")
        e2e = load_json(rd / "evaluation" / "e2e.json") or {}
        herr = load_json(rd / "evaluation" / "harness-error.json")

        restart = result.get("functional", {}).get("restart") or None
        amain_tests, amain = audit_main(ev)
        amap = test_map(ev)
        arestart_tests, arestart = audit_restart(restart, amap)

        omain = result.get("functional", {}).get("main") or {}
        orestart = result.get("functional", {}).get("restart") or {}
        agent = result.get("agent", {}) or {}
        metrics = (result.get("inference", {}) or {}).get("llama_metric_deltas", {}) or {}

        report = {
            "benchmark": "BENCH-CODE-DEV-002",
            "audit": "semantic-audit-v2",
            "run_id": run_id,
            "model": result.get("model"),
            "classification": classify(herr, amain),
            "official": {
                "main": {k: omain.get(k) for k in (
                    "tests_passed","tests_total","critical_passed","critical_total")},
                "restart": {k: orestart.get(k) for k in (
                    "tests_passed","tests_total","critical_passed","critical_total")},
                "e2e": {"passed": e2e.get("passed"), "total": e2e.get("total")},
            },
            "audited": {
                "main": amain,
                "restart": arestart,
                "tests": amain_tests,
                "restart_tests": arestart_tests,
            },
            "agent": {
                "wall_seconds": agent.get("wall_seconds"),
                "exit_code": agent.get("exit_code"),
                "files_modified": agent.get("files_modified"),
                "lines_added": agent.get("lines_added"),
                "lines_deleted": agent.get("lines_deleted"),
            },
            "inference": {
                "prompt_tokens_total": metrics.get("llamacpp:prompt_tokens_total"),
                "tokens_predicted_total": metrics.get("llamacpp:tokens_predicted_total"),
                "prompt_tokens_seconds": metrics.get("llamacpp:prompt_tokens_seconds"),
                "predicted_tokens_seconds": metrics.get("llamacpp:predicted_tokens_seconds"),
                "n_tokens_max": metrics.get("llamacpp:n_tokens_max"),
            },
            "harness_error": herr,
            "notes": [
                "Official results preserved; not overwritten.",
                "Vacuous PASS cases caused by generic 404 are removed.",
                "No model or candidate application is rerun.",
            ],
        }
        dump_json(out / f"{run_id}.audit.json", report)
        reports.append(report)

        rows.append({
            "run_id": run_id,
            "model": report["model"] or "",
            "classification": report["classification"],
            "official_main": score(omain.get("tests_passed"), omain.get("tests_total")),
            "audited_main": score(amain.get("tests_passed"), amain.get("tests_total")),
            "official_critical": score(omain.get("critical_passed"), omain.get("critical_total")),
            "audited_critical": score(amain.get("critical_passed"), amain.get("critical_total")),
            "restart": score(orestart.get("tests_passed"), orestart.get("tests_total")),
            "e2e": score(e2e.get("passed"), e2e.get("total")),
            "wall_seconds": agent.get("wall_seconds") or "",
            "prompt_tokens": metrics.get("llamacpp:prompt_tokens_total") or "",
            "output_tokens": metrics.get("llamacpp:tokens_predicted_total") or "",
            "prompt_tok_s": metrics.get("llamacpp:prompt_tokens_seconds") or "",
            "generation_tok_s": metrics.get("llamacpp:predicted_tokens_seconds") or "",
        })

    fields = [
        "run_id","model","classification",
        "official_main","audited_main","official_critical","audited_critical",
        "restart","e2e","wall_seconds","prompt_tokens","output_tokens",
        "prompt_tok_s","generation_tok_s"
    ]
    with (out / "summary.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    dump_json(out / "summary.json", {
        "benchmark": "BENCH-CODE-DEV-002",
        "audit": "semantic-audit-v2",
        "runs": reports,
    })

    script = Path(__file__).resolve()
    sha = hashlib.sha256(script.read_bytes()).hexdigest()
    (out / "audit-script.sha256.txt").write_text(
        f"{sha}  {script.name}\n", encoding="utf-8"
    )

    print()
    print("BENCH-CODE-DEV-002 - Semantic Audit v2")
    print("=" * 92)
    print(f"{'RUN':32} {'OFFICIAL':>10} {'AUDITED':>10} {'CRIT.OFF':>10} {'CRIT.AUD':>10} {'CLASS':>14}")
    for r in rows:
        print(f"{r['run_id'][:32]:32} {r['official_main']:>10} {r['audited_main']:>10} "
              f"{r['official_critical']:>10} {r['audited_critical']:>10} {r['classification']:>14}")
    print("=" * 92)
    print("Output:", out)
    print("No candidate code or official benchmark artifact was modified.")

if __name__ == "__main__":
    main()
