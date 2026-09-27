# C001-A02 — Formal Result

## Outcome

System:

- OpenCode 1.18.27
- local/qwen3-coder
- Qwen3-Coder-30B-A3B-Instruct Q3_K_M
- configured context: 32768
- llama.cpp build 10752
- llama.cpp commit: `b96806d96061049a5b574269b049bf6241d63d46`

Execution:

- started: `2026-09-27T17:41:38Z`
- ended: `2026-09-27T17:51:05Z`
- wall time: 567 s
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
73f545dc6e179de2c8a0e44d0990a184fede6e04
```

Candidate archive SHA-256:

```text
d5ed813ec223542e63dca53cce2e2606a892cdf614325d695f1629dc3438bf20
```

OpenCode event log SHA-256:

```text
ab447d3cbddc58927724df86d7e353eeee0123608f182e70d4467d094a0519ee
```

OpenCode stderr SHA-256:

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Evaluation JSON SHA-256:

```text
edcb64b1a5baffba2021a7c87288dc47b7a676d06e820a6a6069dd3172bef8d7
```

Inference/telemetry artifacts:

```text
llama-server.log
d715cc1ce1d37c41cff32207adc86509e558189186dcbb4bbfabd69a9b057d4a

llama-metrics-before.prom
033056262d2dfed7ee1a6103733a5e445b13fb53daaa6de97304ae73a95d0f36

llama-metrics-after.prom
e3be05e80a8c368be56fb11e4b0f592beb04ed797108ee9a93d19999da80e46f

amd-smi.csv
fe3a6b8a3cc73be23e51d5a756779988ab4b893c7157eb7b7a00581ab41027f7
```

## Interpretation

C001-A02 is a fully successful autonomous functional run under the BENCH-CODE-001 v1.0 primary engineering outcome:

> independent hidden functional tests passed without human intervention.

This is the second independent 16/16 run for the same OpenCode/Qwen3-Coder configuration.
