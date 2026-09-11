#!/usr/bin/env python3
"""Normalize academic-paper metadata and flag duplicate candidates.

This deterministic post-processing stage sits between PDF extraction and the
Academic Screening benchmark. It preserves the extractor output, derives
cleaned bibliographic fields, applies optional human overrides, computes
content fingerprints, flags likely duplicates, and emits a corpus-level
validation report.

No LLM, OCR, embeddings, or network access are used.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable


DEFAULT_ROOT = Path("/srv/data/papers/academic-screening-v0.1")

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
DOI_YEAR_RE = re.compile(r"(?:^|[./_-])((?:19|20)\d{2})(?:[./_-]|$)")
PAGE_SEPARATOR_RE = re.compile(r"(?m)^\s*=+\s*PAGE\s+\d+\s*=+\s*$")

TITLE_STOP_PREFIXES = (
    "abstract",
    "available online",
    "authorized licensed use",
    "copyright",
    "doi",
    "downloaded on",
    "elsevier",
    "ieee",
    "issn",
    "keywords",
    "peer-review",
    "procedia",
    "received ",
    "revised ",
    "science direct",
    "sciencedirect",
    "springer",
    "www.",
    "http",
)

TITLE_STOP_CONTAINS = (
    "all rights reserved",
    "creativecommons.org",
    "published by",
    "open access article",
    "volume ",
    "vol. ",
    "pages ",
)


@dataclass
class DuplicateCandidate:
    paper_id_a: str
    paper_id_b: str
    duplicate_type: str
    sha256_equal: bool
    doi_equal: bool
    normalized_text_sha256_equal: bool
    title_similarity: float
    title_a: str
    title_b: str
    recommended_action: str


def normalize_space(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def ascii_fold(value: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )


def normalize_for_compare(value: str) -> str:
    value = ascii_fold(value).lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return normalize_space(value)


def clean_doi(value: str | None) -> str:
    value = normalize_space(value)
    if not value:
        return ""
    match = DOI_RE.search(value)
    if not match:
        return ""
    return match.group(0).rstrip(".,;:)]}>").lower()


def normalize_text_for_hash(text: str) -> str:
    text = PAGE_SEPARATOR_RE.sub(" ", text)
    text = ascii_fold(text).lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def text_sha256(text: str) -> str:
    normalized = normalize_text_for_hash(text)
    if not normalized:
        return ""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def plausible_title_line(line: str) -> bool:
    line = normalize_space(line)
    if not (15 <= len(line) <= 240):
        return False
    lower = line.lower()
    if any(lower.startswith(prefix) for prefix in TITLE_STOP_PREFIXES):
        return False
    if any(token in lower for token in TITLE_STOP_CONTAINS):
        return False
    if "@" in line or DOI_RE.search(line):
        return False
    words = line.split()
    if len(words) < 4:
        return False
    alpha_words = sum(any(ch.isalpha() for ch in word) for word in words)
    if alpha_words < 4:
        return False
    digit_ratio = sum(ch.isdigit() for ch in line) / max(len(line), 1)
    if digit_ratio > 0.20:
        return False
    return True


def title_from_first_page(text: str) -> str:
    """Infer a title from the first page using conservative line heuristics."""
    first_page = text.split("===== PAGE 2 =====", 1)[0]
    lines = [normalize_space(line) for line in first_page.splitlines()]
    lines = [line for line in lines if line]

    candidates: list[tuple[int, str]] = []
    for index, line in enumerate(lines[:80]):
        if not plausible_title_line(line):
            continue

        # Join one following line when it looks like a wrapped title.
        joined = line
        if index + 1 < len(lines):
            nxt = lines[index + 1]
            if (
                plausible_title_line(nxt)
                and len(joined) + len(nxt) + 1 <= 260
                and not re.search(r"\b(?:university|department|institute|faculty)\b", nxt, re.I)
            ):
                joined = f"{joined} {nxt}"

        lower = joined.lower()
        score = 0
        if 5 <= len(joined.split()) <= 24:
            score += 4
        if 30 <= len(joined) <= 180:
            score += 3
        if not joined.endswith("."):
            score += 1
        if re.search(r"\b(?:fault|motor|machine|maintenance|vibration|edge|learning|diagnosis|monitoring|prediction)\b", lower):
            score += 2
        if re.search(r"\b(?:department|university|institute|conference|journal)\b", lower):
            score -= 5
        score -= min(index // 10, 4)
        candidates.append((score, joined))

    if not candidates:
        return ""
    candidates.sort(key=lambda item: (item[0], len(item[1])), reverse=True)
    return candidates[0][1]


def choose_title(raw_title: str, extracted_text: str) -> str:
    raw_title = normalize_space(raw_title)
    raw_ok = plausible_title_line(raw_title)
    inferred = title_from_first_page(extracted_text)

    if raw_ok:
        raw_lower = raw_title.lower()
        suspicious = any(raw_lower.startswith(prefix) for prefix in TITLE_STOP_PREFIXES)
        suspicious = suspicious or any(token in raw_lower for token in TITLE_STOP_CONTAINS)
        if not suspicious:
            return raw_title
    return inferred or raw_title


def infer_year(raw_year: str, doi: str, text: str) -> str:
    """Prefer DOI/copyright cues over a weak first-occurrence year."""
    doi_match = DOI_YEAR_RE.search(doi)
    if doi_match:
        return doi_match.group(1)

    first_page = text.split("===== PAGE 2 =====", 1)[0]
    cue_patterns = (
        r"(?:©|copyright)\s*((?:19|20)\d{2})",
        r"\b((?:19|20)\d{2})\s+IEEE\b",
        r"\b((?:19|20)\d{2})\s+The Authors\b",
        r"\b((?:19|20)\d{2})\s+(?:International|IEEE|ACM)\b",
    )
    for pattern in cue_patterns:
        match = re.search(pattern, first_page, re.I)
        if match:
            return match.group(1)

    raw_year = normalize_space(raw_year)
    if re.fullmatch(r"(?:19|20)\d{2}", raw_year):
        return raw_year

    match = YEAR_RE.search(first_page)
    return match.group(0) if match else ""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_overrides(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    rows = read_csv(path)
    return {row.get("paper_id", "").strip(): row for row in rows if row.get("paper_id", "").strip()}


def bool_from_override(value: str | None) -> bool:
    return normalize_space(value).lower() in {"1", "true", "yes", "y", "exclude"}


def write_manual_overrides_template(path: Path, paper_ids: Iterable[str]) -> None:
    """Create, but never overwrite, the human-review override template."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["paper_id", "title", "authors", "year", "doi", "exclude", "notes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for paper_id in paper_ids:
            writer.writerow({"paper_id": paper_id})


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def classify_duplicate(a: dict[str, str], b: dict[str, str]) -> DuplicateCandidate | None:
    sha_equal = bool(a["sha256"] and a["sha256"] == b["sha256"])
    doi_equal = bool(a["doi_clean"] and a["doi_clean"] == b["doi_clean"])
    text_equal = bool(
        a["normalized_text_sha256"]
        and a["normalized_text_sha256"] == b["normalized_text_sha256"]
    )

    title_a_norm = normalize_for_compare(a["title_clean"])
    title_b_norm = normalize_for_compare(b["title_clean"])
    similarity = (
        SequenceMatcher(None, title_a_norm, title_b_norm).ratio()
        if title_a_norm and title_b_norm
        else 0.0
    )

    if sha_equal:
        duplicate_type = "DUPLICATE_EXACT"
        action = "KEEP_ONE_REVIEW"
    elif doi_equal:
        duplicate_type = "DUPLICATE_DOI"
        action = "KEEP_ONE_REVIEW"
    elif text_equal:
        duplicate_type = "DUPLICATE_TEXT"
        action = "KEEP_ONE_REVIEW"
    elif similarity >= 0.94:
        duplicate_type = "POSSIBLE_DUPLICATE_TITLE"
        action = "MANUAL_REVIEW"
    else:
        return None

    return DuplicateCandidate(
        paper_id_a=a["paper_id"],
        paper_id_b=b["paper_id"],
        duplicate_type=duplicate_type,
        sha256_equal=sha_equal,
        doi_equal=doi_equal,
        normalized_text_sha256_equal=text_equal,
        title_similarity=round(similarity, 4),
        title_a=a["title_clean"],
        title_b=b["title_clean"],
        recommended_action=action,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize Academic Screening metadata and flag duplicate candidates."
    )
    parser.add_argument(
        "--metadata-input",
        type=Path,
        default=DEFAULT_ROOT / "metadata" / "papers-metadata-v0.1.csv",
    )
    parser.add_argument(
        "--extracted-dir",
        type=Path,
        default=DEFAULT_ROOT / "extracted",
    )
    parser.add_argument(
        "--manual-overrides",
        type=Path,
        default=DEFAULT_ROOT / "metadata" / "manual-overrides-v0.1.csv",
    )
    parser.add_argument(
        "--clean-output",
        type=Path,
        default=DEFAULT_ROOT / "metadata" / "papers-metadata-clean-v0.1.csv",
    )
    parser.add_argument(
        "--duplicates-output",
        type=Path,
        default=DEFAULT_ROOT / "metadata" / "duplicate-candidates-v0.1.csv",
    )
    parser.add_argument(
        "--validation-output",
        type=Path,
        default=DEFAULT_ROOT / "metadata" / "corpus-validation-v0.1.json",
    )
    args = parser.parse_args()

    if not args.metadata_input.exists():
        raise SystemExit(f"Metadata input does not exist: {args.metadata_input}")
    if not args.extracted_dir.exists():
        raise SystemExit(f"Extracted text directory does not exist: {args.extracted_dir}")

    rows = read_csv(args.metadata_input)
    if not rows:
        raise SystemExit(f"Metadata input is empty: {args.metadata_input}")

    required = {"paper_id", "filename", "sha256", "title", "authors", "year", "doi", "extraction_status"}
    missing = required - set(rows[0].keys())
    if missing:
        raise SystemExit(f"Metadata input is missing required columns: {sorted(missing)}")

    paper_ids = [row["paper_id"].strip() for row in rows]
    write_manual_overrides_template(args.manual_overrides, paper_ids)
    overrides = load_overrides(args.manual_overrides)

    cleaned: list[dict[str, str]] = []
    for row in rows:
        paper_id = row["paper_id"].strip()
        text_path = args.extracted_dir / f"{paper_id}.txt"
        text = text_path.read_text(encoding="utf-8", errors="replace") if text_path.exists() else ""

        doi_clean = clean_doi(row.get("doi", ""))
        title_clean = choose_title(row.get("title", ""), text)
        year_clean = infer_year(row.get("year", ""), doi_clean, text)
        authors_clean = normalize_space(row.get("authors", ""))

        override = overrides.get(paper_id, {})
        if normalize_space(override.get("title")):
            title_clean = normalize_space(override["title"])
        if normalize_space(override.get("authors")):
            authors_clean = normalize_space(override["authors"])
        if normalize_space(override.get("year")):
            year_clean = normalize_space(override["year"])
        if normalize_space(override.get("doi")):
            doi_clean = clean_doi(override["doi"])

        excluded = bool_from_override(override.get("exclude"))
        notes = normalize_space(override.get("notes"))
        normalized_hash = text_sha256(text)

        review_reasons: list[str] = []
        if row.get("extraction_status", "").strip() != "ok":
            review_reasons.append("extraction_not_ok")
        if not title_clean:
            review_reasons.append("missing_title")
        if not year_clean:
            review_reasons.append("missing_year")
        if not text.strip():
            review_reasons.append("missing_text")
        if excluded:
            status = "EXCLUDED"
        elif review_reasons:
            status = "REVIEW_METADATA"
        else:
            status = "READY"

        cleaned_row = dict(row)
        cleaned_row.update(
            {
                "title_raw": normalize_space(row.get("title", "")),
                "title_clean": title_clean,
                "authors_raw": normalize_space(row.get("authors", "")),
                "authors_clean": authors_clean,
                "year_raw": normalize_space(row.get("year", "")),
                "year_clean": year_clean,
                "doi_raw": normalize_space(row.get("doi", "")),
                "doi_clean": doi_clean,
                "normalized_text_sha256": normalized_hash,
                "manual_exclude": str(excluded).lower(),
                "manual_notes": notes,
                "corpus_status": status,
                "review_reasons": ";".join(review_reasons),
            }
        )
        cleaned.append(cleaned_row)

    duplicates: list[DuplicateCandidate] = []
    duplicate_ids: set[str] = []

    status_by_id = {
        row["paper_id"]: row["corpus_status"]
        for row in cleaned
    }

    for i, row_a in enumerate(cleaned):
        for row_b in cleaned[i + 1:]:
            candidate = classify_duplicate(row_a, row_b)

            if candidate:
                duplicates.append(candidate)

                a_active = (
                    status_by_id[candidate.paper_id_a] != "EXCLUDED"
                )
                b_active = (
                    status_by_id[candidate.paper_id_b] != "EXCLUDED"
                )

                # Only flag an unresolved duplicate when both documents
                # remain active in the corpus.
                if a_active and b_active:
                    duplicate_ids.update(
                        (
                            candidate.paper_id_a,
                            candidate.paper_id_b,
                        )
                 )

    for row in cleaned:
        if row["paper_id"] in duplicate_ids and row["corpus_status"] == "READY":
            row["corpus_status"] = "POSSIBLE_DUPLICATE"
            row["review_reasons"] = "possible_duplicate"

    clean_fields = list(cleaned[0].keys())
    write_csv(args.clean_output, cleaned, clean_fields)

    duplicate_rows = [asdict(item) for item in duplicates]
    duplicate_fields = list(DuplicateCandidate.__dataclass_fields__.keys())
    write_csv(args.duplicates_output, duplicate_rows, duplicate_fields)

    validation = {
        "schema_version": "0.1",
        "documents": len(cleaned),
        "extraction_ok": sum(row.get("extraction_status") == "ok" for row in cleaned),
        "ready": sum(row["corpus_status"] == "READY" for row in cleaned),
        "review_metadata": sum(row["corpus_status"] == "REVIEW_METADATA" for row in cleaned),
        "possible_duplicate_documents": sum(row["corpus_status"] == "POSSIBLE_DUPLICATE" for row in cleaned),
        "excluded": sum(row["corpus_status"] == "EXCLUDED" for row in cleaned),
        "missing_title": sum(not row["title_clean"] for row in cleaned),
        "missing_year": sum(not row["year_clean"] for row in cleaned),
        "missing_doi": sum(not row["doi_clean"] for row in cleaned),
        "duplicate_candidate_pairs": len(duplicates),
        "duplicate_types": {
            kind: sum(item.duplicate_type == kind for item in duplicates)
            for kind in (
                "DUPLICATE_EXACT",
                "DUPLICATE_DOI",
                "DUPLICATE_TEXT",
                "POSSIBLE_DUPLICATE_TITLE",
            )
        },
        "inputs": {
            "metadata": str(args.metadata_input),
            "extracted_dir": str(args.extracted_dir),
            "manual_overrides": str(args.manual_overrides),
        },
        "outputs": {
            "clean_metadata": str(args.clean_output),
            "duplicate_candidates": str(args.duplicates_output),
        },
    }
    args.validation_output.parent.mkdir(parents=True, exist_ok=True)
    args.validation_output.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("Academic Screening metadata normalization complete")
    print(f"Documents: {validation['documents']}")
    print(f"Ready: {validation['ready']}")
    print(f"Metadata review: {validation['review_metadata']}")
    print(f"Possible duplicate documents: {validation['possible_duplicate_documents']}")
    print(f"Excluded: {validation['excluded']}")
    print(f"Duplicate candidate pairs: {validation['duplicate_candidate_pairs']}")
    print(f"Clean metadata: {args.clean_output}")
    print(f"Duplicate candidates: {args.duplicates_output}")
    print(f"Validation report: {args.validation_output}")
    print(f"Manual overrides: {args.manual_overrides}")


if __name__ == "__main__":
    main()
