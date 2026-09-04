#!/usr/bin/env python3
"""Build a reproducible inventory for the Academic Screening PDF corpus.

This script does not parse PDF text. It freezes the raw corpus by assigning
stable paper IDs in deterministic filename order and recording file size,
modification time, and SHA-256 hash for each PDF.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def build_inventory(input_dir: Path, output_csv: Path) -> int:
    pdfs = sorted(
        (p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"),
        key=lambda p: p.name.casefold(),
    )

    if not pdfs:
        raise SystemExit(f"No PDF files found in: {input_dir}")

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "paper_id",
        "filename",
        "relative_path",
        "size_bytes",
        "modified_utc",
        "sha256",
    ]

    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for index, pdf in enumerate(pdfs, start=1):
            stat = pdf.stat()
            writer.writerow(
                {
                    "paper_id": f"P{index:03d}",
                    "filename": pdf.name,
                    "relative_path": pdf.name,
                    "size_bytes": stat.st_size,
                    "modified_utc": datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ).isoformat(),
                    "sha256": sha256_file(pdf),
                }
            )

    return len(pdfs)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a deterministic SHA-256 inventory for an Academic Screening PDF corpus."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("/srv/data/papers/academic-screening-v0.1/raw"),
        help="Directory containing raw PDF files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "/srv/data/papers/academic-screening-v0.1/metadata/pdf-inventory-v0.1.csv"
        ),
        help="CSV file to create.",
    )
    args = parser.parse_args()

    if not args.input.exists() or not args.input.is_dir():
        raise SystemExit(f"Input directory does not exist: {args.input}")

    count = build_inventory(args.input, args.output)
    print(f"PDF count: {count}")
    print(f"Inventory: {args.output}")


if __name__ == "__main__":
    main()
