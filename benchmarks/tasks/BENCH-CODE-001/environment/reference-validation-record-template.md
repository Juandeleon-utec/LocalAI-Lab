# BENCH-CODE-001 Reference Validation Record

**Purpose:** validate the benchmark instrument before any model comparison.

## Identity

- Date/time UTC:
- LocalAI-Lab commit:
- Validation host:
- Host role: engineering validation / formal staging
- Operator:

## Frozen artifacts

- Prompt SHA-256:
- Hidden evaluator SHA-256:
- Reference candidate SHA-256:
- Environment snapshot SHA-256:

## Runtime

- OS:
- Kernel:
- CPU:
- RAM:
- Node.js:
- npm:
- Docker:
- Docker Compose:
- MySQL image:
- MySQL image digest:

## Preflight

- `preflight.sh`: PASS / FAIL
- MySQL clean start #1: PASS / FAIL
- MySQL clean stop: PASS / FAIL
- MySQL clean start #2: PASS / FAIL

## Reference candidate

- `npm ci` / `npm install`: PASS / FAIL
- `npm run db:init`: PASS / FAIL
- `npm start`: PASS / FAIL
- `GET /health`: PASS / FAIL
- restart without DB reset: PASS / FAIL

## Evaluator

- pre-restart evaluator exit:
- post-restart evaluator exit:
- tests passed / total:
- critical tests passed / total:
- all tests passed:
- all critical tests passed:

Expected for reference validation:

```text
16 / 16 total
14 / 14 critical
```

## Artifacts retained

- `run-info.txt`
- `environment-snapshot.txt`
- `environment-sha256.txt`
- `npm-install.log`
- `db-init.log`
- `app.log`
- `mysql.log`
- `evaluator-pre.json`
- `evaluator-post.json`
- `evaluator-state.json`
- `evaluation.json`

## Decision

- [ ] Harness validated for engineering use.
- [ ] Environment frozen for formal BENCH-CODE-001 v1.0 runs.
- [ ] Not ready; corrective action required.

Notes:
