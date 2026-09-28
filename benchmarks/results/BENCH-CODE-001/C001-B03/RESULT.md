# C001-B03 — Formal Result

## Outcome

System:

- OpenCode 1.18.27
- local/qwen3.6
- Qwen3.6-35B-A3B Q4_K_M
- configured context: 32768
- llama.cpp build 10752
- llama.cpp commit: `b96806d96061049a5b574269b049bf6241d63d46`
- MTP: disabled

Execution:

- started: `2026-09-28T02:53:41Z`
- ended: `2026-09-28T03:06:42Z`
- wall time: 781 s
- termination reason: `agent_declared_completion`
- OpenCode exit code: 0
- OpenCode final step reason: `stop`
- human interventions: 0

The agent ended after automatic context compaction. Its final message stated that the application source was complete but that its local self-test was blocked because MySQL was not running at `127.0.0.1:3307`. No corrective prompt or human intervention was supplied.

## Candidate freeze

Before freezing, repository state was inspected:

- `.env` was ignored by `.gitignore`;
- `.env.example` and `.gitignore` were staged as candidate files;
- the ignored self-test `.env` was excluded from the candidate archive.

Candidate commit:

```text
12be1b859e41bab2f9d940ac384596c83bfc956a
```

Candidate archive SHA-256:

```text
ab91af4342532f382df1b4700f3c622c6630994d9042e4fe0a7330870bde60cb
```

Archive inspection confirmed that it contained:

```text
.env.example
.gitignore
```

and did **not** contain `.env`.

## Clean deployment result

**Deployment FAIL before hidden tests.**

The clean evaluator environment started the pinned MySQL service successfully. Dependency installation succeeded. The candidate then ran:

```text
npm run db:init
node migrations/init-db.js
```

The migration connected successfully to the contractual benchmark database endpoint:

```text
Connecting to MySQL at 127.0.0.1:3307 as bench_user...
Connected to MySQL server.
```

It then failed with a SQL syntax error near the second statement (`USE bench_code_001`).

Inspection of the frozen migration showed:

```javascript
const config = {
  ...
  multipleStatements: true,
};

const schema = `
CREATE DATABASE ...;
USE ...;
CREATE TABLE ...;
CREATE TABLE ...;
`;

await connection.execute(schema);
```

The candidate therefore supplied a multi-statement schema block to `mysql2/promise` via `execute()`. The failure is localized to the migration implementation; normal application queries in `src/database.js` use `pool.execute(sql, params)` for individual parameterized statements.

Because `npm run db:init` failed, `npm start` was not reached and the hidden evaluator was **not run**.

## Throughput instrumentation

| Metric | C001-B03 |
|---|---:|
| Uncached prompt tokens | 92019 |
| Cached prompt tokens | 805455 |
| Generated tokens | 24049 |
| Prompt processing time | 131.901 s |
| Generation time | 574.349 s |
| Prompt throughput | 697.64 tok/s |
| Decode throughput | 41.87 tok/s |
| Prompt cache ratio | 89.75% |
| Inference time | 706.250 s |
| Inference share of wall | 90.43% |
| Non-inference wall time | 74.750 s |

Raw B03 telemetry remained stored in the external run directory. No additional SHA-256 values for those telemetry files are recorded here because they were not captured in the closeout evidence supplied to this repository.
