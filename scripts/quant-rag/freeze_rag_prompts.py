#!/usr/bin/env python3
"""Freeze and audit the exact 50 global RAG prompts before the Qwen benchmark.

No LLM is called. Never reads ground-truth answers. Fails on altered retrieval,
duplicate questions, missing passages or invalid text hashes. Saves prompt JSONL
and a manifest for all six model variants and three repetitions to reuse.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/srv/data/quant-rag")
SYS = (
    "Eres un asistente técnico que responde consultas sobre los manuales facilitados. "
    "Responde únicamente a partir de los fragmentos documentales proporcionados. "
    "Si la evidencia no es suficiente, indícalo explícitamente sin inventar datos. "
    "Responde en español, de forma precisa. "
    "Al fundamentar afirmaciones, cita las fuentes usando [arduino p.N] o [logo p.N] "
    "según el documento y número de página PDF indicados."
)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical(data: dict) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", type=Path, default=BASE)
    p.add_argument("--output-dir", type=Path)
    args = p.parse_args()
    base = args.base.resolve()
    path = base / "retrieval-v1" / "frozen_contexts.jsonl"
    manifest_path = base / "retrieval-v1" / "retrieval_manifest.json"
    meta = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = sha(path.read_bytes())
    if actual != meta["frozen_contexts_sha256"]:
        raise ValueError("Frozen context file SHA-256 differs from retrieval manifest")
    selected = []
    seen = set()
    policy_count = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        policy_count[row["policy"]] += 1
        existing_hash = row["context_sha256"]
        clean_row = {k: v for k, v in row.items() if k != "context_sha256"}
        if sha(canonical(clean_row)) != existing_hash:
            raise ValueError(f"Context hash mismatch: {row['question_id']}")
        if row["policy"] != "global":
            continue
        question_id = row["question_id"]
        if question_id in seen:
            raise ValueError(f"Repeated question id: {question_id}")
        seen.add(question_id)
        retrieved = row["retrieved"]
        if len(retrieved) != 5:
            raise ValueError(f"Expected five passages for {question_id}: got {len(retrieved)}")
        passages = []
        for number, item in enumerate(retrieved, 1):
            if item["rank"] != number:
                raise ValueError(f"Unexpected rank: {question_id}: {item['rank']}")
            if not isinstance(item["text"], str) or not item["text"].strip():
                raise ValueError(f"Missing text in {question_id}")
            if sha(item["text"].encode("utf-8")) != item["text_sha256"]:
                raise ValueError(f"Passage SHA-256 mismatch: {question_id} {item['chunk_id']}")
            passages.append(f"[{item['doc_id']} p.{item['page_pdf']}; fragmento {item['chunk_id']}]\n{item['text']}")
        user = "FRAGMENTOS DOCUMENTALES:\n\n" + "\n\n".join(passages) + \
            "\n\nPREGUNTA:\n" + row["question"] + "\n\nRESPUESTA:"
        messages = [{"role": "system", "content": SYS},
                    {"role": "user", "content": user}]
        selected.append({
            "question_id": question_id, "domain": row["domain"],
            "context_sha256": existing_hash,
            "retrieved_chunk_ids": [i["chunk_id"] for i in retrieved],
            "messages": messages, "prompt_sha256": sha(canonical({"messages": messages})),
        })
    if policy_count != {"global": 50, "domain": 50}:
        raise ValueError(f"Unexpected policy counts: {dict(policy_count)}")
    if len(selected) != 50 or Counter(x["domain"] for x in selected) != {"arduino":20, "logo":30}:
        raise ValueError("Unexpected question counts")
    out = (args.output_dir or base / "prompts-v1").resolve()
    if out.exists():
        raise FileExistsError(f"Frozen output already exists; do not overwrite: {out}")
    out.mkdir(parents=True)
    output_file = out / "rag_prompts_global.jsonl"
    with output_file.open("w", encoding="utf-8") as f:
        for row in selected:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    manifest = {
        "benchmark": "BENCH-QUANT-RAG-001",
        "prompt_version": "rag-prompt-v1",
        "retrieval_policy": "global", "top_k": 5,
        "source_frozen_contexts_sha256": actual,
        "retrieval_manifest_sha256": sha(manifest_path.read_bytes()),
        "prompt_file_sha256": sha(output_file.read_bytes()),
        "system_prompt_sha256": sha(SYS.encode("utf-8")),
        "questions": len(selected),
        "question_ids": [x["question_id"] for x in selected],
        "variants": ["F16", "Q8_0", "Q6_K", "Q4_K_M", "Q3_K_M", "Q2_K"],
        "repetitions": 3, "planned_completions": 900,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "gold_answers_used": False,
    }
    (out / "prompt_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "prompts": len(selected),
                      "prompt_file_sha256": manifest["prompt_file_sha256"],
                      "planned_completions": 900}, indent=2))

if __name__ == "__main__":
    main()
