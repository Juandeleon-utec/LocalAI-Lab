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
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-bench-root-password}"
BASE_URL="http://127.0.0.1:$PORT"
START_EPOCH="$(date +%s)"

if [[ -z "${BENCH_EVALUATOR:-}" && "${BENCH_ALLOW_NO_EVALUATOR:-0}" != "1" ]]; then
  echo "ERROR: BENCH_EVALUATOR is required. Set BENCH_ALLOW_NO_EVALUATOR=1 only for an unscored harness smoke test." >&2
  exit 2
fi

run_evaluator() {
  local phase="$1"
  local output="$2"

  if [[ -z "${BENCH_EVALUATOR:-}" ]]; then
    return 0
  fi

  if [[ ! -f "$BENCH_EVALUATOR" ]]; then
    echo "ERROR: BENCH_EVALUATOR does not exist: $BENCH_EVALUATOR" >&2
    return 2
  fi

  local evaluator_cmd=()
  if [[ "$BENCH_EVALUATOR" == *.py ]]; then
    evaluator_cmd=(python3 "$BENCH_EVALUATOR")
  else
    if [[ ! -x "$BENCH_EVALUATOR" ]]; then
      echo "ERROR: BENCH_EVALUATOR is not executable: $BENCH_EVALUATOR" >&2
      return 2
    fi
    evaluator_cmd=("$BENCH_EVALUATOR")
  fi

  "${evaluator_cmd[@]}"     --phase "$phase"     --base-url "$BASE_URL"     --output "$output"     --state "$OUTPUT_DIR/evaluator-state.json"     --compose-file "$SCRIPT_DIR/docker-compose.yml"     --db-name "$DB_NAME"     --db-root-password "$MYSQL_ROOT_PASSWORD"
}

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

if git -C "$CANDIDATE_DIR" rev-parse HEAD >/dev/null 2>&1; then
  echo "candidate_commit=$(git -C "$CANDIDATE_DIR" rev-parse HEAD)" >> "$OUTPUT_DIR/run-info.txt"
fi

if [[ ! -f "$CANDIDATE_DIR/package.json" ]]; then
  echo "ERROR: candidate does not contain package.json" >&2
  exit 1
fi

(
  cd "$SCRIPT_DIR"
  DB_HOST_PORT="$DB_HOST_PORT"   DB_NAME="$DB_NAME"   DB_USER="$DB_USER"   DB_PASSWORD="$DB_PASSWORD"   MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD"   ./start-database.sh
)

"$SCRIPT_DIR/capture-environment.sh" "$OUTPUT_DIR/environment-snapshot.txt" > "$OUTPUT_DIR/environment-sha256.txt"

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
  run_evaluator "pre-restart" "$OUTPUT_DIR/evaluator-pre.json"
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
  run_evaluator "post-restart" "$OUTPUT_DIR/evaluator-post.json"
  POST_RC=$?
  set -e

  echo "evaluator_post_exit=$POST_RC" >> "$OUTPUT_DIR/run-info.txt"

  if [[ -f "$OUTPUT_DIR/evaluator-pre.json" && -f "$OUTPUT_DIR/evaluator-post.json" ]]; then
    python3 "$SCRIPT_DIR/aggregate-evaluation.py"       --pre "$OUTPUT_DIR/evaluator-pre.json"       --post "$OUTPUT_DIR/evaluator-post.json"       --output "$OUTPUT_DIR/evaluation.json"
  fi
fi

END_EPOCH="$(date +%s)"
echo "ended_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUTPUT_DIR/run-info.txt"
echo "wall_time_seconds=$((END_EPOCH - START_EPOCH))" >> "$OUTPUT_DIR/run-info.txt"

if (( PRE_RC != 0 || POST_RC != 0 )); then
  exit 1
fi
