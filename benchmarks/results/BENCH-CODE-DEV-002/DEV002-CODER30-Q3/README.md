# DEV002-CODER30-Q3

- model: Qwen3-Coder-30B-A3B-Instruct Q3_K_M
- OpenCode model id: `local/qwen3-coder`
- context: 49,152
- wall time: 535.188 s (recovered post-run timing)
- official main: 14/18
- official critical: 11/15
- audited main: 12/18
- audited critical: 10/15
- restart: 1/2
- E2E: 1/6
- prompt tokens: 55,204
- generated tokens: 13,947
- prompt processing: 656.087 tok/s
- generation: 36.2531 tok/s
- files modified: 4
- line delta: +201 / -56
- classification: FAIL

## Provenance note

The model inference completed, but the then-current runner aborted during post-agent Git evidence capture because a CRLF warning on stderr was treated as a PowerShell native-command error. The model was **not rerun**. Post-processing and evaluation were recovered from the preserved candidate, and `agent_exit_code` was not invented.

## Root findings

Create/update/delete and validation behavior were substantially functional, but the vehicle list returned HTTP 500 and GET-by-id was absent. The restart persistence check was therefore inconclusive because it depended on the broken list route.

This run tied Coder-Next on audited API quality while using less wall time and fewer prompt tokens, giving the best quality/efficiency trade-off among the tested completed candidates.
