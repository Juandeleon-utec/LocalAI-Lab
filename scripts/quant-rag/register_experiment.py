#!/usr/bin/env python3
"""Produce reproducible SHA-256 manifests and CSV registers for BENCH-QUANT-RAG-001.

Only metadata, hashes and evaluation metrics are exported. Never exports gold answers,
question texts or retrieved passage texts into the register. The local source files
stay outside Git. An expected model hash mismatch is a hard error.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/srv/data/quant-rag")
MODEL_PREFIX = "Qwen3-4B-Instruct-2507-"
MODEL_ORDER = ("F16", "Q8_0", "Q6_K", "Q4_K_M", "Q3_K_M", "Q2_K")
MODEL_SHA256 = {
    "F16": "336228a2810f17724ecd6e9e2e40e8381eee81e886316fee311ade2899c31030",
    "Q8_0": "391c1e410fd9f4cf2de2b510273b56a84c19ce18f4fa3bfb3774031dac4ef068",
    "Q6_K": "cd7b21b38b3e71400587c184b6a9b04d3beb4d13fdae6464d4075dee4f1bc5ad",
    "Q4_K_M": "3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597",
    "Q3_K_M": "9c6e0763577125a994a9bea0bbd7a737ac4498b8a6a4e0f788727553af1806c9",
    "Q2_K": "f7ed2f57713ad29e1a4ec093be0cdf3d7fd31e137e8fd4fc3edcfd04a5267862",
}
HF_REPO = "unsloth/Qwen3-4B-Instruct-2507-GGUF"
HF_REVISION = "a06e946bb6b655725eafa393f4a9745d460374c9"
BASE_MODEL_REPO = "Qwen/Qwen3-4B-Instruct-2507"
BASE_MODEL_REVISION = "cdbee75f17c01a7cc42f958dc650907174af0554"
FILES = (
    ("manual-arduino", "manuals/Manual+Programacion+Arduino.pdf", True),
    ("manual-logo", "manuals/Logo_s.pdf", True),
    ("source-inventory", "corpus/source_inventory.json", True),
    ("pages", "corpus/pages.jsonl", True),
    ("chunks", "corpus/chunks.jsonl", True),
    ("chunk-manifest", "corpus/chunk_manifest.json", True),
    ("embeddings", "index-e5-small/embeddings.npy", True),
    ("index-manifest", "index-e5-small/index_manifest.json", True),
    ("gold-questions-PRIVATE", "evaluation/questions_gold.json", True),
    ("frozen-contexts", "retrieval-v1/frozen_contexts.jsonl", True),
    ("retrieval-evaluation", "retrieval-v1/retrieval_evaluation.jsonl", True),
    ("retrieval-manifest", "retrieval-v1/retrieval_manifest.json", True),
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def git_head(repo: Path) -> dict:
    data = {}
    for name, cmd in (
        ("commit", ["git", "rev-parse", "HEAD"]),
        ("branch", ["git", "branch", "--show-current"]),
    ):
        try:
            data[name] = subprocess.check_output(cmd, cwd=repo, text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            data[name] = None
    return data


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", type=Path, default=BASE)
    p.add_argument("--output-dir", type=Path)
    p.add_argument("--repo", type=Path, default=Path.home() / "LocalAI-Lab")
    args = p.parse_args()
    base = args.base.resolve()
    output = (args.output_dir or base / "records-v1").resolve()
    if output == base or output == base / "models":
        p.error("Output must be a dedicated record directory")
    output.mkdir(parents=True, exist_ok=True)

    artifacts = []
    missing = []
    for kind, rel, required in FILES:
        path = base / rel
        if not path.is_file():
            if required:
                missing.append(rel)
            continue
        artifacts.append({"category": kind, "path": rel, "size_bytes": path.stat().st_size,
                          "sha256": digest(path)})
    models = []
    mismatches = []
    for quant in MODEL_ORDER:
        filename = f"{MODEL_PREFIX}{quant}.gguf"
        path = base / "models" / "gguf" / filename
        if not path.is_file():
            missing.append("models/gguf/" + filename)
            continue
        actual = digest(path)
        expected = MODEL_SHA256[quant]
        if actual != expected:
            mismatches.append(f"{filename}: {actual} != {expected}")
        models.append({"variant": quant, "filename": filename, "size_bytes": path.stat().st_size,
                       "sha256": actual, "expected_sha256": expected,
                       "sha256_match": actual == expected,
                       "hf_repo": HF_REPO, "hf_revision": HF_REVISION})
        artifacts.append({"category": "model-" + quant, "path": "models/gguf/" + filename,
                          "size_bytes": path.stat().st_size, "sha256": actual})
    if missing or mismatches:
        if missing:
            print("Missing required files:", *missing, sep="\n  ", file=sys.stderr)
        if mismatches:
            print("MODEL SHA256 MISMATCH:", *mismatches, sep="\n  ", file=sys.stderr)
        return 1

    write_csv(output / "artifacts.csv",
              ["category", "path", "size_bytes", "sha256"], artifacts)
    write_csv(output / "models.csv",
              ["variant", "filename", "size_bytes", "sha256", "expected_sha256",
               "sha256_match", "hf_repo", "hf_revision"], models)

    retrieval_rows = []
    path = base / "retrieval-v1" / "retrieval_evaluation.jsonl"
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            retrieval_rows.append({
                "question_id": row["question_id"], "domain": row["domain"],
                "policy": row["policy"], "top_k": row["top_k"],
                "hit_at_k": row["hit_at_k"],
                "first_relevant_rank": row["first_relevant_rank"],
                "reciprocal_rank": row["reciprocal_rank"],
                "page_recall_at_k": row["page_recall_at_k"],
                "retrieved_chunk_ids": ";".join(row["retrieved_chunk_ids"]),
                "retrieved_pages_pdf": ";".join(map(str, row["retrieved_pages"])),
            })
    counts = Counter(row["policy"] for row in retrieval_rows)
    if counts != {"global": 50, "domain": 50}:
        print(f"Unexpected retrieval counts: {dict(counts)}", file=sys.stderr)
        return 1
    write_csv(output / "retrieval_per_question.csv",
              ["question_id", "domain", "policy", "top_k", "hit_at_k",
               "first_relevant_rank", "reciprocal_rank", "page_recall_at_k",
               "retrieved_chunk_ids", "retrieved_pages_pdf"], retrieval_rows)

    manifest = json.loads((base / "retrieval-v1" / "retrieval_manifest.json").read_text(encoding="utf-8"))
    summary_rows = []
    for policy, groups in manifest["metrics"].items():
        for group, values in groups.items():
            summary_rows.append({"policy": policy, "group": group, **values})
    write_csv(output / "retrieval_summary.csv",
              ["policy", "group", "n_questions", "hit_at_5",
               "mrr_at_5", "mean_page_recall_at_5"], summary_rows)

    metadata = {
        "benchmark": "BENCH-QUANT-RAG-001",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "host": platform.node(),
        "git": git_head(args.repo),
        "base_model_repo": BASE_MODEL_REPO,
        "base_model_revision": BASE_MODEL_REVISION,
        "gguf_repo": HF_REPO,
        "gguf_revision": HF_REVISION,
        "llama_cpp_commit_observed": "b96806d96061049a5b574269b049bf6241d63d46",
        "retrieval_policy_primary": "global",
        "top_k": 5,
        "questions": 50,
        "variants": list(MODEL_ORDER),
        "repetitions": 3,
        "planned_answers": 900,
        "retrieval_metrics": manifest["metrics"],
        "artifacts": artifacts,
        "model_hashes_checked_against_user_observed_values": True,
        "important": "Private gold answers and passage text were not exported.",
    }
    (output / "provenance.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "SHA256SUMS.txt").open("w", encoding="utf-8") as handle:
        for row in artifacts:
            handle.write(f'{row["sha256"]}  {row["path"]}\n')
    print(json.dumps({
        "output": str(output),
        "files_hashed": len(artifacts),
        "models_verified": len(models),
        "retrieval_rows": len(retrieval_rows),
        "record_files": ["artifacts.csv", "models.csv", "retrieval_per_question.csv",
                         "retrieval_summary.csv", "provenance.json", "SHA256SUMS.txt"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
