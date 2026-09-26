#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pre", required=True)
    parser.add_argument("--post", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    pre = load(args.pre)
    post = load(args.post)

    tests = list(pre.get("tests", [])) + list(post.get("tests", []))
    tests.sort(key=lambda x: int(str(x.get("id", "T0")).lstrip("T") or 0))

    critical = [t for t in tests if t.get("critical") is True]
    passed = [t for t in tests if t.get("passed") is True]
    critical_passed = [t for t in critical if t.get("passed") is True]

    result = {
        "benchmark": "BENCH-CODE-001",
        "benchmark_version": "1.0",
        "evaluator_version": pre.get("evaluator_version") or post.get("evaluator_version"),
        "tests": tests,
        "summary": {
            "tests_passed": len(passed),
            "tests_total": len(tests),
            "critical_tests_passed": len(critical_passed),
            "critical_tests_total": len(critical),
            "all_tests_passed": len(passed) == len(tests),
            "all_critical_tests_passed": len(critical_passed) == len(critical),
        },
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(result["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
