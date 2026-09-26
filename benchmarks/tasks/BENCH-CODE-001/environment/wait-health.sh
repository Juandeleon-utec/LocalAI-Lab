#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:3000}"
TIMEOUT_SECONDS="${2:-60}"

deadline=$((SECONDS + TIMEOUT_SECONDS))

while (( SECONDS < deadline )); do
  body="$(curl -fsS --max-time 2 "$BASE_URL/health" 2>/dev/null || true)"
  if [[ "$body" == *'"status"'* && "$body" == *'"ok"'* ]]; then
    echo "Candidate is healthy at $BASE_URL"
    exit 0
  fi
  sleep 1
done

echo "ERROR: Candidate did not become healthy within ${TIMEOUT_SECONDS}s: $BASE_URL/health" >&2
exit 1
