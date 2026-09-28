# C001-B02 — Formal Result

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

- started: `2026-09-28T01:11:09Z`
- ended: `2026-09-28T02:11:09Z`
- wall time: 3600 s
- termination reason: `timeout_60_minutes`
- OpenCode exit code: 124
- human interventions: 0

## Clean deployment result

**Deployment FAIL before hidden tests.**

The frozen candidate was redeployed after removing residual candidate-created services and ensuring port 3000 was free.

- dependency installation succeeded;
- `npm run db:init` succeeded;
- `npm start` failed to become healthy within the 90-second harness limit.

The application log showed the server failing to connect to MySQL at both `::1:3306` and `127.0.0.1:3306`, although the benchmark harness supplies the fresh MySQL service through `DB_PORT=3307`.

Post-run inspection of the frozen candidate found:

```text
src/config/index.js:
require('dotenv').config({ override: true });
...
dbPort: parseInt(process.env.DB_PORT, 10) || 3306
```

This configuration permits a repository-local dotenv value to overwrite the harness-provided environment-variable contract.

The clean deployment never reached a healthy application state, so the hidden evaluator was **not run**.

## Superseded diagnostic evaluation

An earlier evaluation produced 12/16 total and 10/14 critical tests. That result is retained only as diagnostic evidence. It occurred while a residual candidate-created MySQL container was listening on host port 3306 and therefore does not represent a clean benchmark deployment.

## Runtime behavior at generation timeout

The formal agent run itself reached the 60-minute stop condition. Final OpenCode events showed repeated application-start/port-verification attempts. A residual Node process was also observed after the timeout and cleaned up only after the candidate was frozen.

## Frozen artifacts

Candidate commit:

```text
725e16faf2bb93bbb33e361b74ae0b1f8745609b
```

Candidate archive SHA-256:

```text
36e5a8464cda168be201f93e9d9877072aca4af7d56b2dfbfea0d1988170e71f
```

OpenCode event log SHA-256:

```text
30b085126f65b43d9c1f57af5a582b8022e1be57fc70d8e724a73633043d0c0f
```

OpenCode stderr SHA-256:

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Superseded diagnostic evaluation JSON SHA-256:

```text
d30d8c7dddbecc37023ce6dfbd2bb0c186198f48e09ded4b6534e70ce957bbb3
```

Inference/telemetry artifacts:

```text
llama-server.log
626791cf20747edf3c8340145ede7b9c639ac8364abfa3a3184e82c85a169dc3

llama-metrics-before.prom
033056262d2dfed7ee1a6103733a5e445b13fb53daaa6de97304ae73a95d0f36

llama-metrics-after.prom
63f4e99e77c5386b1784c31f0ff5c3af270d537649c1abc32fa19f99b2d058f7

amd-smi.csv
8f349f6e0235e9f0c3fa622835f7a9811a700a68a27bb617e9bd0741a3e2aa57
```

## Throughput instrumentation

Run-isolated token counts and throughput are retained separately from deployment quality. They describe the 60-minute generation run even though the final artifact did not deploy cleanly.
