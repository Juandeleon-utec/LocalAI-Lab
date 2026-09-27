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

## Still required before formal start

- exact ROCm/HIP version;
- exact llama-server launch arguments;
- OpenCode version;
- immutable seed archive SHA-256;
- confirmation that the server reports one slot with 32768-token context;
- start timestamp UTC.
