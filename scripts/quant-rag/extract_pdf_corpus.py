#!/usr/bin/env python3
"""Extract text and basic metadata from the Academic Screening PDF corpus.

The script reads the frozen PDF inventory created by build_pdf_inventory.py,
extracts page-aware text with PyMuPDF, writes one UTF-8 text file per paper,
and creates a CSV containing extraction metrics and conservative metadata.

No LLM, OCR, embeddings, or network access are used. This stage is intended to
be deterministic and auditable so parsing cost and quality can be measured
separately from later RAG stages.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ABSTRACT_BLOCK_RE = re.compile(
    r"(?is)"
    r"(?:\bA\s*B\s*S\s*T\s*R\s*A\s*C\s*T\b|\bAbstract\b|\bSummary\b)"
    r"\s*"
    r"(.*?)"
    r"(?="
    r"\n\s*(?:1[\.\s]+)?Introduction\b"
    r"|\n\s*Index Terms\b"
    r"|$"
    r")"
)

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "PyMuPDF is required. Install it with: python3 -m pip install pymupdf"
    ) from exc



DEFAULT_ROOT = Path("/srv/data/papers/academic-screening-v0.1")

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")


@dataclass
class ExtractionResult:
    paper_id: str
    filename: str
    sha256: str
    title: str
    authors: str
    year: str
    doi: str
    abstract: str
    keywords: str
    page_count: int
    characters_extracted: int
    words_extracted: int
    extraction_time_s: float
    extraction_status: str
    error: str
    text_path: str


def normalize_space(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def clean_doi(value: str) -> str:
    return value.rstrip(".,;:)\]}>")


def first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(0) if match else ""

def extract_abstract(text: str, max_chars: int = 5000) -> str:
    """Conservatively extract an abstract from the first pages."""
    sample = text[:30000]

    match = re.search(
        r"(?is)"
        r"(?:^|\n)\s*"
        r"(?:A\s*B\s*S\s*T\s*R\s*A\s*C\s*T|Summary)"
        r"\s*[:\-]?\s*"
        r"(.+?)"
        r"(?="
        r"\n\s*(?:1[\.\s]+)?Introduction\b"
        r"|\n\s*Index Terms\b"
        r"|$"
        r")",
        sample,
    )

    if not match:
        return ""

    return normalize_space(match.group(1))[:max_chars]


def extract_keywords(text: str, max_chars: int = 1500) -> str:
    sample = text[:30000]
    match = re.search(
        r"(?is)(?:^|\n)\s*(?:keywords?|index terms)\s*[:\-]\s*(.+?)(?=\n\s*(?:1\.?\s+introduction|introduction|1\.)\b)",
        sample,
    )
    if not match:
        return ""
    return normalize_space(match.group(1))[:max_chars]


def infer_year(metadata: dict[str, str], first_pages_text: str) -> str:
    for key in ("creationDate", "modDate"):
        value = metadata.get(key) or ""
        match = YEAR_RE.search(value)
        if match:
            return match.group(0)

    for match in YEAR_RE.finditer(first_pages_text[:6000]):
        year = int(match.group(0))
        if 1900 <= year <= 2100:
            return str(year)
    return ""


def candidate_title(metadata: dict[str, str], first_page_text: str) -> str:
    title = normalize_space(metadata.get("title"))
    if title and title.lower() not in {"untitled", "none"}:
        return title

    lines = [normalize_space(line) for line in first_page_text.splitlines()]
    lines = [line for line in lines if 12 <= len(line) <= 300]
    if not lines:
        return ""

    excluded = ("doi:", "http", "www.", "journal", "volume", "vol.", "copyright")
    for line in lines[:20]:
        lower = line.lower()
        if any(token in lower for token in excluded):
            continue
        if len(line.split()) >= 4:
            return line
    return ""


def page_text(doc: fitz.Document) -> tuple[str, str, int]:
    pages: list[str] = []
    total_chars = 0
    first_page = ""

    for index, page in enumerate(doc):
        text = page.get_text("text") or ""
        if index == 0:
            first_page = text
        total_chars += len(text)
        pages.append(f"\n\n===== PAGE {index + 1} =====\n\n{text.rstrip()}\n")

    return "".join(pages), first_page, total_chars


def read_inventory(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SystemExit(f"Inventory is empty: {path}")

    required = {"paper_id", "filename", "sha256"}
    missing = required - set(rows[0].keys())
    if missing:
        raise SystemExit(f"Inventory is missing required columns: {sorted(missing)}")
    return rows


def extract_one(
    row: dict[str, str], raw_dir: Path, extracted_dir: Path
) -> ExtractionResult:
    paper_id = row["paper_id"].strip()
    filename = row["filename"].strip()
    pdf_path = raw_dir / filename
    output_path = extracted_dir / f"{paper_id}.txt"
    start = time.perf_counter()

    try:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        with fitz.open(pdf_path) as doc:
            metadata = {k: (v or "") for k, v in (doc.metadata or {}).items()}
            full_text, first_page, char_count = page_text(doc)
            first_pages_sample = full_text[:50000]

            title = candidate_title(metadata, first_page)
            authors = normalize_space(metadata.get("author"))
            year = infer_year(metadata, first_pages_sample)
            doi = clean_doi(first_match(DOI_RE, first_pages_sample))
            abstract = extract_abstract(first_pages_sample)
            keywords = extract_keywords(first_pages_sample)
            page_count = doc.page_count

        extracted_dir.mkdir(parents=True, exist_ok=True)
        output_path.write_text(full_text, encoding="utf-8")

        elapsed = time.perf_counter() - start
        return ExtractionResult(
            paper_id=paper_id,
            filename=filename,
            sha256=row["sha256"].strip(),
            title=title,
            authors=authors,
            year=year,
            doi=doi,
            abstract=abstract,
            keywords=keywords,
            page_count=page_count,
            characters_extracted=char_count,
            words_extracted=len(full_text.split()),
            extraction_time_s=elapsed,
            extraction_status="ok" if char_count > 0 else "empty_text",
            error="",
            text_path=str(output_path),
        )
    except Exception as exc:
        elapsed = time.perf_counter() - start
        return ExtractionResult(
            paper_id=paper_id,
            filename=filename,
            sha256=row.get("sha256", "").strip(),
            title="",
            authors="",
            year="",
            doi="",
            abstract="",
            keywords="",
            page_count=0,
            characters_extracted=0,
            words_extracted=0,
            extraction_time_s=elapsed,
            extraction_status="error",
            error=f"{type(exc).__name__}: {exc}",
            text_path=str(output_path),
        )


def write_metadata(results: Iterable[ExtractionResult], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = list(ExtractionResult.__dataclass_fields__.keys())
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow(result.__dict__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract page-aware text and basic metadata from the frozen Academic Screening corpus."
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=DEFAULT_ROOT / "metadata" / "pdf-inventory-v0.1.csv",
        help="Frozen PDF inventory CSV.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=DEFAULT_ROOT / "raw",
        help="Directory containing the original PDF files.",
    )
    parser.add_argument(
        "--extracted-dir",
        type=Path,
        default=DEFAULT_ROOT / "extracted",
        help="Directory where Pxxx.txt files are written.",
    )
    parser.add_argument(
        "--metadata-output",
        type=Path,
        default=DEFAULT_ROOT / "metadata" / "papers-metadata-v0.1.csv",
        help="CSV containing extraction metrics and basic metadata.",
    )
    args = parser.parse_args()

    if not args.inventory.exists():
        raise SystemExit(f"Inventory does not exist: {args.inventory}")
    if not args.raw_dir.exists() or not args.raw_dir.is_dir():
        raise SystemExit(f"Raw PDF directory does not exist: {args.raw_dir}")

    rows = read_inventory(args.inventory)
    corpus_start = time.perf_counter()
    results: list[ExtractionResult] = []

    for index, row in enumerate(rows, start=1):
        result = extract_one(row, args.raw_dir, args.extracted_dir)
        results.append(result)
        print(
            f"[{index:03d}/{len(rows):03d}] {result.paper_id} "
            f"status={result.extraction_status} pages={result.page_count} "
            f"chars={result.characters_extracted} time={result.extraction_time_s:.3f}s"
        )

    write_metadata(results, args.metadata_output)
    total_time = time.perf_counter() - corpus_start

    ok = sum(r.extraction_status == "ok" for r in results)
    empty = sum(r.extraction_status == "empty_text" for r in results)
    errors = sum(r.extraction_status == "error" for r in results)
    total_pages = sum(r.page_count for r in results)
    total_chars = sum(r.characters_extracted for r in results)

    print("\nAcademic Screening PDF extraction complete")
    print(f"Documents: {len(results)}")
    print(f"OK: {ok}")
    print(f"Empty text: {empty}")
    print(f"Errors: {errors}")
    print(f"Pages: {total_pages}")
    print(f"Characters: {total_chars}")
    print(f"Wall time: {total_time:.3f}s")
    print(f"Metadata: {args.metadata_output}")
    print(f"Extracted text: {args.extracted_dir}")

    if errors:
        sys.exit(2)


if __name__ == "__main__":
    main()
