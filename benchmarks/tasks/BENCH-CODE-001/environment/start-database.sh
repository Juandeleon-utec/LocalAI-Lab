#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

docker compose down --remove-orphans >/dev/null 2>&1 || true
docker compose up -d mysql

cid="$(docker compose ps -q mysql)"
if [[ -z "$cid" ]]; then
  echo "ERROR: MySQL container was not created." >&2
  exit 1
fi

echo "Waiting for BENCH-CODE-001 MySQL..."
for _ in $(seq 1 60); do
  status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid")"
  if [[ "$status" == "healthy" ]]; then
    echo "MySQL is healthy."
    exit 0
  fi
  if [[ "$status" == "unhealthy" ]]; then
    docker compose logs mysql
    echo "ERROR: MySQL became unhealthy." >&2
    exit 1
  fi
  sleep 2
done

docker compose logs mysql
echo "ERROR: Timed out waiting for MySQL health." >&2
exit 1
