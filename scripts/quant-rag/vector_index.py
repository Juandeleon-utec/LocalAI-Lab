#!/usr/bin/env python3
"""Frozen E5 vector index and deterministic Top-K retrieval for BENCH-QUANT-RAG-001.

Index uses ONLY chunks.jsonl from the two manuals. Ground-truth answers are never loaded.
Install: python -m pip install numpy sentence-transformers huggingface_hub
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
PASSAGE_PREFIX = "passage: "
QUERY_PREFIX = "query: "

def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()

def rows(path: Path):
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)

def validate_chunks(path: Path):
    items = list(rows(path))
    if not items:
        raise ValueError("No chunks found")
    seen = set()
    for item in items:
        for field in ("chunk_id", "doc_id", "page_pdf", "text", "text_sha256"):
            if field not in item:
                raise ValueError("Chunk missing field: " + field)
        if item["doc_id"] not in ("arduino", "logo"):
            raise ValueError("Unexpected document ID")
        if item["chunk_id"] in seen:
            raise ValueError("Duplicate chunk_id")
        seen.add(item["chunk_id"])
        if sha256(item["text"].encode("utf-8")) != item["text_sha256"]:
            raise ValueError("Chunk text hash mismatch: " + item["chunk_id"])
    return items

def normalized(array):
    import numpy as np
    vectors = np.asarray(array, dtype=np.float32)
    if vectors.ndim != 2 or vectors.shape[1] == 0:
        raise ValueError("Embeddings must be a 2D matrix")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    if not np.isfinite(vectors).all() or (norms == 0).any():
        raise ValueError("Non-finite or zero embeddings")
    return np.ascontiguousarray(vectors / norms)

def load_model(model_name: str, revision: str, device: str):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name, revision=revision, device=device, trust_remote_code=False)

def frozen_revision(revision: str):
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Embedding revision must be an immutable 40-character Git SHA")

def build(chunks_file: Path, index_dir: Path, model, model_name: str, revision: str, batch_size: int = 32):
    import numpy as np
    frozen_revision(revision)
    chunks_file = chunks_file.resolve()
    chunks = validate_chunks(chunks_file)
    vectors = normalized(model.encode(
        [PASSAGE_PREFIX + c["text"] for c in chunks],
        batch_size=batch_size, convert_to_numpy=True, show_progress_bar=True
    ))
    if vectors.shape[0] != len(chunks):
        raise ValueError("Wrong embedding count")
    index_dir.mkdir(parents=True, exist_ok=True)
    vector_file = index_dir / "embeddings.npy"
    np.save(vector_file, vectors, allow_pickle=False)
    manifest = {
        "benchmark": "BENCH-QUANT-RAG-001", "index_version": 1,
        "chunk_count": len(chunks), "dimensions": int(vectors.shape[1]),
        "chunks_path": str(chunks_file),
        "chunks_sha256": sha256(chunks_file.read_bytes()),
        "vectors_sha256": sha256(vector_file.read_bytes()),
        "embedding_model": model_name,
        "embedding_revision": revision,
        "passage_prefix": PASSAGE_PREFIX, "query_prefix": QUERY_PREFIX,
        "similarity": "cosine", "normalization": "l2",
    }
    (index_dir / "index_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest

def retrieve(question: str, chunks: list, vectors, model, top_k: int, domain: str | None = None):
    import numpy as np
    if not question.strip():
        raise ValueError("Question cannot be empty")
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    if domain not in (None, "arduino", "logo"):
        raise ValueError("Unknown domain")
    query = normalized(model.encode([QUERY_PREFIX + question], convert_to_numpy=True, show_progress_bar=False))[0]
    if vectors.shape[0] != len(chunks) or query.shape[0] != vectors.shape[1]:
        raise ValueError("Embedding dimension/count mismatch")
    scores = vectors @ query
    eligible = (i for i, c in enumerate(chunks) if domain is None or c["doc_id"] == domain)
    ranked = sorted(eligible, key=lambda i: (-float(scores[i]), chunks[i]["chunk_id"]))[:top_k]
    return [{
        "rank": rank, "chunk_id": chunks[i]["chunk_id"], "doc_id": chunks[i]["doc_id"],
        "page_pdf": chunks[i]["page_pdf"], "score": round(float(scores[i]), 8),
        "text": chunks[i]["text"], "text_sha256": chunks[i]["text_sha256"]
    } for rank, i in enumerate(ranked, 1)]

def query(index_dir: Path, question: str, model, top_k: int, domain: str | None = None):
    import numpy as np
    manifest = json.loads((index_dir / "index_manifest.json").read_text(encoding="utf-8"))
    chunks_file = Path(manifest["chunks_path"])
    if sha256(chunks_file.read_bytes()) != manifest["chunks_sha256"]:
        raise ValueError("Chunks file differs from frozen index")
    vector_file = index_dir / "embeddings.npy"
    if sha256(vector_file.read_bytes()) != manifest["vectors_sha256"]:
        raise ValueError("Embedding matrix differs from frozen index")
    chunks = validate_chunks(chunks_file)
    vectors = np.load(vector_file, allow_pickle=False)
    return retrieve(question, chunks, vectors, model, top_k, domain)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="Generate and freeze dense index")
    b.add_argument("--chunks", type=Path, required=True)
    b.add_argument("--index-dir", type=Path, required=True)
    b.add_argument("--revision", required=True, help="Pinned 40-char HF model commit SHA")
    b.add_argument("--model", default=EMBEDDING_MODEL)
    b.add_argument("--batch-size", type=int, default=32)
    b.add_argument("--device", default="cpu")
    q = sub.add_parser("query", help="Retrieve evidence for a single question")
    q.add_argument("--index-dir", type=Path, required=True)
    q.add_argument("--question", required=True)
    q.add_argument("--top-k", type=int, default=5)
    q.add_argument("--domain", choices=["arduino", "logo"], default=None)
    q.add_argument("--device", default="cpu")
    args = parser.parse_args()
    if args.command == "build":
        frozen_revision(args.revision)
        m = load_model(args.model, args.revision, args.device)
        result = build(args.chunks, args.index_dir, m, args.model, args.revision, args.batch_size)
    else:
        settings = json.loads((args.index_dir / "index_manifest.json").read_text(encoding="utf-8"))
        m = load_model(settings["embedding_model"], settings["embedding_revision"], args.device)
        result = {"question": args.question, "domain_filter": args.domain,
                  "retrieved": query(args.index_dir, args.question, m, args.top_k, args.domain)}
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
