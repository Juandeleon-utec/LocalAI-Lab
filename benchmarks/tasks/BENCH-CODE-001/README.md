# BENCH-CODE-001 v1.0

## Authenticated Node.js/MySQL Web Application

**Status:** protocol candidate frozen before formal runs  
**Benchmark type:** greenfield coding-agent task  
**Primary purpose:** compare complete AI-assisted development systems under a reproducible, executable task.

## Research questions

1. Can the current local coding system produce a complete, deployable web application without human correction when given sufficient context?
2. How does Qwen3-Coder-30B-A3B-Instruct compare with Qwen3.6-35B-A3B when both use the same OpenCode agent, repository state and 32K context budget?
3. How does the best local system compare at system level with a professional hosted coding agent such as Claude Code?
4. Does MTP improve end-to-end efficiency for Qwen3.6 without materially changing functional quality?

## Task

The participant must create a small authenticated web application using Node.js and MySQL. The application supports registration, login and user-owned records with CRUD operations. A minimal web frontend must be provided.

The exact task delivered to every participant is in [prompt.md](prompt.md).

## Benchmark artifacts

- `prompt.md` — immutable participant prompt.
- `protocol.md` — run controls, systems, repetitions and measurement policy.
- `evaluator/README.md` — evaluator contract and hidden-test policy.
- `review-rubric.md` — blinded human-review rubric.
- `seed/README.md` — content of the initial participant workspace.

## Planned systems

| Run family | System | Local context |
| --- | --- | ---: |
| C001-A | OpenCode + Qwen3-Coder-30B-A3B-Instruct Q3_K_M | 32768 |
| C001-B | OpenCode + Qwen3.6-35B-A3B Q4_K_M | 32768 |
| C001-C | Claude Code | provider-native |
| C001-D | OpenCode + Qwen3.6-35B-A3B Q4_K_M + MTP | 32768 |

C001-A/B compare local models while holding the agent and nominal context budget constant. C001-C is a system-level hosted baseline, not an isolated model comparison. C001-D is primarily an inference-efficiency experiment.

## Pilot status

The earlier 8K OpenCode/Qwen3-Coder work remains useful as engineering evidence, but it is treated as a pilot because context pressure and compaction were observed. Formal BENCH-CODE-001 local runs use a 32K context budget unless a later protocol version explicitly changes it.

## Repetition policy

The initial engineering phase uses three clean runs per system. Publication-oriented use should reassess the repetition count before formal claims.

## Ground truth

Claude Code is not the reference implementation. All systems are evaluated against the same independent functional contract and evaluator.

## Freeze rule

Once the first formal run is executed, BENCH-CODE-001 v1.0 prompt, endpoint contract, primary metrics and hidden evaluator must not be silently changed. Material changes require a new benchmark version.
