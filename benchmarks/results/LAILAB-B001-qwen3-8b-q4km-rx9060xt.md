# LocalAI-Lab Benchmark LAILAB-B001

## Objective

Establish the first reproducible inference-performance baseline for the LocalAI-Lab platform using an AMD Radeon RX 9060 XT 16 GB with ROCm 10 and a native `llama.cpp` HIP build.

## Date

2026-09-01

## Hardware

| Component | Value |
|---|---|
| CPU | Intel Core i5-14600KF |
| GPU | AMD Radeon RX 9060 XT |
| GPU architecture | `gfx1200` |
| Reported VRAM | 16,304 MiB |
| System RAM | 64 GB class / 62 GiB visible |

## Software

| Component | Value |
|---|---|
| OS | Ubuntu Server 24.04.4 LTS |
| Kernel | `7.0.0-30-generic` |
| ROCm | 10.0 |
| HIP | 7.15.26333-0000000 |
| HIP compiler | Clang 23.0.0 |
| llama.cpp version | 0.3.0-dev |
| llama.cpp build | 10752 |
| llama.cpp commit | `b96806d96061049a5b574269b049bf6241d63d46` |
| llama.cpp tag | `b10752` |
| Backend | GGML HIP / ROCm |

## Model

| Field | Value |
|---|---|
| Repository | `Qwen/Qwen3-8B-GGUF` |
| Model | Qwen3-8B |
| Quantization | Q4_K_M |
| Quantization label | Q4_K - Medium |
| Model size | 4.68 GiB |
| Parameters | 8.19 B |
| Modalities | Text |

## Runtime device detection

`llama-bench` reported:

```text
ggml_cuda_init: found 1 ROCm devices (Total VRAM: 16304 MiB):
  Device 0: AMD Radeon RX 9060 XT, gfx1200 (0x1200), VMM: no, Wave Size: 32, VRAM: 16304 MiB
```

Despite the historical `ggml_cuda_init` function name, the backend is ROCm/HIP, as confirmed by the linked `libggml-hip.so`, `libamdhip64.so.7`, hipBLAS, rocBLAS, and related ROCm libraries.

## Interactive inference validation

Command:

```bash
./build-rocm/bin/llama-cli \
  -hf Qwen/Qwen3-8B-GGUF:Q4_K_M \
  -ngl 99 \
  -c 4096 \
  -n 256 \
  -p "Explain in three paragraphs how a neural network learns from data."
```

Observed interactive throughput:

| Metric | Result |
|---|---:|
| Prompt processing | 337.6 tok/s |
| Token generation | 55.2 tok/s |

The model loaded and generated text successfully on the RX 9060 XT.

## Benchmark methodology

Primary GPU benchmark:

```bash
./build-rocm/bin/llama-bench \
  -hf Qwen/Qwen3-8B-GGUF:Q4_K_M \
  -ngl 99 \
  -p 512 \
  -n 128 \
  -r 5
```

Combined prompt/generation benchmark:

```bash
./build-rocm/bin/llama-bench \
  -hf Qwen/Qwen3-8B-GGUF:Q4_K_M \
  -ngl 99 \
  -pg 512,128 \
  -r 5
```

CPU-reference benchmark:

```bash
./build-rocm/bin/llama-bench \
  -hf Qwen/Qwen3-8B-GGUF:Q4_K_M \
  -ngl 0 \
  -p 512 \
  -n 128 \
  -r 5
```

Each reported result is based on five benchmark repetitions.

## Results

### GPU offload

| Test | Throughput |
|---|---:|
| PP512 | **2275.85 ± 118.37 tok/s** |
| TG128 | **56.04 ± 0.13 tok/s** |

A repeated run produced:

| Test | Throughput |
|---|---:|
| PP512 | 2263.25 ± 124.68 tok/s |
| TG128 | 55.97 ± 0.18 tok/s |
| PP512 + TG128 | 249.80 ± 0.14 tok/s |

The two independent GPU runs are closely aligned, especially for autoregressive generation throughput.

### CPU reference

The CPU-reference run used `ngl=0`, meaning no model layers were stored in GPU VRAM. The ROCm backend remained available to the executable, but inference weights were kept on the CPU path.

| Test | Throughput |
|---|---:|
| PP512 | **1044.22 ± 69.24 tok/s** |
| TG128 | **11.14 ± 0.05 tok/s** |

### GPU speedup over CPU reference

| Metric | GPU | CPU reference | Speedup |
|---|---:|---:|---:|
| PP512 | 2275.85 tok/s | 1044.22 tok/s | **2.18×** |
| TG128 | 56.04 tok/s | 11.14 tok/s | **5.03×** |

The generation result is the most relevant for interactive LLM usage: the RX 9060 XT delivered approximately five times the autoregressive token-generation throughput of the CPU-reference configuration.

## Resource measurements

Observed during the GPU benchmark:

| Metric | Observed value |
|---|---:|
| Peak VRAM | **4,872 MiB** |
| GPU temperature | **78 °C** |
| GPU power | **160 W** |

The model file is 4.68 GiB and peak observed VRAM was 4,872 MiB, indicating that the model fit fully in GPU memory with relatively small additional memory overhead under this benchmark configuration.

## Approximate efficiency indicator

Using the observed generation throughput and the observed 160 W GPU power reading:

```text
56.04 tok/s / 160 W ≈ 0.35 tok/s/W
```

This value is only an indicative point estimate. The power reading was observed during execution rather than integrated as a time series. It must not be treated as a rigorous energy-per-token result.

For publication-quality energy analysis, future experiments should sample power over time and integrate energy over the complete benchmark interval, reporting J/token or Wh per workload.

## Interpretation

1. ROCm 10 and `llama.cpp` HIP acceleration are operational on the Radeon RX 9060 XT (`gfx1200`).
2. Qwen3-8B Q4_K_M fits comfortably in 16 GB VRAM.
3. Autoregressive generation is stable at approximately 56 tok/s across repeated runs.
4. GPU generation throughput is approximately 5.03× the CPU-reference result.
5. Prompt processing is approximately 2.18× faster with GPU offload.
6. The observed interactive performance is sufficient for responsive local assistant use.
7. This benchmark validates the platform before moving to larger coding-oriented MoE models that will require partial CPU/RAM offload.

## Limitations

- Temperature and power are single observed values, not time-integrated measurements.
- Ambient temperature was not recorded.
- GPU hotspot/junction temperature was not recorded.
- CPU package power was not recorded.
- No energy-per-token integration was performed.
- The CPU reference used the same HIP-enabled executable with `ngl=0`; therefore it should be described as a CPU-reference configuration rather than an independently built CPU-only binary.
- Only one model and one quantization level are included in this baseline.

## Benchmark identifier

`LAILAB-B001`

This result is the first formal performance baseline of LocalAI-Lab and should be used as the reference point for subsequent model, quantization, context-length, GPU-offload, and software-stack comparisons.
