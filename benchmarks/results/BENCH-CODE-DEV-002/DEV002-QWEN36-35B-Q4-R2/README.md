# DEV002-QWEN36-35B-Q4-R2

- model: Qwen3.6-35B-A3B Q4_K_M
- OpenCode model id: `local/qwen3.6-35b-q4`
- context: 49,152
- agent exit: 0
- human interventions: 0
- wall time: 987.068 s
- official main: 11/18
- official critical: 8/15
- audited main: 5/18
- audited critical: 5/15
- restart: 1/2
- E2E: 0/6
- prompt tokens: 131,222
- generated tokens: 29,255
- prompt processing: 628.782 tok/s
- generation: 40.6422 tok/s
- maximum observed context metric: 44,795 tokens
- files modified: 3
- line delta: +286 / -1
- classification: FAIL

## Root findings

All positive vehicle CRUD operations returned generic 404 responses. The model created `Vehiculo.js`, `routes/admin/vehicles.js` and a new `routes/admin/index.js`, but did not modify the existing `backend/src/routes/admin.js` router used by the application. The new route implementation was therefore effectively disconnected from the live application.

This is the clearest example of why Semantic Audit v2 was required: several negative tests passed only because the route did not exist at all, reducing the official 11/18 to an audited 5/18.
