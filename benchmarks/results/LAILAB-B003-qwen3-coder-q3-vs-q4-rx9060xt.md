# LAILAB-B003 — Qwen3-Coder Q3_K_M vs Q4_K_M on RX 9060 XT

Date: 2026-10-05

## Objective

Direct paired throughput comparison of two quantizations of the same Qwen3-Coder-30B-A3B-Instruct base model on the same LocalAI-Lab hardware and llama.cpp/ROCm stack.

This benchmark complements the earlier agentic observations by using the same bounded llama-bench workload for Q3_K_M and Q4_K_M.

## Controlled workload

- backend: ROCm
- automatic GPU fitting: `ngl=-1`
- fit target: 1024 MiB
- prompt test: PP512
- generation test: TG128
- internal repetitions: 5
- same base model: Qwen3-Coder-30B-A3B-Instruct
- same GPU: AMD Radeon RX 9060 XT 16 GB class

## Results

| Metric | Q3_K_M | Q4_K_M | Q4 vs Q3 |
| --- | ---: | ---: | ---: |
| GGUF size | 13.70 GiB | 17.28 GiB | +26.13% |
| Parameters | 30.53 B | 30.53 B | same |
| PP512 | 1953.24 ± 180.63 tok/s | 1384.99 ± 119.01 tok/s | -29.09% |
| TG128 | 69.33 ± 1.80 tok/s | 56.22 ± 1.33 tok/s | -18.91% |

Equivalent interpretation:

- Q3_K_M was 41.03% faster than Q4_K_M on PP512.
- Q3_K_M was 23.32% faster than Q4_K_M on TG128.
- Q4_K_M is 26.13% larger on disk/model storage.

## Size-normalized throughput indicator

This is not an energy metric; it is only a rough storage-size-normalized throughput indicator.

| Metric | Q3_K_M | Q4_K_M |
| --- | ---: | ---: |
| TG128 / GiB | 5.06 tok/s/GiB | 3.25 tok/s/GiB |
| PP512 / GiB | 142.57 tok/s/GiB | 80.15 tok/s/GiB |

## Reverse-order replication

A second paired execution inverted model order to reduce simple order/thermal-state bias.

| Run | Quantization | PP512 (tok/s) | TG128 (tok/s) |
| --- | --- | ---: | ---: |
| Pair 1 | Q3_K_M | 1953.24 ± 180.63 | 69.33 ± 1.80 |
| Pair 1 | Q4_K_M | 1384.99 ± 119.01 | 56.22 ± 1.33 |
| Pair 2 (reverse) | Q4_K_M | 1348.46 ± 108.52 | 56.30 ± 1.46 |
| Pair 2 (reverse) | Q3_K_M | 1957.73 ± 160.90 | 69.32 ± 1.75 |

Mean of the two external runs:

| Metric | Q3_K_M | Q4_K_M | Q4 vs Q3 |
| --- | ---: | ---: | ---: |
| PP512 | 1955.49 tok/s | 1366.73 tok/s | -30.11% |
| TG128 | 69.325 tok/s | 56.26 tok/s | -18.85% |

Equivalent Q3 advantage:

- PP512: +43.08%
- TG128: +23.22%

External-run repeatability:

- Q3 PP512 pair difference relative to pair mean: 0.23%
- Q3 TG128 pair difference relative to pair mean: 0.01%
- Q4 PP512 pair difference relative to pair mean: 2.67%
- Q4 TG128 pair difference relative to pair mean: 0.14%

The TG128 result is especially stable across execution order for both quantizations. This materially strengthens the conclusion that, on this 16 GB RX 9060 XT and this llama.cpp build/configuration, Q3_K_M sustains roughly 23% higher token-generation throughput than Q4_K_M under the bounded TG128 workload.

## Interpretation

Q3_K_M is materially faster than Q4_K_M on this 16 GB GPU under the same direct inference workload.

The likely systems-level explanation is memory placement pressure: the 13.70 GiB Q3 model can fit much more comfortably inside the available GPU memory while preserving the 1024 MiB fit target, whereas the 17.28 GiB Q4 model exceeds nominal physical VRAM even before KV/cache/runtime overhead. With automatic fitting enabled, Q4 therefore necessarily relies more heavily on non-VRAM placement/offload. Exact layer placement should be measured explicitly before assigning all of the performance loss to offload.

This benchmark does not measure coding quality. Earlier agentic experiments showed better long-horizon completion/stability for Q4_K_M in the tested audit/debug tasks, so the current engineering trade-off is:

- Q3_K_M: higher direct throughput and better memory fit;
- Q4_K_M: higher-precision quantization and, in current exploratory agentic evidence, better long-horizon task completion.

The quality/stability claim remains exploratory because the number of matched agentic repetitions is still small.

## Relationship to LAILAB-B002

The historical B002 Q3_K_M result was:

- PP512: 1923.80 ± 215.82 tok/s
- TG128: 69.13 ± 1.94 tok/s

The new B003 Q3 values are:

- PP512: 1953.24 ± 180.63 tok/s
- TG128: 69.33 ± 1.80 tok/s

The close agreement provides a useful repeatability check for the Q3 baseline.

## Next step

The reverse-order pair has now been completed and confirms the throughput difference. Next, capture VRAM, RAM, GPU utilization, temperature, power and exact layer/offload placement so the performance gap can be related to resource placement rather than throughput alone.
