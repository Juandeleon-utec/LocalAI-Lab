#!/usr/bin/env python3
"""Prepare an immutable, page-aware PDF corpus for BENCH-QUANT-RAG-001.

Only manuals are permitted in this stage; question/answer documents are never indexed.
This produces source_inventory.json and pages.jsonl, without embeddings or LLM calls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    import pymupdf as fitz  # PyMuPDF public API
except ImportError as exc:
    raise SystemExit("Install dependency: python -m pip install pymupdf") from exc

SOURCES = {
    "arduino": "Manual+Programacion+Arduino.pdf",
    "logo": "Logo_s.pdf",
}

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def prepare(input_dir: Path, output_dir: Path) -> dict:
    input_dir = input_dir.resolve()
    output_dir = output_dir.resolve()
    if input_dir == output_dir:
        raise ValueError("Input and output directories must differ")
    # Refuse unknown PDFs or question/answer files in the source folder.
    observed = {p.name for p in input_dir.iterdir() if p.is_file()}
    extra_pdfs = sorted(name for name in observed if name.lower().endswith(".pdf") and name not in SOURCES.values())
    if extra_pdfs:
        raise ValueError(f"Unexpected PDFs in corpus folder: {extra_pdfs}")
    for filename in SOURCES.values():
        if filename not in observed:
            raise FileNotFoundError(input_dir / filename)
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory = {"benchmark": "BENCH-QUANT-RAG-001", "version": 1, "sources": []}
    # Build first, then write; never include ground truth in this corpus.
    pages: list[dict] = []
    for doc_id, filename in SOURCES.items():
        path = input_dir / filename
        with fitz.open(path) as pdf:
            count = pdf.page_count
            for idx, page in enumerate(pdf):
                text = page.get_text("text", sort=True) or ""
                pages.append({
                    "doc_id": doc_id,
                    "source_file": filename,
                    "page_pdf": idx + 1,
                    "text": text,
                    "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "char_count": len(text),
                })
        inventory["sources"].append({
            "doc_id": doc_id,
            "filename": filename,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "page_count": count,
        })
    with (output_dir / "pages.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
        for page in pages:
            stream.write(json.dumps(page, ensure_ascii=False) + "\n")
    (output_dir / "source_inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    inventory["total_pages"] = len(pages)
    return inventory

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True, help="Folder containing ONLY the two manual PDFs")
    parser.add_argument("--output-dir", type=Path, required=True, help="Folder for generated page-wise corpus")
    args = parser.parse_args()
    result = prepare(args.input_dir, args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
