# Documented retry / invalid-attempt notes

## Qwen3.6-35B Q4 — attempt 1

The first Qwen3.6 attempt produced a llama.cpp context error:

`request (52229 tokens) exceeds the available context size (49152 tokens)`

The fixed benchmark context budget was not increased. The attempt was preserved as `ATTEMPT1-CONTEXT-OVERFLOW`, the server/runtime state was cleaned, and a single explicitly named R2 run was executed under the same 49,152-token limit.

R2 completed without context overflow and is the run used in the consolidated comparison. The retry is disclosed because context-management behavior is itself relevant evidence.
