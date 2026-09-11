#!/usr/bin/env python3
"""Run the Academic Screening LLM-only baseline (A001).

The script reads the frozen screening dataset, renders the versioned screening
prompt for each paper, calls an OpenAI-compatible local llama-server endpoint,
validates the returned JSON, and writes reproducible per-paper predictions,
raw responses, timing/token telemetry, and a run manifest.

No RAG, embeddings, reranking, OCR, or external network access are used.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DATASET = Path(
    "/srv/data/benchmarks/academic-rag/datasets/academic-screening-v0.1/papers-v0.1.csv"
)
DEFAULT_PROMPT = Path("prompts/academic-screening-v0.1.txt")
DEFAULT_RUNS_ROOT = Path("/srv/data/benchmarks/academic-rag/runs")

LABELS = {
    0: "NOT_RELEVANT",
    1: "TANGENTIAL",
    2: "RELEVANT",
    3: "HIGHLY_RELEVANT",
}
READING_DECISIONS = {"READ_FULL", "READ_SECTIONS", "REFERENCE_ONLY", "DISCARD"}
EVIDENCE_LEVELS = {"SUFFICIENT", "PARTIAL", "INSUFFICIENT"}
DIMENSIONS = (
    "topic_match",
    "methodology_match",
    "hardware_or_sensor_match",
    "dataset_match",
    "edge_ai_relevance",
    "machine_learning_method_match",
    "experimental_design_value",
    "state_of_the_art_value",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"Dataset is empty: {path}")
    return rows


def load_text(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"Required file does not exist: {path}")
    return path.read_text(encoding="utf-8")


def render_prompt(template: str, objective: str, row: dict[str, str]) -> str:
    values = {
        "research_objective": objective.strip(),
        "paper_id": row.get("paper_id", "").strip(),
        "title": row.get("title", "").strip(),
        "authors": row.get("authors", "").strip(),
        "year": row.get("year", "").strip(),
        "doi": row.get("doi", "").strip(),
        "abstract": row.get("abstract", "").strip(),
        "keywords": row.get("keywords", "").strip(),
        "evidence": "",
    }
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("response does not contain a JSON object")
    value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("response JSON is not an object")
    return value


def validate_prediction(obj: dict[str, Any], expected_paper_id: str) -> list[str]:
    errors: list[str] = []
    paper_id = str(obj.get("paper_id", "")).strip()
    if paper_id != expected_paper_id:
        errors.append(f"paper_id mismatch: {paper_id!r}")

    relevance = obj.get("relevance_class")
    if not isinstance(relevance, int) or relevance not in LABELS:
        errors.append("relevance_class must be integer 0..3")
    elif obj.get("relevance_label") != LABELS[relevance]:
        errors.append("relevance_label does not match relevance_class")

    if obj.get("reading_decision") not in READING_DECISIONS:
        errors.append("invalid reading_decision")

    confidence = obj.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= float(confidence) <= 1:
        errors.append("confidence must be 0.0..1.0")

    if obj.get("evidence_sufficiency") not in EVIDENCE_LEVELS:
        errors.append("invalid evidence_sufficiency")

    dims = obj.get("relevance_dimensions")
    if not isinstance(dims, dict):
        errors.append("relevance_dimensions must be an object")
    else:
        for name in DIMENSIONS:
            value = dims.get(name)
            if not isinstance(value, int) or value not in {0, 1, 2, 3}:
                errors.append(f"invalid dimension: {name}")

    if not isinstance(obj.get("key_topics"), list):
        errors.append("key_topics must be a list")
    if not isinstance(obj.get("recommended_sections"), list):
        errors.append("recommended_sections must be a list")
    if not isinstance(obj.get("rationale"), str):
        errors.append("rationale must be a string")
    return errors


def post_chat(
    url: str,
    api_key: str,
    model: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    timeout_s: float,
    seed: int | None,
) -> tuple[dict[str, Any], float]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if seed is not None:
        payload["seed"] = seed

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    elapsed = time.perf_counter() - start
    parsed = json.loads(body)
    return parsed, elapsed


def response_content(response: dict[str, Any]) -> str:
    try:
        return str(response["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("OpenAI response missing choices[0].message.content") from exc


def usage_value(response: dict[str, Any], name: str) -> int | None:
    value = (response.get("usage") or {}).get(name)
    return int(value) if isinstance(value, (int, float)) else None


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def prediction_row(
    paper: dict[str, str],
    prediction: dict[str, Any] | None,
    status: str,
    validation_errors: list[str],
    elapsed_s: float,
    response: dict[str, Any] | None,
    error: str,
) -> dict[str, Any]:
    pred = prediction or {}
    dims = pred.get("relevance_dimensions") if isinstance(pred.get("relevance_dimensions"), dict) else {}
    return {
        "paper_id": paper.get("paper_id", ""),
        "title": paper.get("title", ""),
        "status": status,
        "relevance_class": pred.get("relevance_class", ""),
        "relevance_label": pred.get("relevance_label", ""),
        "reading_decision": pred.get("reading_decision", ""),
        "confidence": pred.get("confidence", ""),
        "evidence_sufficiency": pred.get("evidence_sufficiency", ""),
        **{name: dims.get(name, "") for name in DIMENSIONS},
        "key_topics": json.dumps(pred.get("key_topics", []), ensure_ascii=False),
        "recommended_sections": json.dumps(pred.get("recommended_sections", []), ensure_ascii=False),
        "rationale": pred.get("rationale", ""),
        "latency_s": round(elapsed_s, 6),
        "prompt_tokens": usage_value(response or {}, "prompt_tokens") or "",
        "completion_tokens": usage_value(response or {}, "completion_tokens") or "",
        "total_tokens": usage_value(response or {}, "total_tokens") or "",
        "validation_errors": "; ".join(validation_errors),
        "error": error,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Academic Screening baseline A001 against a local OpenAI-compatible endpoint.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    objective = parser.add_mutually_exclusive_group(required=True)
    objective.add_argument("--research-objective")
    objective.add_argument("--research-objective-file", type=Path)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    parser.add_argument("--api-key", default=os.environ.get("LOCALAI_API_KEY", "localai-dev-key"))
    parser.add_argument("--model", default="qwen3-coder")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run-id", default="A001")
    parser.add_argument("--runs-root", type=Path, default=DEFAULT_RUNS_ROOT)
    parser.add_argument("--limit", type=int, default=0, help="Optional smoke-test limit; 0 means all papers.")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    if args.research_objective_file:
        research_objective = load_text(args.research_objective_file).strip()
    else:
        research_objective = (args.research_objective or "").strip()
    if not research_objective:
        raise SystemExit("Research objective must not be empty.")

    papers = load_csv(args.dataset)
    if args.limit > 0:
        papers = papers[: args.limit]
    template = load_text(args.prompt)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = args.runs_root / f"{args.run_id}-{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    predictions_path = run_dir / "predictions.csv"
    raw_path = run_dir / "responses.jsonl"
    manifest_path = run_dir / "manifest.json"

    endpoint = args.base_url.rstrip("/") + "/chat/completions"
    results: list[dict[str, Any]] = []
    run_start = time.perf_counter()
    successful = 0

    with raw_path.open("w", encoding="utf-8") as raw_handle:
        for index, paper in enumerate(papers, start=1):
            paper_id = paper.get("paper_id", "").strip()
            prompt = render_prompt(template, research_objective, paper)
            response: dict[str, Any] | None = None
            prediction: dict[str, Any] | None = None
            validation_errors: list[str] = []
            status = "ERROR"
            error = ""
            elapsed = 0.0

            try:
                response, elapsed = post_chat(
                    endpoint,
                    args.api_key,
                    args.model,
                    prompt,
                    args.temperature,
                    args.max_tokens,
                    args.timeout,
                    args.seed,
                )
                content = response_content(response)
                prediction = extract_json_object(content)
                validation_errors = validate_prediction(prediction, paper_id)
                status = "OK" if not validation_errors else "INVALID"
                if status == "OK":
                    successful += 1
            except Exception as exc:  # per-paper isolation is intentional
                error = f"{type(exc).__name__}: {exc}"
                if args.fail_fast:
                    raise

            raw_handle.write(
                json.dumps(
                    {
                        "paper_id": paper_id,
                        "status": status,
                        "latency_s": elapsed,
                        "validation_errors": validation_errors,
                        "error": error,
                        "prediction": prediction,
                        "api_response": response,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            results.append(prediction_row(paper, prediction, status, validation_errors, elapsed, response, error))
            print(f"[{index:03d}/{len(papers):03d}] {paper_id} status={status} time={elapsed:.3f}s")

    write_csv(predictions_path, results)
    wall_time = time.perf_counter() - run_start
    total_prompt_tokens = sum(int(row["prompt_tokens"]) for row in results if str(row["prompt_tokens"]).isdigit())
    total_completion_tokens = sum(int(row["completion_tokens"]) for row in results if str(row["completion_tokens"]).isdigit())
    total_tokens = sum(int(row["total_tokens"]) for row in results if str(row["total_tokens"]).isdigit())

    manifest = {
        "benchmark": "Academic Screening LLM-only baseline",
        "run_id": args.run_id,
        "timestamp_utc": timestamp,
        "papers": len(papers),
        "successful": successful,
        "invalid": sum(row["status"] == "INVALID" for row in results),
        "errors": sum(row["status"] == "ERROR" for row in results),
        "wall_time_s": round(wall_time, 6),
        "papers_per_hour": round((len(papers) / wall_time) * 3600, 3) if wall_time else None,
        "model": args.model,
        "base_url": args.base_url,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "seed": args.seed,
        "research_objective": research_objective,
        "dataset": str(args.dataset),
        "dataset_sha256": sha256_file(args.dataset),
        "prompt": str(args.prompt),
        "prompt_sha256": sha256_file(args.prompt),
        "token_usage": {
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "total_tokens": total_tokens,
        },
        "outputs": {
            "predictions": str(predictions_path),
            "raw_responses": str(raw_path),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("\nAcademic Screening baseline complete")
    print(f"Run: {run_dir}")
    print(f"Papers: {len(papers)}")
    print(f"Successful: {successful}")
    print(f"Invalid: {manifest['invalid']}")
    print(f"Errors: {manifest['errors']}")
    print(f"Wall time: {wall_time:.3f}s")
    print(f"Predictions: {predictions_path}")
    print(f"Raw responses: {raw_path}")
    print(f"Manifest: {manifest_path}")

    if successful != len(papers):
        sys.exit(2)


if __name__ == "__main__":
    main()
