# DEV002-CODER-NEXT-Q3

- model: Qwen3-Coder-Next ~80B-A3B Q3_K_M
- OpenCode model id: `local/qwen3-coder-next-q3`
- context: 49,152
- agent exit: 0
- human interventions: 0
- wall time: 737.994 s
- official main: 15/18
- official critical: 12/15
- audited main: 12/18
- audited critical: 10/15
- restart: 2/2
- E2E: 0/6
- prompt tokens: 78,847
- generated tokens: 12,178
- prompt processing: 277.218 tok/s
- generation: 30.0023 tok/s
- files modified: 5
- line delta: +206 / -2
- classification: FAIL

## Root findings

The backend supported create/list/update/delete and restart persistence. GET `/api/admin/vehicles/:id` was missing, which also prevented direct verification of the updated vehicle through that endpoint. Duplicate matrícula was rejected as HTTP 500 rather than the required 4xx.

The frontend did not satisfy the required stable `data-testid` contract, producing 0/6 E2E passes.

Semantic Audit v2 removed vacuous 404-based passes and produced the final 12/18, 10/15 audited score.
