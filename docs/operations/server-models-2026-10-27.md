# Local AI server — operational state and model inventory (27 Oct 2026)

**Status:** snapshot reconstructed from user-provided commands and project notes (24–27 October). This is not a current live health check. All ports below are **historical observations**, not guaranteed simultaneous active listeners.

## Hardware and inference stack

- Host: `ia-server`; Ubuntu 24.04; AMD Radeon RX 9060 XT, nominal 16 GB VRAM; ROCm 10.0; llama.cpp with ROCm acceleration.
- Python/Streamlit academic reviewer interface has been observed on port `8501`.
- Separate llama-server versions/builds were used during the campaign; do not assume all models share one runtime binary.

## Observed configurations

| Model / alias | Quantization | Endpoint / port | Notes |
|---|---|---|---|
| Qwen3 30B-A3B Instruct 2507 / `qwen3-academic` | Q3_K_M | 8090 | Academic LLM endpoint used in reviewer v0.3.2; 8192/32768 context configurations reported at different times. |
| Gemma 4 26B-A4B / `gemma4-academic-q3` | Q3_K_M | 8088 | Reasoning toggled ON/OFF; a separate exploratory Q3 profile served 114688 context in an earlier check. |
| Gemma 4 21B-A4B REAP / `gemma4-reap-q4` | Q4_K_M | 8089 | `/health` and `/models` responded during 25 Oct check; 8192 context reported. |
| Coding Qwen3-Coder profile | Q3_K_M | 8080 | Older published daily coding configuration, managed using OliveTin/systemd; not assumed running on 27 Oct. |

Observed 25 Oct: port 8088 was unavailable while 8089 responded. On the REAP check, model `gemma4-reap-q4` was returned by `/models`.

## REAP exploratory telemetry

- GPU: RX 9060 XT; `llama.cpp` build reported as 11675; ROCm 10.0.
- Context: 8192 tokens; VRAM observation: approximately 14,194 MB occupied of 16,304 MB reported; generation ~55.85 tok/s.
- **Not** a formal, controlled head-to-head benchmark; mark as exploratory.

## Local startup artifacts (not uploaded)

- `iniciar_v032.sh`: original academic-reviewer Qwen startup script.
- `iniciar_v032_gemma.sh`: Gemma-specific reviewer startup script discussed/tested.
- `iniciar_web.sh`: Streamlit launcher.
- Aliases, server arguments, process-manager configuration and definitive working shell contents must be copied from the server and checked before these can be promoted to deployable repo scripts.

## Operational checks

```bash
for port in 8080 8088 8089 8090; do
  echo "--- $port ---"
  curl -fsS --max-time 2 "http://127.0.0.1:$port/health" || true
  echo
  curl -fsS --max-time 2 "http://127.0.0.1:$port/models" || true
  echo
done
curl -I --max-time 3 http://127.0.0.1:8501 || true
```

Do not publish API keys, unpublished document contents, private PDF documents or run payloads that include user data.

## Verified terminal inventory addendum — 2026-10-28

A supplied terminal inventory identifies the previously unlisted REAP GGUF at:
`/srv/data/models/gemma4-21b-reap/gemma-4-21b-a4b-it-REAP-Q4_K_M.gguf` — **13,832,449,920 bytes**.
This is outside `/srv/models`; the earlier inventory's absence was a search-scope limitation, not evidence that the file was missing.

Script extracts (not complete files) establish the following configurations:

| Script | Model path / alias | LLM port | Other observed settings |
|---|---|---:|---|
| `iniciar_v032.sh` | academic Qwen3 30B Q3 / `qwen3-academic` | 8090 | `-c 8192 -np 1 -ngl 99 --jinja --temp 0.1 --top-p 0.8 --metrics` |
| `iniciar_v032_gemma.sh` | Gemma4 26B Q3 / `gemma4-academic-q3` | 8088 | temp 0.1, top-p 0.8, metrics; API 8000, UI 8501 |
| `iniciar_v032_gemma_21.sh` | REAP 21B Q4 / `gemma4-REAP-Q4` | 8088 | temp 0.1, top-p 0.8, metrics; API 8000, UI 8501 |
| `iniciar_v032_reap.sh` | unknown | unknown | no matching lines in the grep output; inspect full content before drawing conclusions |
| `iniciar_web.sh` | loaded from current environment | unspecified | checks model endpoint and launches Streamlit UI |

The Gemma scripts use `llama.cpp-gemma4-lab/build-rocm/bin/llama-server`; the Qwen script uses `llama.cpp/build-rocm/bin/llama-server`. The Gemma scripts also manage the API and UI and attempt to free Qwen on 8090 where appropriate. The REAP script shown here uses 8088, **different from a previous REAP observation on 8089**; preserve both as distinct historical configurations. The grep excerpts alone do not prove flags omitted from the filtered output are absent.

**Warning:** these details are based on supplied `grep` extracts, not copies of the full startup scripts or a current process snapshot. They are not safe deployment templates without validation.
