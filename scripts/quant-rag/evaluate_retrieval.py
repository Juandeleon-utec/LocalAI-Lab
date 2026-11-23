#!/usr/bin/env python3
"""Evaluate retrieval quality for the 50-question RAG benchmark.

Two retrieval policies are evaluated with the SAME frozen E5 index:
  global: search across both manuals
  domain: restrict to the question's known document (without using gold pages)

The answer key is used ONLY after retrieval, to calculate reference-page metrics.
Frozen contexts contain questions and passages, NEVER reference answers or gold pages.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from vector_index import load_model, query, sha256

DOMAINS = {"arduino", "logo"}
EXPECTED = {"arduino": 20, "logo": 30}
POLICIES = ("global", "domain")


def validate_questions(path: Path, strict_count: bool = True) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise ValueError("Question dataset must be a JSON array")
    counts = defaultdict(int)
    seen = set()
    for position, entry in enumerate(data, 1):
        for field in ("id", "dominio", "pregunta", "paginas_pdf"):
            if field not in entry:
                raise ValueError(f"Question {position} missing {field}")
        ident, domain, question = entry["id"], entry["dominio"], entry["pregunta"]
        if not isinstance(ident, str) or not ident.strip() or ident in seen:
            raise ValueError(f"Duplicate or invalid question ID: {ident}")
        seen.add(ident)
        if domain not in DOMAINS:
            raise ValueError(f"Unknown domain at {ident}: {domain}")
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"Empty question {ident}")
        pages = entry["paginas_pdf"]
        if not isinstance(pages, list) or not pages or any(type(p) is not int or p <= 0 for p in pages):
            raise ValueError(f"Invalid PDF reference pages {ident}")
        counts[domain] += 1
    if strict_count and dict(counts) != EXPECTED:
        raise ValueError(f"Expected {EXPECTED} questions, got {dict(counts)}")
    return data


def page_metrics(retrieved: list[dict], gold_pages: list[int], expected_domain: str) -> dict:
    gold = set(gold_pages)
    matched_ranks = [item["rank"] for item in retrieved if item["doc_id"] == expected_domain and item["page_pdf"] in gold]
    unique_pages = {item["page_pdf"] for item in retrieved if item["doc_id"] == expected_domain}
    return {
        "hit_at_k": int(bool(matched_ranks)),
        "first_relevant_rank": min(matched_ranks) if matched_ranks else None,
        "reciprocal_rank": (1 / min(matched_ranks)) if matched_ranks else 0.0,
        "page_recall_at_k": len(gold & unique_pages) / len(gold),
        "reference_pages_count": len(gold),
    }


def summarize(evaluations: list[dict], top_k: int) -> dict:
    result = {}
    for policy in POLICIES:
        subset = [row for row in evaluations if row["policy"] == policy]
        per_group = {}
        for name in ("all", "arduino", "logo"):
            group = subset if name == "all" else [r for r in subset if r["domain"] == name]
            if not group:
                continue
            per_group[name] = {
                "n_questions": len(group),
                f"hit_at_{top_k}": sum(r["hit_at_k"] for r in group) / len(group),
                f"mrr_at_{top_k}": sum(r["reciprocal_rank"] for r in group) / len(group),
                f"mean_page_recall_at_{top_k}": sum(r["page_recall_at_k"] for r in group) / len(group),
            }
        result[policy] = per_group
    return result


def run(questions: list[dict], index_dir: Path, model, top_k: int):
    """Yield separate evaluation rows and contexts; contexts exclude ground truth."""
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    evaluations = []
    contexts = []
    for entry in questions:
        for policy in POLICIES:
            filter_domain = entry["dominio"] if policy == "domain" else None
            passages = query(index_dir, entry["pregunta"], model, top_k, domain=filter_domain)
            metrics = page_metrics(passages, entry["paginas_pdf"], entry["dominio"])
            evaluations.append({
                "question_id": entry["id"],
                "domain": entry["dominio"],
                "policy": policy,
                "top_k": top_k,
                **metrics,
                "retrieved_chunk_ids": [p["chunk_id"] for p in passages],
                "retrieved_pages": [p["page_pdf"] for p in passages],
            })
            # Do not include answer / gold page / labels in the inference context.
            clean_passages = [{
                "rank": p["rank"],
                "chunk_id": p["chunk_id"],
                "doc_id": p["doc_id"],
                "page_pdf": p["page_pdf"],
                "score": p["score"],
                "text": p["text"],
                "text_sha256": p["text_sha256"],
            } for p in passages]
            context = {
                "question_id": entry["id"],
                "domain": entry["dominio"],
                "policy": policy,
                "question": entry["pregunta"],
                "retrieved": clean_passages,
            }
            encoded = json.dumps(context, ensure_ascii=False, sort_keys=True).encode("utf-8")
            context["context_sha256"] = sha256(encoded)
            contexts.append(context)
    return evaluations, contexts


def save_outputs(output_dir: Path, evaluations: list[dict], contexts: list[dict], summary: dict,
                 dataset_sha: str, index_manifest_sha: str, top_k: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    # Gold-dependent evaluation is stored separately from answer-free inference contexts.
    for filename, records in (("retrieval_evaluation.jsonl", evaluations),
                              ("frozen_contexts.jsonl", contexts)):
        content = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records)
        (output_dir / filename).write_text(content, encoding="utf-8")
    manifest = {
        "benchmark": "BENCH-QUANT-RAG-001", "retrieval_version": 1,
        "dataset_sha256": dataset_sha,
        "index_manifest_sha256": index_manifest_sha,
        "questions_count": len(contexts) // len(POLICIES),
        "policies": list(POLICIES), "top_k": top_k,
        "metrics": summary,
        "frozen_contexts_sha256": sha256((output_dir / "frozen_contexts.jsonl").read_bytes()),
        "retrieval_evaluation_sha256": sha256((output_dir / "retrieval_evaluation.jsonl").read_bytes()),
    }
    (output_dir / "retrieval_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, required=True, help="Reference JSON kept outside corpus/index")
    parser.add_argument("--index-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    questions = validate_questions(args.questions)
    index_manifest_file = args.index_dir / "index_manifest.json"
    manifest = json.loads(index_manifest_file.read_text(encoding="utf-8"))
    model = load_model(manifest["embedding_model"], manifest["embedding_revision"], args.device)
    evaluations, contexts = run(questions, args.index_dir, model, args.top_k)
    summary = summarize(evaluations, args.top_k)
    save_outputs(args.output_dir, evaluations, contexts, summary,
                 sha256(args.questions.read_bytes()), sha256(index_manifest_file.read_bytes()), args.top_k)
    print(json.dumps({
        "questions": len(questions),
        "retrievals": len(evaluations),
        "index_model": manifest["embedding_model"],
        "top_k": args.top_k,
        "summary": summary,
        "outputs": str(args.output_dir),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
