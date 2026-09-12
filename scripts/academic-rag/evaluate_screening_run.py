#!/usr/bin/env python3
"""Evaluate an Academic Screening run against frozen ground truth.

The evaluator is dependency-free (Python standard library only) and is intended
for the LAILAB Academic Screening benchmark. It joins predictions and ground
truth by paper_id, validates the comparison set, computes multiclass and
screening-oriented metrics, and writes reproducible machine-readable and
human-readable reports into the evaluated run directory.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_GROUND_TRUTH = Path(
    "/srv/data/benchmarks/academic-rag/ground-truth/academic-screening-v0.1/ground-truth-v0.1.csv"
)
LABELS = {
    0: "NOT_RELEVANT",
    1: "TANGENTIAL",
    2: "RELEVANT",
    3: "HIGHLY_RELEVANT",
}
ACTIVE_READING = {"READ_FULL", "READ_SECTIONS"}


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"File does not exist: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"CSV is empty: {path}")
    return rows


def as_int(value: str, field: str, paper_id: str) -> int:
    try:
        parsed = int(str(value).strip())
    except ValueError as exc:
        raise SystemExit(f"Invalid {field} for {paper_id}: {value!r}") from exc
    if parsed not in LABELS:
        raise SystemExit(f"{field} must be 0..3 for {paper_id}: {parsed}")
    return parsed


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def round_metric(value: float) -> float:
    return round(float(value), 6)


def f1_score(precision: float, recall: float) -> float:
    return safe_div(2 * precision * recall, precision + recall)


def build_index(rows: list[dict[str, str]], source: str) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for row in rows:
        paper_id = row.get("paper_id", "").strip()
        if not paper_id:
            raise SystemExit(f"Missing paper_id in {source}")
        if paper_id in index:
            raise SystemExit(f"Duplicate paper_id {paper_id} in {source}")
        index[paper_id] = row
    return index


def confusion_matrix(pairs: list[tuple[int, int]]) -> list[list[int]]:
    matrix = [[0 for _ in range(4)] for _ in range(4)]
    for truth, pred in pairs:
        matrix[truth][pred] += 1
    return matrix


def per_class_metrics(matrix: list[list[int]]) -> dict[str, dict[str, float | int]]:
    total = sum(sum(row) for row in matrix)
    result: dict[str, dict[str, float | int]] = {}
    for cls in range(4):
        tp = matrix[cls][cls]
        fp = sum(matrix[r][cls] for r in range(4) if r != cls)
        fn = sum(matrix[cls][c] for c in range(4) if c != cls)
        tn = total - tp - fp - fn
        precision = safe_div(tp, tp + fp)
        recall = safe_div(tp, tp + fn)
        f1 = f1_score(precision, recall)
        result[str(cls)] = {
            "label": LABELS[cls],
            "support": sum(matrix[cls]),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "precision": round_metric(precision),
            "recall": round_metric(recall),
            "f1": round_metric(f1),
        }
    return result


def weighted_kappa(pairs: list[tuple[int, int]], quadratic: bool = True) -> float:
    """Cohen weighted kappa for ordinal classes 0..3."""
    n = len(pairs)
    if not n:
        return 0.0
    obs = confusion_matrix(pairs)
    truth_counts = [sum(obs[i]) for i in range(4)]
    pred_counts = [sum(obs[r][j] for r in range(4)) for j in range(4)]

    def weight(i: int, j: int) -> float:
        d = abs(i - j) / 3.0
        return d * d if quadratic else d

    observed = 0.0
    expected = 0.0
    for i in range(4):
        for j in range(4):
            w = weight(i, j)
            observed += w * obs[i][j] / n
            expected += w * (truth_counts[i] * pred_counts[j]) / (n * n)
    if expected == 0:
        return 1.0 if observed == 0 else 0.0
    return 1.0 - observed / expected


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_report(metrics: dict[str, Any]) -> str:
    binary = metrics["binary_screening"]
    reading = metrics["reading_workload"]
    lines = [
        "# Academic Screening Evaluation",
        "",
        f"- Papers evaluated: **{metrics['papers_evaluated']}**",
        f"- Exact 4-class accuracy: **{metrics['multiclass']['accuracy']:.3f}**",
        f"- Macro F1: **{metrics['multiclass']['macro_f1']:.3f}**",
        f"- Relevance-class MAE: **{metrics['ordinal']['mae']:.3f}**",
        f"- Quadratic weighted kappa: **{metrics['ordinal']['quadratic_weighted_kappa']:.3f}**",
        "",
        "## Screening metrics (relevant = class >= 2)",
        "",
        f"- Recall / relevant-paper retention: **{binary['recall']:.3f}**",
        f"- Precision: **{binary['precision']:.3f}**",
        f"- F1: **{binary['f1']:.3f}**",
        f"- False-negative rate: **{binary['false_negative_rate']:.3f}**",
        f"- Highly relevant (class 3) recall: **{binary['class3_recall']:.3f}**",
        "",
        "## Reading workload",
        "",
        "Active reading is defined as READ_FULL or READ_SECTIONS.",
        "",
        f"- Ground-truth active-reading papers: **{reading['ground_truth_active_reading']}**",
        f"- Model active-reading papers: **{reading['predicted_active_reading']}**",
        f"- Model active-reading fraction: **{reading['predicted_active_reading_fraction']:.3f}**",
        f"- Potential active-reading reduction: **{reading['potential_active_reading_reduction']:.3f}**",
        f"- Relevant papers retained among active-reading recommendations: **{reading['relevant_retained_by_active_reading']}/{reading['ground_truth_relevant']}** ({reading['relevant_retention_by_active_reading']:.3f})",
        "",
        "## Ground-truth caveat",
        "",
        "Interpret metrics in light of the provenance of the frozen ground truth. If labels were produced with AI assistance and human supervision, report that explicitly rather than describing them as purely human labels.",
        "",
        "## Confusion matrix",
        "",
        "Rows are ground truth; columns are predictions.",
        "",
        "| GT \\ Pred | 0 | 1 | 2 | 3 |",
        "|---|---:|---:|---:|---:|",
    ]
    matrix = metrics["multiclass"]["confusion_matrix"]
    for i, row in enumerate(matrix):
        lines.append(f"| {i} ({LABELS[i]}) | {row[0]} | {row[1]} | {row[2]} | {row[3]} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Academic Screening predictions against ground truth.")
    parser.add_argument("--run", type=Path, required=True, help="Run directory containing predictions.csv and manifest.json")
    parser.add_argument("--ground-truth", type=Path, default=DEFAULT_GROUND_TRUTH)
    parser.add_argument("--relevant-threshold", type=int, default=2, choices=(1, 2, 3))
    args = parser.parse_args()

    run_dir = args.run.resolve()
    predictions_path = run_dir / "predictions.csv"
    manifest_path = run_dir / "manifest.json"
    predictions = load_csv(predictions_path)
    ground_truth = load_csv(args.ground_truth)

    pred_idx = build_index(predictions, "predictions")
    gt_idx = build_index(ground_truth, "ground truth")

    gt_ids = set(gt_idx)
    pred_ids = set(pred_idx)
    missing_predictions = sorted(gt_ids - pred_ids)
    extra_predictions = sorted(pred_ids - gt_ids)
    if missing_predictions or extra_predictions:
        raise SystemExit(
            "paper_id sets differ: "
            f"missing_predictions={missing_predictions}, extra_predictions={extra_predictions}"
        )

    comparison_rows: list[dict[str, Any]] = []
    pairs: list[tuple[int, int]] = []
    valid_ids: list[str] = []

    for paper_id in sorted(gt_ids):
        gt = gt_idx[paper_id]
        pred = pred_idx[paper_id]
        status = pred.get("status", "").strip()
        if status != "OK":
            raise SystemExit(f"Prediction {paper_id} has non-OK status: {status!r}")

        truth = as_int(gt.get("relevance_class", ""), "ground-truth relevance_class", paper_id)
        predicted = as_int(pred.get("relevance_class", ""), "predicted relevance_class", paper_id)
        pairs.append((truth, predicted))
        valid_ids.append(paper_id)

        gt_decision = gt.get("reading_decision", "").strip()
        pred_decision = pred.get("reading_decision", "").strip()
        comparison_rows.append(
            {
                "paper_id": paper_id,
                "title": pred.get("title", ""),
                "gt_class": truth,
                "pred_class": predicted,
                "class_error": predicted - truth,
                "abs_class_error": abs(predicted - truth),
                "gt_label": gt.get("relevance_label", LABELS[truth]),
                "pred_label": pred.get("relevance_label", LABELS[predicted]),
                "gt_reading_decision": gt_decision,
                "pred_reading_decision": pred_decision,
                "gt_relevant": int(truth >= args.relevant_threshold),
                "pred_relevant": int(predicted >= args.relevant_threshold),
                "binary_correct": int((truth >= args.relevant_threshold) == (predicted >= args.relevant_threshold)),
                "exact_class_correct": int(truth == predicted),
            }
        )

    n = len(pairs)
    matrix = confusion_matrix(pairs)
    class_metrics = per_class_metrics(matrix)
    accuracy = safe_div(sum(matrix[i][i] for i in range(4)), n)
    macro_precision = sum(float(class_metrics[str(i)]["precision"]) for i in range(4)) / 4
    macro_recall = sum(float(class_metrics[str(i)]["recall"]) for i in range(4)) / 4
    macro_f1 = sum(float(class_metrics[str(i)]["f1"]) for i in range(4)) / 4
    mae = sum(abs(t - p) for t, p in pairs) / n
    rmse = math.sqrt(sum((t - p) ** 2 for t, p in pairs) / n)

    threshold = args.relevant_threshold
    tp = sum(1 for t, p in pairs if t >= threshold and p >= threshold)
    fp = sum(1 for t, p in pairs if t < threshold and p >= threshold)
    fn = sum(1 for t, p in pairs if t >= threshold and p < threshold)
    tn = sum(1 for t, p in pairs if t < threshold and p < threshold)
    binary_precision = safe_div(tp, tp + fp)
    binary_recall = safe_div(tp, tp + fn)
    binary_f1 = f1_score(binary_precision, binary_recall)
    fnr = safe_div(fn, tp + fn)

    class3_total = sum(1 for t, _ in pairs if t == 3)
    class3_detected = sum(1 for t, p in pairs if t == 3 and p == 3)
    class3_recall = safe_div(class3_detected, class3_total)

    gt_decisions = {pid: gt_idx[pid].get("reading_decision", "").strip() for pid in valid_ids}
    pred_decisions = {pid: pred_idx[pid].get("reading_decision", "").strip() for pid in valid_ids}
    gt_active = sum(d in ACTIVE_READING for d in gt_decisions.values())
    pred_active = sum(d in ACTIVE_READING for d in pred_decisions.values())
    relevant_ids = {pid for pid in valid_ids if int(gt_idx[pid]["relevance_class"]) >= threshold}
    relevant_retained_active = sum(pred_decisions[pid] in ACTIVE_READING for pid in relevant_ids)

    metrics: dict[str, Any] = {
        "benchmark": "Academic Screening evaluation",
        "run": str(run_dir),
        "ground_truth": str(args.ground_truth),
        "papers_evaluated": n,
        "relevant_threshold": threshold,
        "ground_truth_class_distribution": dict(sorted(Counter(t for t, _ in pairs).items())),
        "predicted_class_distribution": dict(sorted(Counter(p for _, p in pairs).items())),
        "multiclass": {
            "accuracy": round_metric(accuracy),
            "macro_precision": round_metric(macro_precision),
            "macro_recall": round_metric(macro_recall),
            "macro_f1": round_metric(macro_f1),
            "confusion_matrix": matrix,
            "per_class": class_metrics,
        },
        "ordinal": {
            "mae": round_metric(mae),
            "rmse": round_metric(rmse),
            "linear_weighted_kappa": round_metric(weighted_kappa(pairs, quadratic=False)),
            "quadratic_weighted_kappa": round_metric(weighted_kappa(pairs, quadratic=True)),
        },
        "binary_screening": {
            "true_positive": tp,
            "false_positive": fp,
            "false_negative": fn,
            "true_negative": tn,
            "precision": round_metric(binary_precision),
            "recall": round_metric(binary_recall),
            "f1": round_metric(binary_f1),
            "false_negative_rate": round_metric(fnr),
            "class3_recall": round_metric(class3_recall),
        },
        "reading_workload": {
            "active_reading_definition": sorted(ACTIVE_READING),
            "ground_truth_active_reading": gt_active,
            "predicted_active_reading": pred_active,
            "predicted_active_reading_fraction": round_metric(safe_div(pred_active, n)),
            "potential_active_reading_reduction": round_metric(1.0 - safe_div(pred_active, n)),
            "ground_truth_relevant": len(relevant_ids),
            "relevant_retained_by_active_reading": relevant_retained_active,
            "relevant_retention_by_active_reading": round_metric(safe_div(relevant_retained_active, len(relevant_ids))),
            "ground_truth_decision_distribution": dict(sorted(Counter(gt_decisions.values()).items())),
            "predicted_decision_distribution": dict(sorted(Counter(pred_decisions.values()).items())),
        },
    }

    if manifest_path.exists():
        try:
            metrics["run_manifest"] = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            metrics["run_manifest_error"] = "manifest.json is not valid JSON"

    metrics_path = run_dir / "evaluation.json"
    comparisons_path = run_dir / "comparison.csv"
    report_path = run_dir / "evaluation.md"
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(
        comparisons_path,
        comparison_rows,
        [
            "paper_id",
            "title",
            "gt_class",
            "pred_class",
            "class_error",
            "abs_class_error",
            "gt_label",
            "pred_label",
            "gt_reading_decision",
            "pred_reading_decision",
            "gt_relevant",
            "pred_relevant",
            "binary_correct",
            "exact_class_correct",
        ],
    )
    report_path.write_text(render_report(metrics), encoding="utf-8")

    print("Academic Screening evaluation complete")
    print(f"Papers evaluated: {n}")
    print(f"Exact 4-class accuracy: {accuracy:.3f}")
    print(f"Macro F1: {macro_f1:.3f}")
    print(f"Relevant-paper recall (GT >= {threshold}): {binary_recall:.3f}")
    print(f"Relevant-paper precision: {binary_precision:.3f}")
    print(f"False-negative rate: {fnr:.3f}")
    print(f"Class-3 recall: {class3_recall:.3f}")
    print(f"MAE relevance class: {mae:.3f}")
    print(f"Quadratic weighted kappa: {weighted_kappa(pairs, quadratic=True):.3f}")
    print(f"Potential active-reading reduction: {1.0 - safe_div(pred_active, n):.3f}")
    print(f"Relevant retention by active-reading policy: {safe_div(relevant_retained_active, len(relevant_ids)):.3f}")
    print(f"Metrics: {metrics_path}")
    print(f"Comparison: {comparisons_path}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
