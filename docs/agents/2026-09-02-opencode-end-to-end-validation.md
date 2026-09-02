# OpenCode End-to-End Agent Validation

**Date:** 2026-09-02  
**Status:** Functional validation completed; automated test-pass validation still pending capture  
**Client:** Windows + Visual Studio Code  
**Inference server:** Ubuntu Server 24.04 LTS + ROCm 10 + `llama.cpp`  
**Model:** Qwen3-Coder-30B-A3B-Instruct Q3_K_M  
**GPU:** AMD Radeon RX 9060 XT 16 GB

## Objective

Validate that a Windows development workstation can use a local coding agent over the LAN while inference runs remotely on the LocalAI-Lab AMD GPU server.

The target architecture is:

```text
Windows workstation
└── Visual Studio Code
    └── OpenCode
        └── OpenAI-compatible HTTP API over LAN
            └── llama-server
                └── Qwen3-Coder-30B-A3B-Instruct Q3_K_M
                    └── llama.cpp HIP / ROCm 10
                        └── Radeon RX 9060 XT 16 GB
```

## Server configuration

`llama-server` was started manually for validation. No systemd or automatic startup was enabled at this stage.

Representative configuration:

```bash
cd ~/llama.cpp

./build-rocm/bin/llama-server \
  -m /srv/models/coding/qwen3-coder-30b-a3b/Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --alias qwen3-coder \
  --fit on \
  --fit-target 1024 \
  -c 8192 \
  --jinja \
  --api-key localai-dev-key
```

The server was reachable from the Windows workstation at:

```text
http://192.168.2.237:8080/v1
```

The API key above is a development-only credential used for LAN validation and should not be reused for an Internet-exposed service.

## OpenAI-compatible API validation

The Windows workstation successfully queried `/v1/chat/completions` using `curl`.

Observed response metadata included:

- model alias: `qwen3-coder`
- `llama.cpp` fingerprint: `b10752-b96806d96`
- prompt tokens: 20
- completion tokens: 128
- prompt throughput: approximately 12.20 tok/s for the short interactive request
- generation throughput: approximately 64.22 tok/s
- completion termination: `length`, caused by the configured `max_tokens=128`

The observed generation throughput is consistent with the direct B002 benchmark and indicates low practical overhead for the HTTP serving path in this small test.

## OpenCode installation

OpenCode was installed globally on the Windows workstation:

```powershell
npm install -g opencode-ai
opencode --version
```

Validated version:

```text
1.18.27
```

## Repository inspection test

OpenCode was launched from the local clone of `LocalAI-Lab` in Visual Studio Code.

The agent was asked to inspect the repository without modifying files. It:

- explored the repository structure;
- issued 33 tool calls during the inspection;
- identified the project's two main workloads: coding and academic RAG/research;
- identified the main hardware and software stack;
- summarized the documentation layout;
- read benchmark results.

After synchronizing the local clone with `main`, OpenCode correctly compared:

- `LAILAB-B001` — Qwen3-8B Q4_K_M
- `LAILAB-B002` — Qwen3-Coder-30B-A3B-Instruct Q3_K_M

Its comparison reproduced the recorded benchmark values and selected B002 as the stronger coding-backend candidate, while correctly noting that coding quality had not yet been formally evaluated.

## Controlled write test

A dedicated branch was created on the Windows clone:

```text
test/opencode-agent-write
```

A Python virtual environment was created locally for test execution:

```powershell
python -m venv .venv
```

`pytest` was installed in that environment.

The repository did not previously contain a `.gitignore`, so one was created locally with:

```text
.venv/
```

OpenCode was then instructed to create files only under:

```text
experiments/opencode-test/
```

The agent successfully created the requested files under that controlled directory. This validates that the agent can perform repository write operations from the Windows workstation while using the remote local model as its inference backend.

## Validation status

| Capability | Status | Evidence |
|---|---|---|
| ROCm GPU inference | PASS | B001/B002 benchmarks |
| `llama-server` startup | PASS | model served on port 8080 |
| LAN connectivity | PASS | Windows client reached server |
| API authentication | PASS | authenticated `/v1` request succeeded |
| OpenAI-compatible chat API | PASS | `/v1/chat/completions` returned valid response |
| OpenCode startup | PASS | OpenCode 1.18.27 |
| Repository read/navigation | PASS | 33-tool-call repository exploration |
| Benchmark reasoning | PASS | B001/B002 comparison matched repository data |
| Controlled repository writes | PASS | files created under `experiments/opencode-test/` |
| Local Python test environment | PASS | Python 3.11 venv + pytest available |
| Agent-driven test pass | PENDING | final successful pytest output not yet captured |
| Autonomous edit-test-fix loop | PENDING | requires controlled failure/correction experiment |

## Engineering interpretation

This experiment moves LocalAI-Lab beyond isolated inference benchmarking. The platform now demonstrates a working client/server coding-agent path in which:

1. the developer works from a normal Windows + Visual Studio Code workstation;
2. OpenCode performs repository inspection and file operations locally;
3. model inference is executed remotely on the AMD GPU server;
4. communication occurs through an OpenAI-compatible `llama-server` endpoint over the LAN.

This is the first functional validation of the intended "local Claude Code-like" architecture.

## Limitations

This test does not yet demonstrate that the local model matches hosted coding agents in code quality or autonomous problem-solving ability.

The following remain to be measured:

- successful pytest completion produced by the agent itself;
- edit-test-debug-retest loops;
- repository-scale code changes;
- tool-call counts per task;
- task completion rate;
- human intervention rate;
- wall-clock latency;
- token usage;
- energy consumption per coding task;
- comparison with Qwen Code, Aider, Claude Code, or other agents.

## Next experiment

Create a controlled coding benchmark in which OpenCode must:

1. inspect a small repository;
2. implement a requested change;
3. execute tests;
4. diagnose at least one intentionally failing test;
5. modify the implementation;
6. rerun the tests until they pass;
7. record tool calls, elapsed time, token throughput, VRAM, GPU power, and human intervention.

This experiment should become the first task-level coding-agent benchmark for LocalAI-Lab.
