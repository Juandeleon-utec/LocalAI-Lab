#!/usr/bin/env python3
"""Deterministic page-bounded chunking for BENCH-QUANT-RAG-001.

Input: pages.jsonl produced by prepare_corpus.py.
Output: chunks.jsonl and chunk_manifest.json.
No ground-truth question/answer files are read.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def text_windows(text: str, size: int, overlap: int):
    """Yield reproducible slices. No slice can cross a PDF page."""
    if not text.strip():
        return
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            # Prefer a word boundary near the target endpoint.
            boundary = text.rfind(" ", start + max(1, size // 2), end)
            if boundary > start:
                end = boundary + 1
        part = text[start:end].strip()
        if part:
            yield start, end, part
        if end == len(text):
            break
        next_start = end - overlap
        if next_start <= start:
            next_start = start + 1
        start = next_start

def chunk_pages(input_file: Path, output_dir: Path, size: int = 900, overlap: int = 150):
    if size < 100 or overlap < 0 or overlap >= size // 2:
        raise ValueError("Expected size >= 100 and 0 <= overlap < size/2")
    input_file = input_file.resolve()
    output_dir = output_dir.resolve()
    if not input_file.exists():
        raise FileNotFoundError(input_file)
    output_dir.mkdir(parents=True, exist_ok=True)
    chunks = []
    document_pages = set()
    with input_file.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            page = json.loads(line)
            for required in ("doc_id", "source_file", "page_pdf", "text", "text_sha256"):
                if required not in page:
                    raise ValueError(f"Line {line_number}: missing {required}")
            if page["doc_id"] not in ("arduino", "logo"):
                raise ValueError(f"Line {line_number}: unexpected document {page['doc_id']}")
            key = (page["doc_id"], page["page_pdf"])
            if key in document_pages:
                raise ValueError(f"Line {line_number}: duplicate page {key}")
            document_pages.add(key)
            text = page["text"]
            if digest(text.encode("utf-8")) != page["text_sha256"]:
                raise ValueError(f"Line {line_number}: text hash mismatch")
            for i, (start, end, fragment) in enumerate(text_windows(text, size, overlap), 1):
                chunks.append({
                    "chunk_id": f"{page['doc_id']}-p{page['page_pdf']:04d}-c{i:03d}",
                    "doc_id": page["doc_id"],
                    "source_file": page["source_file"],
                    "page_pdf": page["page_pdf"],
                    "part": i,
                    "start_char": start,
                    "end_char": end,
                    "text": fragment,
                    "text_sha256": digest(fragment.encode("utf-8")),
                })
    payload = "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in chunks)
    manifest = {
        "benchmark": "BENCH-QUANT-RAG-001",
        "stage": "chunking",
        "version": 1,
        "source_pages_sha256": digest(input_file.read_bytes()),
        "size_chars": size,
        "overlap_chars": overlap,
        "input_pages": len(document_pages),
        "output_chunks": len(chunks),
        "chunks_sha256": digest(payload.encode("utf-8")),
    }
    (output_dir / "chunks.jsonl").write_bytes(payload.encode("utf-8"))
    (output_dir / "chunk_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Path to pages.jsonl")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--size", type=int, default=900, help="Target maximum characters per chunk")
    parser.add_argument("--overlap", type=int, default=150, help="Overlap in characters")
    options = parser.parse_args()
    print(json.dumps(chunk_pages(options.input, options.output_dir, options.size, options.overlap), indent=2))

if __name__ == "__main__":
    main()
