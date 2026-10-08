# DEV002-CODER30-Q4

- model: Qwen3-Coder-30B-A3B-Instruct Q4_K_M
- OpenCode model id: `local/qwen3-coder-q4`
- context: 49,152
- agent exit: 0
- human interventions: 0
- wall time: 843.555 s
- prompt tokens: 87,192
- generated tokens: 19,903
- prompt processing: 611.408 tok/s
- generation: 30.7436 tok/s
- versioned files modified: 5
- line delta: +350 / -209
- classification: **FAIL_STARTUP**

## Startup failure

The delivered candidate failed `npm run db:migrate` before the backend could start:

`SequelizeAssociationError: You have used the alias transportista in two separate associations. Aliased associations must have unique aliases.`

The stack pointed to the candidate-modified `backend/src/models/index.js`. This is a candidate-generated startup defect, not an infrastructure failure.

The candidate also created `backend/src/models/Vehiculo.js`, `backend/src/routes/admin/vehicles.js` and `test_models.js`, but the application was not executable, so API/restart/E2E evaluation could not proceed.
