#!/usr/bin/env python3
"""Build the frozen Academic Screening v0.1 dataset and empty human ground truth.

This deterministic stage consumes cleaned corpus metadata, keeps only READY
papers, writes the screening dataset used by model experiments, creates a
human ground-truth template without overwriting existing labels, and records a
manifest with counts and SHA-256 fingerprints.

No LLM, embeddings, OCR, or network access are used.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

CORPUS_ROOT = Path("/srv/data/papers/academic-screening-v0.1")
BENCH_ROOT = Path("/srv/data/benchmarks/academic-rag")

PAPERS_FIELDS = [
    "paper_id",
    "title",
    "authors",
    "year",
    "doi",
    "scopus_id",
    "source",
    "abstract",
    "keywords",
    "filename",
    "document_type",
    "language",
    "notes",
]

GROUND_TRUTH_FIELDS = [
    "paper_id",
    "relevance_class",
    "relevance_label",
    "reading_decision",
    "evaluator",
    "evaluation_date",
    "confidence",
    "topic_match",
    "methodology_match",
    "hardware_or_sensor_match",
    "dataset_match",
    "edge_ai_relevance",
    "machine_learning_method_match",
    "experimental_design_value",
    "state_of_the_art_value",
    "rationale",
    "recommended_sections",
    "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean(value: str | None) -> str:
    return (value or "").strip()


def pick(row: dict[str, str], preferred: str, fallback: str) -> str:
    return clean(row.get(preferred)) or clean(row.get(fallback))


def build_dataset_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[str]]:
    dataset: list[dict[str, str]] = []
    skipped: list[str] = []

    for row in rows:
        paper_id = clean(row.get("paper_id"))
        status = clean(row.get("corpus_status")).upper()
        if status != "READY":
            skipped.append(paper_id)
            continue

        dataset.append(
            {
                "paper_id": paper_id,
                "title": pick(row, "title_clean", "title"),
                "authors": pick(row, "authors_clean", "authors"),
                "year": pick(row, "year_clean", "year"),
                "doi": pick(row, "doi_clean", "doi"),
                "scopus_id": clean(row.get("scopus_id")),
                "source": "local_pdf_corpus",
                "abstract": clean(row.get("abstract")),
                "keywords": clean(row.get("keywords")),
                "filename": clean(row.get("filename")),
                "document_type": clean(row.get("document_type")) or "article",
                "language": clean(row.get("language")) or "en",
                "notes": clean(row.get("manual_notes")),
            }
        )

    dataset.sort(key=lambda item: item["paper_id"])
    return dataset, skipped


def validate_dataset(rows: list[dict[str, str]]) -> dict[str, int]:
    ids = [row["paper_id"] for row in rows]
    duplicate_ids = len(ids) - len(set(ids))
    return {
        "documents": len(rows),
        "duplicate_paper_ids": duplicate_ids,
        "missing_title": sum(not row["title"] for row in rows),
        "missing_abstract": sum(not row["abstract"] for row in rows),
        "missing_keywords": sum(not row["keywords"] for row in rows),
        "missing_year": sum(not row["year"] for row in rows),
        "missing_doi": sum(not row["doi"] for row in rows),
        "missing_authors": sum(not row["authors"] for row in rows),
    }


def create_ground_truth_if_missing(path: Path, paper_ids: list[str]) -> bool:
    """Create the human-label file once; never overwrite prior evaluations."""
    if path.exists():
        return False

    rows = []
    for paper_id in paper_ids:
        row = {field: "" for field in GROUND_TRUTH_FIELDS}
        row["paper_id"] = paper_id
        rows.append(row)
    write_csv(path, rows, GROUND_TRUTH_FIELDS)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Academic Screening v0.1 benchmark dataset.")
    parser.add_argument(
        "--clean-metadata",
        type=Path,
        default=CORPUS_ROOT / "metadata" / "papers-metadata-clean-v0.1.csv",
    )
    parser.add_argument(
        "--dataset-output",
        type=Path,
        default=BENCH_ROOT / "datasets" / "academic-screening-v0.1" / "papers-v0.1.csv",
    )
    parser.add_argument(
        "--ground-truth-output",
        type=Path,
        default=BENCH_ROOT / "ground-truth" / "academic-screening-v0.1" / "ground-truth-v0.1.csv",
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=BENCH_ROOT / "datasets" / "academic-screening-v0.1" / "manifest-v0.1.json",
    )
    args = parser.parse_args()

    if not args.clean_metadata.exists():
        raise SystemExit(f"Clean metadata does not exist: {args.clean_metadata}")

    source_rows = read_csv(args.clean_metadata)
    if not source_rows:
        raise SystemExit(f"Clean metadata is empty: {args.clean_metadata}")

    required = {"paper_id", "corpus_status", "filename"}
    missing = required - set(source_rows[0].keys())
    if missing:
        raise SystemExit(f"Clean metadata is missing required columns: {sorted(missing)}")

    dataset_rows, skipped = build_dataset_rows(source_rows)
    validation = validate_dataset(dataset_rows)

    if validation["duplicate_paper_ids"]:
        raise SystemExit("Dataset contains duplicate paper_id values; refusing to freeze it.")
    if validation["missing_title"]:
        raise SystemExit("Dataset contains missing titles; fix metadata before freezing it.")
    if validation["missing_abstract"]:
        raise SystemExit(
            f"Dataset contains {validation['missing_abstract']} papers without abstracts; "
            "fix or explicitly review them before the screening benchmark."
        )

    write_csv(args.dataset_output, dataset_rows, PAPERS_FIELDS)
    ground_truth_created = create_ground_truth_if_missing(
        args.ground_truth_output, [row["paper_id"] for row in dataset_rows]
    )

    manifest = {
        "schema_version": "0.1",
        "benchmark": "academic-screening-v0.1",
        "corpus": "academic-screening-v0.1",
        "source_documents": len(source_rows),
        "included_documents": len(dataset_rows),
        "excluded_or_nonready_documents": len(skipped),
        "skipped_paper_ids": skipped,
        "validation": validation,
        "inputs": {
            "clean_metadata": str(args.clean_metadata),
            "clean_metadata_sha256": file_sha256(args.clean_metadata),
        },
        "outputs": {
            "papers": str(args.dataset_output),
            "papers_sha256": file_sha256(args.dataset_output),
            "ground_truth": str(args.ground_truth_output),
            "ground_truth_created": ground_truth_created,
        },
        "notes": [
            "Only rows with corpus_status=READY are included.",
            "paper_id values are preserved from the source corpus and are not renumbered.",
            "Ground truth is created only when missing and is never overwritten by this script.",
            "No model predictions are stored in the ground-truth file.",
        ],
    }

    args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("Academic Screening dataset build complete")
    print(f"Source documents: {len(source_rows)}")
    print(f"Included READY documents: {len(dataset_rows)}")
    print(f"Skipped documents: {len(skipped)}")
    print(f"Missing keywords: {validation['missing_keywords']}")
    print(f"Missing DOI: {validation['missing_doi']}")
    print(f"Missing authors: {validation['missing_authors']}")
    print(f"Dataset: {args.dataset_output}")
    print(f"Ground truth: {args.ground_truth_output}")
    print(f"Manifest: {args.manifest_output}")
    print(f"Ground truth created now: {ground_truth_created}")


if __name__ == "__main__":
    main()
