# Academic Reviewer AI — October 2026 model comparison

**Captured:** 2026-10-27 from documented conversations. **Status:** preliminary qualitative and numerical observations; raw evaluator outputs remain on the local server, not in this Git repository.

## Architecture and protocol

- Local reviewer application: `academic-reviewer-ai-v0.3.2`; Streamlit `http://192.168.2.237:8501` observed.
- Runs written beneath `benchmarks/runs/<run-id>/`; example recorded run: `AR-4413ebf5fcd2`.
- Relevant outputs: `manifest.json`, `result.json`, and Markdown reports.
- Baseline uses Qwen `qwen3-academic` on `http://127.0.0.1:8090/v1`.
- The intended model comparison uses the same input PDF and frozen prompt/engine versions. Do not claim equivalent conditions without matching document/extraction hashes and prompt_version.

## Reported observations

| Configuration / experiment | Reported output | Interpretation |
|---|---|---|
| Earlier v0.2 bibliographic review | 23 observations (3 critical, 12 moderate, 8 minor); 8 discarded for insufficient literal evidence | Different software version; **not** directly comparable to v0.3.2. |
| Earlier v0.3.2 report #2 | 5 moderate observations, 6 excerpts, 11 discarded | Baseline reviewer output; model/run linkage requires manifest verification. |
| Gemma 4 26B Q3 reviewer test | 4 findings, 1 confirmed, 14 discarded, 2 deterministic checks | Reported comparative observation; matching SHA and scoring definitions still required. |
| Gemma 4 21B REAP Q4 reviewer test | 5 findings, 0 confirmed, 14 discarded, 2 deterministic checks | Not evidence of superior or inferior model quality from one input. |

The Gemma trials reportedly exhibited mixed-language findings. A different extraction, validator or prompt version could materially affect score interpretation. Preserve both *generated* and *evidence-confirmed* counts separately.

## Review input used for repeated evaluation

A bibliographic PRISMA-based research review about detection/localization of canine waste was discussed repeatedly (539 initial records -> 29 final articles). Private original PDF is **not included** in this repository. No assertion that all rows above share exactly that same content hash.

## Required before claiming a formally reproducible model comparison

- Freeze input PDF hash, extraction hash, engine_version and prompt_version.
- Save model GGUF checksum and active llama-server effective settings per run.
- Export redacted original result JSON, validator decisions and report; preserve run IDs.
- Use consistent rubric for false positives, literal evidence, severity, recall, language and timing.
- Run repeated trials or label one-shot results exploratory.
- Review any sensitive source document before committing; share only permitted metadata.

## Verified local run manifest inventory — terminal output 2026-10-28

Seven local `manifest.json` files were enumerated under
`/home/jpdeleon/academic-reviewer-ai-v0.3.2/benchmarks/runs/`.
All seven report `engine_version=0.3.2`, `prompt_version=academic-reviewer-v0.3.2-evidence-1`,
`extraction_sha256=105989dae26fe7808ddfad4368ca048a5949c6292eb6f86c35ae0ea77aaa26b2`,
and an existing `result.json`.

| Run ID | UTC created_at | Model |
|---|---|---|
| AR-f5c39484bf83 | 2026-10-24T17:18:00.512551+00:00 | qwen3-academic |
| AR-4413ebf5fcd2 | 2026-10-24T18:07:45.636980+00:00 | qwen3-academic |
| AR-1a1922d522b4 | 2026-10-24T21:22:37.529651+00:00 | gemma4-academic-q3 |
| AR-3d635177e590 | 2026-10-25T03:20:56.106352+00:00 | gemma4-academic-q3 |
| AR-2fdf58148d16 | 2026-10-25T03:52:17.942119+00:00 | gemma4-academic-q3 |
| AR-7333c55150b2 | 2026-10-25T05:10:09.770350+00:00 | gemma4-academic-q3 |
| AR-7f3d0d839fa1 | 2026-10-25T19:42:26.384466+00:00 | gemma4-REAP-Q4 |

Counts by model: Qwen 2, Gemma 26B Q3 4, REAP 21B Q4 1.

**Comparability qualification:** matching extraction hash and version strings provide a useful common comparison basis, but the terminal snippet did not output `document_sha256`; original `manifest.json` and `result.json` files, model parameters, rubric and result-level outcomes still need inspection. The matching extraction hash alone does not establish a controlled benchmark.

Do not publish original PDF or confidential source passages; review exports before committing.

## Aggregate verified from uploaded JSON evidence (2026-10-28)

Evidence: user-supplied archive `localai-reviewer-results.tar.gz` with seven `manifest.json` and seven `result.json`. Results below were calculated directly from `result.json -> findings` and `contextual_adjudication[].validation_status`, **not** inferred from prose summaries.

All seven manifests have identical `source_sha256` and `extraction_sha256`, `engine_version=0.3.2`, `prompt_version=academic-reviewer-v0.3.2-evidence-1`, `mode=articulo`, `chunk_count=6`, `truncated=false`. This supports a shared input/extraction and engine/prompt setup. Model serving configuration, runtime load and sampling details are not fully frozen by this archive alone.

| Run | Model | Generated findings | Confirmed | Pending | Rejected | Warnings array |
|---|---|---:|---:|---:|---:|---:|
| AR-f5c39484bf83 | qwen3-academic | 9 | 1 | 6 | 2 | 1 |
| AR-4413ebf5fcd2 | qwen3-academic | 5 | 0 | 5 | 0 | 1 |
| AR-1a1922d522b4 | gemma4-academic-q3 | 4 | 0 | 4 | 0 | 1 |
| AR-3d635177e590 | gemma4-academic-q3 | 2 | 0 | 2 | 0 | 11 |
| AR-2fdf58148d16 | gemma4-academic-q3 | 4 | 0 | 4 | 0 | 12 |
| AR-7333c55150b2 | gemma4-academic-q3 | 4 | 1 | 3 | 0 | 1 |
| AR-7f3d0d839fa1 | gemma4-REAP-Q4 | 5 | 0 | 5 | 0 | 1 |
| **TOTAL** | | **33** | **2** | **29** | **2** | **28** |

### Aggregate by model

| Model | Runs | Findings | Confirmed | Pending | Rejected |
|---|---:|---:|---:|---:|---:|
| qwen3-academic | 2 | 14 | 1 | 11 | 2 |
| gemma4-academic-q3 | 4 | 14 | 1 | 13 | 0 |
| gemma4-REAP-Q4 | 1 | 5 | 0 | 5 | 0 |

**Interpretation:** `pendiente` means not adjudicated as confirmed; a pending finding is not an established manuscript defect. `rechazado` is a validator label, not a measurement of holistic model quality. Unequal repetitions (2/4/1) and differences in warning patterns prevent a ranking of model quality.

### Evidence handling and outstanding work

The archive contains finding-level evidence, report summaries and validator details that may quote the research manuscript. **Only the derived aggregate metadata above was committed**; raw `result.json`, PDFs, quotations and hidden validation text were not published. Before releasing full outputs, obtain authorization and redact manuscript-derived text and private metadata. Collect wall-time, token counts, actual inference flags, llama.cpp/ROCm build and GPU measurements to compare computational cost.
