#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-environment-snapshot.txt}"

{
  echo "timestamp_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "## uname"
  uname -a || true
  echo
  echo "## os-release"
  cat /etc/os-release 2>/dev/null || true
  echo
  echo "## cpu"
  lscpu 2>/dev/null || true
  echo
  echo "## memory"
  free -h 2>/dev/null || true
  echo
  echo "## node"
  node --version 2>/dev/null || true
  echo
  echo "## npm"
  npm --version 2>/dev/null || true
  echo
  echo "## docker"
  docker version 2>/dev/null || true
  echo
  echo "## docker compose"
  docker compose version 2>/dev/null || true
  echo
  echo "## mysql image"
  docker image inspect "${MYSQL_IMAGE:-mysql:8.4}" --format '{{json .RepoDigests}}' 2>/dev/null || true
} > "$OUT"

sha256sum "$OUT"
