#!/usr/bin/env bash
set -euo pipefail

required=(bash docker curl node npm python3 sha256sum setsid)

missing=0
for cmd in "${required[@]}"; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "MISSING: $cmd"
    missing=1
  else
    echo "FOUND:   $cmd -> $(command -v "$cmd")"
  fi
done

if (( missing != 0 )); then
  echo
  echo "Preflight FAILED: required commands are missing." >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "MISSING: docker compose plugin" >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker daemon is not available to this shell." >&2
  exit 1
fi

echo
echo "## Versions"
echo "bash:    $BASH_VERSION"
echo "node:    $(node --version)"
echo "npm:     $(npm --version)"
echo "python:  $(python3 --version 2>&1)"
echo "docker:  $(docker --version)"
echo "compose: $(docker compose version)"

echo
echo "Preflight PASS"
