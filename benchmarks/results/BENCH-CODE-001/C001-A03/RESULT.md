# C001-A03 — Formal Result

## Outcome

System:

- OpenCode 1.18.27
- local/qwen3-coder
- Qwen3-Coder-30B-A3B-Instruct Q3_K_M
- configured context: 32768
- llama.cpp build 10752
- llama.cpp commit: `b96806d96061049a5b574269b049bf6241d63d46`

Execution:

- started: `2026-09-27T18:06:26Z`
- ended: `2026-09-27T18:16:11Z`
- wall time: 586 s
- termination reason: `agent_declared_completion`
- OpenCode exit code: 0
- OpenCode final step reason: `stop`
- human interventions: 0

## Hidden evaluator

BENCH-CODE-001 v1.0 evaluator result:

```text
tests_passed=16
tests_total=16
critical_tests_passed=14
critical_tests_total=14
all_tests_passed=true
all_critical_tests_passed=true
```

All hidden tests passed, including persistence after application restart and representative injection-style authentication/ownership checks.

## Frozen artifacts

Candidate commit:

```text
7a291a923cbad003ee7496b8357e8cdf8a1f50c0
```

Candidate archive SHA-256:

```text
b035da8c7ece2667e2dda31eef4f516fc81a49ef1c850db7f738a21b140879bc
```

OpenCode event log SHA-256:

```text
f7d4eb77b1ae28901a6b5a025813952d807b57f67855a3e45935be32af3e4a34
```

OpenCode stderr SHA-256:

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Evaluation JSON SHA-256:

```text
d28b51df23c15c53a4d52cba25a53946dd2caff1c969a5697cf68815c311b1aa
```

Inference/telemetry artifacts:

```text
llama-server.log
bf752c76b5c5fbd8be1b97660fd2ea974efd2d1d1bb02ecb33beec7b26346243

llama-metrics-before.prom
033056262d2dfed7ee1a6103733a5e445b13fb53daaa6de97304ae73a95d0f36

llama-metrics-after.prom
ee504fb2a1da9e0507ea8b01039c3cd9a4046de9d51ad657cff8aa1dade01be8

amd-smi.csv
ac966d0f34c821850eddfde2067c0ccb733520ea06ecd33301ca1e3a2620220a
```

## Interpretation

C001-A03 is a fully successful autonomous functional run under the BENCH-CODE-001 v1.0 primary engineering outcome:

> independent hidden functional tests passed without human intervention.

This is the third independent 16/16 run for the same OpenCode/Qwen3-Coder configuration.
