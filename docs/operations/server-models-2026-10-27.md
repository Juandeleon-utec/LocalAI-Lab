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
