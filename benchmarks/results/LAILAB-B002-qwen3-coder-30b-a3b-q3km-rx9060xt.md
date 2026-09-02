# LAILAB-B002 — Qwen3-Coder-30B-A3B-Instruct Q3_K_M on RX 9060 XT

## Summary

This experiment evaluates Qwen3-Coder-30B-A3B-Instruct, quantized as Q3_K_M, on the LocalAI-Lab AMD Radeon RX 9060 XT using the ROCm/HIP build of llama.cpp established in the Phase 5 baseline.

The model is a Mixture-of-Experts (MoE) architecture with 30.53B total parameters. The Q3_K_M GGUF is 13.70 GiB and fits almost entirely within the 16 GiB-class GPU while preserving approximately 1 GiB of target free VRAM through llama.cpp automatic fitting.

Experiment ID: `LAILAB-B002`

Date: `2026-09-02`

## Hardware

| Component | Configuration |
|---|---|
| CPU | Intel Core i5-14600KF, 14 cores / 20 threads |
| System memory | 64 GB class, 62 GiB visible |
| GPU | AMD Radeon RX 9060 XT |
| GPU architecture | `gfx1200` |
| GPU VRAM reported by llama.cpp | 16,304 MiB |
| OS | Ubuntu 24.04.4 LTS |
| Kernel | 7.0.0-30-generic |

## Software

| Component | Version / configuration |
|---|---|
| ROCm | 10.0 SDK/runtime environment |
| HIP | 7.15.26333-0000000 |
| llama.cpp | 0.3.0-dev |
| llama.cpp build | 10752 |
| llama.cpp commit | `b96806d96061049a5b574269b049bf6241d63d46` |
| Compiler | Clang 23.0.0 |
| Backend | GGML HIP / ROCm |
| GPU target | `gfx1200` |

## Model

| Field | Value |
|---|---|
| Model | Qwen3-Coder-30B-A3B-Instruct |
| Architecture reported by llama-bench | `qwen3moe` |
| Total parameters | 30.53 B |
| Quantization | Q3_K_M (`Q3_K - Medium`) |
| GGUF size reported by llama-bench | 13.70 GiB |
| Model path | `/srv/models/coding/qwen3-coder-30b-a3b/Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf` |

## Runtime configuration

The benchmark used llama.cpp automatic fit with a target free-memory margin of 1024 MiB:

```bash
./build-rocm/bin/llama-bench \
  -m /srv/models/coding/qwen3-coder-30b-a3b/Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf \
  --fit-target 1024 \
  -p 512 \
  -n 128 \
  -r 5
```

A second combined benchmark was executed with:

```bash
./build-rocm/bin/llama-bench \
  -m /srv/models/coding/qwen3-coder-30b-a3b/Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf \
  --fit-target 1024 \
  -pg 512,128 \
  -r 5
```

`llama-bench` reported `ngl = -1`, indicating automatic GPU-layer fitting rather than a manually fixed layer count.

## Performance results

### Benchmark 1 — separate prompt processing and token generation

| Test | Throughput |
|---|---:|
| PP512 | **1923.80 ± 215.82 tok/s** |
| TG128 | **69.13 ± 1.94 tok/s** |

Observed telemetry during this run:

| Metric | Observed value |
|---|---:|
| Peak VRAM | ~14,400 MiB |
| GPU temperature | 73 °C |
| GPU power | 133 W |

### Benchmark 2 — combined workload

| Test | Throughput |
|---|---:|
| PP512 | **1905.84 ± 211.66 tok/s** |
| TG128 | **69.14 ± 1.88 tok/s** |
| PP512 + TG128 | **296.18 ± 2.61 tok/s** |

Observed telemetry during this run:

| Metric | Observed value |
|---|---:|
| Peak VRAM | ~14,700 MiB |
| GPU temperature | 73 °C |
| GPU power | 138 W |

## Interactive inference observation

Before the formal benchmark, an interactive coding prompt was executed with a 4096-token context and automatic fitting. The model successfully generated Python code with type hints and documentation.

Observed interactive throughput:

| Metric | Throughput |
|---|---:|
| Prompt | 22.6 tok/s |
| Generation | 65.9 tok/s |

This interactive prompt result is retained as an operational observation only and should not be directly compared with the formal PP512 benchmark because the workload, prompt length, initialization overhead, and measurement method differ.

A second short interactive test (`"test"`, 32 generated tokens) reported approximately 63.1 tok/s generation with ~14,466 MiB VRAM usage. Its prompt throughput value is not treated as a benchmark because the prompt was too short for meaningful prompt-processing comparison.

## Comparison with LAILAB-B001

LAILAB-B001 used Qwen3-8B Q4_K_M on the same RX 9060 XT and llama.cpp/ROCm stack.

| Metric | B001: Qwen3-8B Q4_K_M | B002: Qwen3-Coder-30B-A3B Q3_K_M | Change |
|---|---:|---:|---:|
| Model size | 4.68 GiB | 13.70 GiB | +192.7% |
| Parameters | 8.19 B | 30.53 B total | +272.8% total params |
| PP512 | 2275.85 tok/s | 1923.80 tok/s | **-15.5%** |
| TG128 | 56.04 tok/s | 69.13 tok/s | **+23.4%** |
| Peak VRAM | 4872 MiB | ~14,400 MiB | +195.6% |
| GPU temperature | 78 °C | 73 °C | -5 °C |
| GPU power | 160 W | 133 W | -27 W |

The key result is that the much larger MoE coding model achieved approximately **23% higher token-generation throughput** than the dense 8B validation model while using lower observed GPU power during the first formal B002 run. Prompt processing was approximately 15.5% slower.

This result is consistent with the computational characteristics expected from a sparse MoE model: total parameter count and storage requirements are large, but only a subset of experts is active for each token. This architectural interpretation should be treated as explanatory context rather than a direct measurement of expert activation in this experiment.

## Approximate power-efficiency indicator

Using the observed power reading during Benchmark 1:

- TG128: 69.13 tok/s
- Observed GPU power: 133 W
- Approximate indicator: **0.520 tok/s/W**

For the combined-workload telemetry point:

- TG128: 69.14 tok/s
- Observed GPU power: 138 W
- Approximate indicator: **0.501 tok/s/W**

For reference, B001 produced approximately 0.350 tok/s/W using its observed 160 W reading. Thus, the B002 first-run indicator is approximately 48% higher.

These values are **not energy measurements**. Power was manually observed rather than integrated over the benchmark duration. They must not be reported as joules/token or formal energy efficiency. Future telemetry should sample power continuously and integrate energy over time.

## Interpretation

The Q3_K_M quantization appears particularly well matched to the 16 GiB RX 9060 XT:

- The 13.70 GiB model fits with automatic GPU-memory fitting enabled.
- Peak observed VRAM remained approximately 14.4–14.7 GiB, leaving operational headroom.
- Token generation was stable around 69 tok/s in both formal runs.
- Prompt processing remained approximately 1.9k tok/s at PP512.
- Observed GPU temperature remained at 73 °C.
- Observed power was 133–138 W during the recorded tests.

This makes Qwen3-Coder-30B-A3B-Instruct Q3_K_M a strong candidate for the primary LocalAI-Lab coding model and for subsequent exposure through `llama-server` to remote development clients such as Visual Studio Code.

## Limitations

1. GPU power, temperature, and VRAM values were manually observed using AMD monitoring tools rather than sampled and logged continuously.
2. Ambient temperature was not recorded.
3. No CPU-only B002 comparison was run because the operational objective is GPU-backed coding inference.
4. Coding quality was not formally evaluated in this benchmark; only throughput and operational behavior were measured.
5. The Q3_K_M quantization should later be compared against higher-quality quantizations or alternative model variants where memory permits.
6. VS Code / coding-agent end-to-end latency, tool calls, test execution, and repository-edit success remain to be measured in later experiments.

## Next experiment

The next stage is to expose this model through `llama-server` on the LAN and validate an OpenAI-compatible API from a second workstation. Subsequent coding-agent experiments should measure:

- time to first token,
- generation throughput,
- end-to-end task completion time,
- number of agent iterations,
- tool calls,
- build/test success,
- human intervention,
- VRAM/RAM utilization,
- temperature,
- time-series power and energy per task.
