# BENCH-CODE-001 v1.0 — Execution Protocol

## 1. Scope

This protocol controls the first reproducible greenfield coding-agent comparison in LocalAI-Lab.

The benchmark evaluates complete agent systems. It does not claim that differences between Claude Code and OpenCode/local models are caused only by the underlying LLM.

## 2. Immutable inputs

Before the first formal run, record SHA-256 hashes for:

- `prompt.md`;
- the exported seed repository;
- hidden evaluator archive;
- evaluator configuration;
- benchmark protocol;
- benchmark-server image or environment specification.

All runs of v1.0 must use the same immutable inputs.

## 3. Initial workspace

Each run starts from a fresh Git repository exported from `seed/`.

The participant must not receive:

- prior candidate outputs;
- hidden evaluator source;
- another model's solution;
- human-written reference implementation.

Create an experiment branch or disposable repository for each run.

## 4. Execution environment

All candidate applications are validated on the same dedicated benchmark/staging server.

The benchmark server should provide the same:

- physical host and operating-system build;
- CPU allocation;
- RAM allocation;
- Node.js version;
- MySQL version;
- network policy;
- environment-variable contract;
- database initialization state.

Each candidate receives a fresh MySQL database.

Candidate applications must not share database state.

The benchmark server is a staging/evaluation environment, not a public production service.

## 5. Network policy

During agent generation, network access required for normal package installation may be enabled.

If possible, interactive web search/browsing should be disabled for every system. If a system cannot be configured equivalently, record that difference in the run manifest.

## 6. Human intervention

Formal runs use:

- one initial participant prompt;
- no corrective human prompts;
- no manual code edits;
- no hints after execution begins.

The agent may inspect files, run commands, edit code, execute tests/checks and correct its own failures.

If human intervention becomes necessary, record the run as requiring intervention rather than silently assisting it.

## 7. Stop conditions

A run stops when one of the following occurs:

1. the agent declares completion;
2. the agent reports an unrecoverable failure;
3. 60 minutes of wall-clock agent time are reached;
4. the execution environment fails for reasons unrelated to the candidate.

Infrastructure failures are recorded separately from model/agent failures.

## 8. Systems and comparison layers

### Local model comparison

Hold the agent and nominal context budget constant:

- OpenCode + Qwen3-Coder-30B-A3B-Instruct Q3_K_M — 32768 context;
- OpenCode + Qwen3.6-35B-A3B Q4_K_M — 32768 context.

Record actual maximum context/token usage and compaction events where observable.

### Hosted system baseline

Claude Code receives:

- the same seed repository;
- the same `prompt.md`;
- the same benchmark-server validation;
- no corrective human prompting.

Claude Code uses its normal supported model/context configuration. This is explicitly a complete-system baseline.

### MTP experiment

Qwen3.6 + MTP uses the same model quantization, agent, prompt, seed and 32K context as the non-MTP Qwen3.6 run as far as practical.

Primary MTP outcomes are throughput, latency, total task time and energy. Functional quality is retained as a guardrail metric.

## 9. Repetitions

Engineering phase:

- 3 independent clean runs per system.

Before publication-oriented claims, define the statistical analysis and reconsider whether more repetitions are required.

## 10. Primary outcome

Primary engineering outcome:

**independent hidden functional tests passed without human intervention.**

Report both:

- total tests passed;
- whether all critical authorization/authentication tests passed.

Do not collapse all outcomes into a single subjective score.

## 11. Additional metrics

### Functional

- application starts successfully;
- `/health` succeeds;
- hidden tests passed;
- regression/functional failures;
- persistence after restart.

### Agent autonomy

- completed without human intervention;
- tool calls;
- agent iterations;
- edit-test-fix cycles;
- observable compaction events;
- failure mode.

### Efficiency

- total wall time;
- prompt/input tokens where available;
- generated/output tokens where available;
- prompt-processing throughput;
- generation throughput.

### Code artifacts

- files created/modified;
- lines added/deleted;
- dependency count;
- final repository size;
- optional static-analysis metrics.

### Local infrastructure

- mean/peak VRAM;
- mean/peak RAM;
- GPU/CPU utilization;
- temperature;
- sampled power;
- integrated energy per task.

### Hosted baseline

Record available usage/cost/latency information. Local hardware metrics are N/A for hosted systems.

## 12. Candidate deployment and manual review

After the agent stops:

1. freeze the candidate repository at a commit;
2. deploy that exact commit to the benchmark server;
3. run the hidden evaluator;
4. retain logs and test output;
5. expose the candidate only on the controlled evaluation network for human review.

For human review, relabel candidates A/B/C rather than exposing the generating system when practical.

## 13. Run manifest minimum fields

Each run should record:

- run ID and timestamp;
- BENCH-CODE-001 version;
- LocalAI-Lab commit;
- seed commit/hash;
- prompt SHA-256;
- evaluator SHA-256;
- system/agent name and version;
- model/provider identifier;
- model GGUF filename/SHA-256 and quantization for local runs;
- llama.cpp commit/build for local runs;
- ROCm/kernel/OS for local runs;
- server launch arguments;
- configured context;
- actual context/token usage where observable;
- compaction count where observable;
- generation settings where exposed;
- start/end time;
- termination reason;
- human intervention count;
- functional test results;
- candidate commit;
- telemetry artifact references.

## 14. Freeze and versioning

Once formal v1.0 execution begins:

- do not edit the prompt in place;
- do not change hidden tests in place;
- do not change primary outcomes in place.

Changes that can affect candidate behavior or scoring create BENCH-CODE-001 v1.1 or a new benchmark ID.
