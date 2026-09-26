# BENCH-CODE-001 v1.0 — Benchmark/Staging Environment

## Purpose

Every generated candidate must be deployed and evaluated on the same controlled server environment after generation.

This is a staging/benchmark environment, not a public production service.

The current Windows development workstation (Ryzen 7 5700G, 32 GB RAM, GTX 1050 4 GB) is technically sufficient to run Node.js/MySQL candidate applications, but it is not automatically designated as the formal staging host. The staging host must be selected and frozen before formal runs.

## Initial runtime baseline

For the v1.0 engineering phase, use:

- one fixed x86-64 staging host for all formal runs (Windows or Linux);
- Docker/OCI-compatible container runtime;
- Node.js 24 LTS family for candidate execution;
- MySQL 8.4 LTS family;
- one fresh MySQL database per candidate run.

At protocol-freeze time, record the exact Node.js point release, MySQL point release and container-image digests.

As of 2026-09-26, Node.js 24 is an LTS release line and MySQL 8.4 is an LTS line. The formal run manifest must preserve the exact versions actually used.

## Environment contract

Provide candidate applications with:

```text
PORT
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
AUTH_SECRET
```

Use benchmark-only credentials.

## Isolation requirements

Each candidate run receives:

- a clean candidate repository checkout;
- a dedicated database/schema;
- no data from a previous run;
- identical CPU and RAM limits where container controls are used;
- identical network policy;
- identical runtime versions.

The candidate application must never share a live database with another candidate.

## Candidate deployment sequence

1. create/reset the run-specific database;
2. check out the frozen candidate commit;
3. execute `npm install` or `npm ci` when a lockfile is present;
4. execute `npm run db:init`;
5. execute `npm start`;
6. wait for `GET /health`;
7. run the external hidden evaluator;
8. restart the application for persistence checks;
9. preserve application, MySQL and evaluator logs;
10. stop and remove run-specific resources.

## Version pinning

Do not rely on moving tags such as `latest` for formal runs.

Before the first formal execution:

- pin the exact Node.js container image or digest;
- pin the exact MySQL container image or digest;
- checksum the environment/harness configuration;
- record Docker/container-runtime version and host OS/kernel.

## Access

Human review may expose candidate applications on a controlled LAN port or reverse proxy.

Do not expose BENCH-CODE-001 candidates directly to the public Internet.


## Public harness

The repository includes both Windows/PowerShell and Bash variants where operating-system-specific orchestration is required.

Windows staging uses:

- `preflight.ps1`;
- `start-database.ps1` / `stop-database.ps1`;
- `wait-health.ps1`;
- `capture-environment.ps1`;
- `run-candidate.ps1`.

Linux/Bash staging uses the corresponding `.sh` helpers.

Shared files:

- `docker-compose.yml` — ephemeral MySQL service;
- `aggregate-evaluation.py` — combines pre/post evaluator phases into one result;
- `reference-validation.env.example` — benchmark-only environment example;
- `VALIDATION.md` — reference-validation and freeze procedure.

The exact hidden evaluator is deliberately external. Set `BENCH_EVALUATOR` to its path when running a scored candidate. Python evaluator files are invoked through `python3`, so executable file permissions are not required.

By default, `run-candidate.sh` refuses to run without an evaluator. `BENCH_ALLOW_NO_EVALUATOR=1` exists only for an explicitly unscored harness smoke test.
