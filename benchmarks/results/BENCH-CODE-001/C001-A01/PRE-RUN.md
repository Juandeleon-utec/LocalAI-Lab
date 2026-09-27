# C001-A01 — Pre-run inference freeze

Status: **PRE-RUN — do not count as a formal result until the agent starts**

## Benchmark

- ID: BENCH-CODE-001
- Version: 1.0
- Run ID: C001-A01
- Participant system: OpenCode + local Qwen3-Coder
- Configured context: 32768 tokens
- Human intervention target: 0

## Local inference server

- llama.cpp version: 0.3.0-dev
- llama.cpp build: 10752
- llama.cpp commit: `b96806d96061049a5b574269b049bf6241d63d46`
- compiler: Clang 23.0.0
- platform: Linux x86_64

## Model

- model family: Qwen3-Coder-30B-A3B-Instruct
- quantization: Q3_K_M
- GGUF file: `Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf`
- GGUF SHA-256:

```text
f67299d72124ed68b4cbf3a776079df289bd854a17dfe6febfc835d1e1fbdefb
```

## Runtime library resolution

The frozen llama-server binary initially required the ROCm library directory to be added to the shell runtime library path. With the active runtime environment:

```text
ldd .../llama-server -> All shared libraries resolved
```

No llama-server process was running when the fingerprint was captured.

## Server preflight result

The formal 32K server profile was started successfully after removing the manually forced `-ngl 99` setting that caused a pre-run VRAM OOM during context allocation.

Observed health:

```json
{"status":"ok"}
```

Observed slot/context initialization:

```text
n_slots = 1
n_ctx_slot = 32768
kv_unified = false
```

This confirms the intended formal context budget before agent execution. The failed `-ngl 99` attempt occurred before the agent received the benchmark prompt and therefore is not a formal benchmark run.

## Still required before formal start

- exact ROCm/HIP version;
- exact live llama-server command line;
- OpenCode version;
- immutable seed archive SHA-256;
- start timestamp UTC.


## Infrastructure-aborted launch attempt — 2026-09-27

A launcher attempt printed `C001-A01 FORMAL START` at `2026-09-27T12:17:48Z`, but it is classified as **invalid / non-scorable infrastructure setup**, not as a model result.

Observed before any useful agent work:

- Windows freeze verification failed because Docker Desktop's Linux engine pipe was unavailable;
- OpenCode 1.18.27 reported `Provider not found: local`;
- the active OpenCode config did not contain the required 32768 context declaration;
- the interactive PowerShell paste split an `if { ... } else { ... }` construct, leaving termination/exit-code fields empty;
- OpenCode emitted an `Unexpected server error` event after approximately 4 seconds;
- no candidate implementation work is credited to Qwen from this attempt.

Per the BENCH-CODE-001 protocol, infrastructure failures are recorded separately from model/agent failures. C001-A01 remains pending and must restart from a fresh seed only after Docker, OpenCode provider resolution and the launcher script are validated.
