# BENCH-CODE-001 Reference Validation PASS — 2026-09-26

## Result

The known-good reference candidate completed the full Windows BENCH-CODE-001 harness successfully.

Observed sequence:

```text
fresh mysql:8.4 container
-> MySQL healthy
-> npm install
-> npm run db:init
-> database schema initialized
-> npm start
-> GET /health PASS
-> hidden evaluator pre-restart
-> Node restart without resetting MySQL
-> GET /health PASS
-> hidden evaluator post-restart
-> aggregate evaluation
```

## Hidden evaluator result

Pre-restart phase:

```text
15 / 15 total
13 / 13 critical
all tests passed: true
all critical tests passed: true
```

Post-restart persistence phase:

```text
1 / 1 total
1 / 1 critical
all tests passed: true
all critical tests passed: true
```

Aggregated BENCH-CODE-001 v1.0 result:

```text
16 / 16 total
14 / 14 critical
all tests passed: true
all critical tests passed: true
```

## Interpretation

The benchmark instrument has now demonstrated end-to-end operation on the Windows engineering-validation workstation, including:

- clean ephemeral MySQL lifecycle;
- dependency installation;
- schema initialization;
- application startup;
- health readiness;
- authentication/CRUD/security evaluator phases;
- process restart without database reset;
- persistence validation;
- pre/post result aggregation.

No model comparison result is represented by this validation run. The reference candidate exists only to validate the benchmark instrument.

## Next gate

Before C001-A01:

1. capture the exact LocalAI-Lab commit used;
2. preserve the generated environment snapshot SHA-256;
3. preserve the exact MySQL image digest;
4. preserve the prompt SHA-256;
5. preserve the hidden evaluator SHA-256;
6. decide whether this Windows workstation is the formal staging host;
7. if selected, freeze its runtime configuration for all formal BENCH-CODE-001 v1.0 runs.
