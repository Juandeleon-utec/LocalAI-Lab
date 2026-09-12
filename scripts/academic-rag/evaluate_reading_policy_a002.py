#!/usr/bin/env python3
"""Evaluate deterministic reading policy A002 from an existing A001 run.

A002 does not call an LLM. It reuses the relevance classes already predicted in
A001 and maps them deterministically to reading actions:

3 -> READ_FULL
2 -> READ_SECTIONS
1 -> REFERENCE_ONLY
0 -> DISCARD

The script compares the derived reading decisions against the frozen ground
truth and reports workload reduction and relevant-paper retention.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_GT = Path(
    "/srv/data/benchmarks/academic-rag/ground-truth/academic-screening-v0.1/ground-truth-v0.1.csv"
)
DEFAULT_RUNS_ROOT = Path("/srv/data/benchmarks/academic-rag/runs")

POLICY = {
    3: "READ_FULL",
    2: "READ_SECTIONS",
    1: "REFERENCE_ONLY",
    0: "DISCARD",
}
ACTIVE_READING = {"READ_FULL", "READ_SECTIONS"}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"CSV is empty: {path}")
    return rows


def index_by_id(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        pid = row.get("paper_id", "").strip()
        if not pid:
            raise SystemExit(f"{label}: row without paper_id")
        if pid in out:
            raise SystemExit(f"{label}: duplicate paper_id {pid}")
        out[pid] = row
    return out


def safe_div(a: int, b: int) -> float:
    return a / b if b else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate deterministic A002 reading policy from an A001 run.")
    parser.add_argument("--run", type=Path, required=True, help="A001 run directory containing predictions.csv")
    parser.add_argument("--ground-truth", type=Path, default=DEFAULT_GT)
    parser.add_argument("--runs-root", type=Path, default=DEFAULT_RUNS_ROOT)
    parser.add_argument("--run-id", default="A002")
    args = parser.parse_args()

    predictions_path = args.run / "predictions.csv"
    if not predictions_path.exists():
        raise SystemExit(f"Missing predictions.csv: {predictions_path}")

    pred_rows = load_csv(predictions_path)
    gt_rows = load_csv(args.ground_truth)
    pred = index_by_id(pred_rows, "predictions")
    gt = index_by_id(gt_rows, "ground truth")

    if set(pred) != set(gt):
        missing_pred = sorted(set(gt) - set(pred))
        missing_gt = sorted(set(pred) - set(gt))
        raise SystemExit(f"paper_id mismatch; missing predictions={missing_pred}, missing ground truth={missing_gt}")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.runs_root / f"{args.run_id}-{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=False)

    comparison: list[dict[str, object]] = []
    active = 0
    relevant_total = 0
    relevant_retained = 0
    class3_total = 0
    class3_full = 0
    exact_decision = 0

    for pid in sorted(pred):
        prow = pred[pid]
        grow = gt[pid]
        if prow.get("status") != "OK":
            raise SystemExit(f"Prediction for {pid} is not OK: {prow.get('status')}")
        try:
            pclass = int(prow["relevance_class"])
            gclass = int(grow["relevance_class"])
        except (KeyError, ValueError) as exc:
            raise SystemExit(f"Invalid relevance class for {pid}") from exc
        if pclass not in POLICY or gclass not in POLICY:
            raise SystemExit(f"Relevance class outside 0..3 for {pid}")

        derived = POLICY[pclass]
        gt_decision = grow.get("reading_decision", "").strip()
        is_active = derived in ACTIVE_READING
        is_relevant = gclass >= 2

        active += int(is_active)
        relevant_total += int(is_relevant)
        relevant_retained += int(is_relevant and is_active)
        class3_total += int(gclass == 3)
        class3_full += int(gclass == 3 and derived == "READ_FULL")
        exact_decision += int(derived == gt_decision)

        comparison.append(
            {
                "paper_id": pid,
                "title": prow.get("title", ""),
                "gt_relevance_class": gclass,
                "pred_relevance_class": pclass,
                "gt_reading_decision": gt_decision,
                "a001_model_reading_decision": prow.get("reading_decision", ""),
                "a002_derived_reading_decision": derived,
                "active_reading": int(is_active),
                "gt_relevant": int(is_relevant),
                "relevant_retained": int(is_relevant and is_active),
            }
        )

    n = len(comparison)
    reduction = 1.0 - safe_div(active, n)
    retention = safe_div(relevant_retained, relevant_total)
    class3_full_recall = safe_div(class3_full, class3_total)
    decision_accuracy = safe_div(exact_decision, n)

    comparison_path = out_dir / "policy-comparison.csv"
    with comparison_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(comparison[0].keys()))
        writer.writeheader()
        writer.writerows(comparison)

    evaluation = {
        "benchmark": "Academic Screening deterministic reading policy",
        "run_id": args.run_id,
        "timestamp_utc": timestamp,
        "source_a001_run": str(args.run),
        "ground_truth": str(args.ground_truth),
        "policy": {str(k): v for k, v in sorted(POLICY.items(), reverse=True)},
        "papers": n,
        "active_reading_papers": active,
        "potential_active_reading_reduction": round(reduction, 6),
        "gt_relevant_papers": relevant_total,
        "gt_relevant_retained": relevant_retained,
        "relevant_retention": round(retention, 6),
        "gt_class3_papers": class3_total,
        "gt_class3_assigned_read_full": class3_full,
        "class3_read_full_recall": round(class3_full_recall, 6),
        "exact_reading_decision_accuracy": round(decision_accuracy, 6),
        "note": "A002 reuses A001 relevance predictions; no LLM inference is performed.",
    }
    evaluation_path = out_dir / "evaluation.json"
    evaluation_path.write_text(json.dumps(evaluation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = f"""# Academic Screening A002 — Deterministic Reading Policy\n\n"
    report += f"Source A001 run: `{args.run}`\n\n"
    report += "Policy:\n\n- 3 -> READ_FULL\n- 2 -> READ_SECTIONS\n- 1 -> REFERENCE_ONLY\n- 0 -> DISCARD\n\n"
    report += f"- Papers: {n}\n"
    report += f"- Active-reading papers: {active}\n"
    report += f"- Potential active-reading reduction: {reduction:.3f}\n"
    report += f"- Relevant-paper retention: {retention:.3f}\n"
    report += f"- Class-3 READ_FULL recall: {class3_full_recall:.3f}\n"
    report += f"- Exact reading-decision agreement with ground truth: {decision_accuracy:.3f}\n"
    report += "\nA002 isolates reading-policy behavior from LLM classification quality. It does not rerun inference.\n"
    (out_dir / "report.md").write_text(report, encoding="utf-8")

    print("Academic Screening A002 complete")
    print(f"Source A001: {args.run}")
    print(f"Papers: {n}")
    print(f"Active-reading papers: {active}")
    print(f"Potential active-reading reduction: {reduction:.3f}")
    print(f"Relevant retention: {retention:.3f}")
    print(f"Class-3 READ_FULL recall: {class3_full_recall:.3f}")
    print(f"Reading-decision agreement with GT: {decision_accuracy:.3f}")
    print(f"Run: {out_dir}")
    print(f"Evaluation: {evaluation_path}")
    print(f"Comparison: {comparison_path}")


if __name__ == "__main__":
    main()
