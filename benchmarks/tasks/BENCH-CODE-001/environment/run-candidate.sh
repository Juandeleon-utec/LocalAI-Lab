#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <candidate-directory> <output-directory>" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CANDIDATE_DIR="$(cd "$1" && pwd)"
OUTPUT_DIR="$(mkdir -p "$2" && cd "$2" && pwd)"

PORT="${PORT:-3000}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_HOST_PORT="${DB_HOST_PORT:-3307}"
DB_NAME="${DB_NAME:-bench_code_001}"
DB_USER="${DB_USER:-bench_user}"
DB_PASSWORD="${DB_PASSWORD:-bench_password}"
AUTH_SECRET="${AUTH_SECRET:-bench-code-001-local-secret}"
BASE_URL="http://127.0.0.1:$PORT"

APP_PID=""

stop_app() {
  if [[ -n "$APP_PID" ]] && kill -0 "$APP_PID" 2>/dev/null; then
    kill -- "-$APP_PID" 2>/dev/null || kill "$APP_PID" 2>/dev/null || true
    wait "$APP_PID" 2>/dev/null || true
  fi
  APP_PID=""
}

cleanup() {
  stop_app
  (
    cd "$SCRIPT_DIR"
    docker compose logs mysql > "$OUTPUT_DIR/mysql.log" 2>&1 || true
    docker compose down --remove-orphans >/dev/null 2>&1 || true
  )
}

trap cleanup EXIT INT TERM

start_app() {
  (
    cd "$CANDIDATE_DIR"
    exec setsid env       PORT="$PORT"       DB_HOST="$DB_HOST"       DB_PORT="$DB_HOST_PORT"       DB_NAME="$DB_NAME"       DB_USER="$DB_USER"       DB_PASSWORD="$DB_PASSWORD"       AUTH_SECRET="$AUTH_SECRET"       npm start
  ) >> "$OUTPUT_DIR/app.log" 2>&1 &
  APP_PID=$!
  echo "$APP_PID" > "$OUTPUT_DIR/app.pid"
}

echo "candidate_dir=$CANDIDATE_DIR" > "$OUTPUT_DIR/run-info.txt"
echo "started_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUTPUT_DIR/run-info.txt"

if [[ ! -f "$CANDIDATE_DIR/package.json" ]]; then
  echo "ERROR: candidate does not contain package.json" >&2
  exit 1
fi

(
  cd "$SCRIPT_DIR"
  DB_HOST_PORT="$DB_HOST_PORT"   DB_NAME="$DB_NAME"   DB_USER="$DB_USER"   DB_PASSWORD="$DB_PASSWORD"   ./start-database.sh
)

cd "$CANDIDATE_DIR"

if [[ -f package-lock.json ]]; then
  npm ci 2>&1 | tee "$OUTPUT_DIR/npm-install.log"
  echo "install_command=npm ci" >> "$OUTPUT_DIR/run-info.txt"
else
  npm install 2>&1 | tee "$OUTPUT_DIR/npm-install.log"
  echo "install_command=npm install" >> "$OUTPUT_DIR/run-info.txt"
fi

env   PORT="$PORT"   DB_HOST="$DB_HOST"   DB_PORT="$DB_HOST_PORT"   DB_NAME="$DB_NAME"   DB_USER="$DB_USER"   DB_PASSWORD="$DB_PASSWORD"   AUTH_SECRET="$AUTH_SECRET"   npm run db:init 2>&1 | tee "$OUTPUT_DIR/db-init.log"

start_app
"$SCRIPT_DIR/wait-health.sh" "$BASE_URL" 90

PRE_RC=0
POST_RC=0

if [[ -n "${BENCH_EVALUATOR:-}" ]]; then
  set +e
  "$BENCH_EVALUATOR"     --phase pre-restart     --base-url "$BASE_URL"     --output "$OUTPUT_DIR/evaluator-pre.json"
  PRE_RC=$?
  set -e

  echo "evaluator_pre_exit=$PRE_RC" >> "$OUTPUT_DIR/run-info.txt"
fi

stop_app
sleep 2
start_app
"$SCRIPT_DIR/wait-health.sh" "$BASE_URL" 90

if [[ -n "${BENCH_EVALUATOR:-}" ]]; then
  set +e
  "$BENCH_EVALUATOR"     --phase post-restart     --base-url "$BASE_URL"     --output "$OUTPUT_DIR/evaluator-post.json"
  POST_RC=$?
  set -e

  echo "evaluator_post_exit=$POST_RC" >> "$OUTPUT_DIR/run-info.txt"
fi

echo "ended_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUTPUT_DIR/run-info.txt"

if (( PRE_RC != 0 || POST_RC != 0 )); then
  exit 1
fi
