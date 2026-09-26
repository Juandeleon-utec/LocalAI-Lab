# BENCH-CODE-001 v1.0 — Formal Staging Freeze

Status: **FINAL — frozen before the first formal BENCH-CODE-001 v1.0 run**

This document records the benchmark/staging inputs that must remain unchanged across all formal BENCH-CODE-001 v1.0 runs after the freeze is finalized.

## Repository

- LocalAI-Lab baseline commit: `1a8b47e4c3c1fc062eedbff43b27377d47f9ba7f`

## Participant prompt

- File: `benchmarks/tasks/BENCH-CODE-001/prompt.md`
- SHA-256:

```text
e1ec6e63a2a603a4d5591158a262d66de1f838a93e72d03ae2a158827e35dbac
```

## Hidden evaluator

Engineering-validation archive SHA-256:

```text
edb663ba732cd54ad3ce6cae34e73d1a351ed8afe4bcf58209dd60e46aede670
```

The evaluator remains external to participant workspaces.

## Reference candidate

Engineering-validation archive SHA-256:

```text
452d8deae6fa04b83b1356850db265105e5fa5ee94bfa4471deff5dc93d3d5cf
```

The reference candidate is used only to validate the benchmark instrument.

## Reference-validation result

Observed on 2026-09-26:

- pre-restart: 15 / 15 total PASS;
- pre-restart critical: 13 / 13 PASS;
- post-restart persistence: 1 / 1 PASS;
- post-restart critical: 1 / 1 PASS;
- aggregate: 16 / 16 total PASS;
- aggregate: 14 / 14 critical PASS.

## Formal staging host candidate

Windows workstation:

- OS: Microsoft Windows 11 Pro;
- Windows version: 10.0.26200;
- Windows build: 26200;
- CPU: AMD Ryzen 7 5700G with Radeon Graphics;
- physical CPU cores: 8;
- logical processors: 16;
- physical memory reported: 34,240,933,888 bytes;
- NVIDIA GPU: GeForce GTX 1050 4 GB (not used by BENCH-CODE-001 candidate execution).

Docker Desktop currently exposes:

- architecture: x86_64;
- CPUs: 16;
- memory: approximately 15.56 GiB;
- backend kernel: WSL2 Linux;
- Docker Desktop runtime remains part of the staging configuration and must not be materially changed between formal runs.

## Runtime

- Node.js: `v24.19.0`;
- npm: `11.17.0`;
- Python: `3.11.9`;
- Docker: `29.8.0`, build `88096ef`;
- Docker Compose: `v5.5.1`.

## MySQL

Configured image tag:

```text
mysql:8.4
```

Resolved immutable image digest:

```text
mysql@sha256:0744ee5ef89ce6ccfa13de3e579fe6b9e27f93dd70da9c06d2c908b1b193fb8d
```

Formal runs must resolve to this digest. If the moving `mysql:8.4` tag changes, the harness must pin this digest explicitly before continuing formal comparisons.

## Environment snapshot

Reference-validation snapshot timestamp:

```text
2026-09-26T23:00:49Z
```

Environment snapshot SHA-256:

```text
7c3b89e3ad1b2093c1450edbf4843cfbbdd8134691a6ce0f9497cdb0470fa3a3
```

This is the SHA-256 of the reference-validation `environment-snapshot.txt` generated on 2026-09-26 before C001-A01.

## Freeze rule

After this document is finalized, do not materially change any of the following between C001-A01 and the remaining BENCH-CODE-001 v1.0 formal runs:

- participant prompt;
- hidden evaluator;
- public harness;
- Windows staging host;
- Windows build;
- Node.js/npm runtime;
- Python runtime used by evaluator;
- Docker/Desktop runtime;
- Docker resource allocation;
- MySQL image digest;
- benchmark environment variables/contract.

A material change after C001-A01 requires either rerunning all affected candidates from the beginning or declaring a new benchmark environment revision.

## Formal run order

1. C001-A01 / A02 / A03 — OpenCode + Qwen3-Coder-30B-A3B-Instruct Q3_K_M, context 32768;
2. C001-B01 / B02 / B03 — OpenCode + Qwen3.6-35B-A3B Q4_K_M, context 32768;
3. C001-C01 / C02 / C03 — Claude Code, provider-native supported/default configuration;
4. C001-D — Qwen3.6-35B-A3B Q4_K_M + MTP efficiency experiment.

The reference candidate is not part of these comparative results.
