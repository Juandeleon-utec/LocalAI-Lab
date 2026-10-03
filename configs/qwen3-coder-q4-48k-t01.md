# Qwen3-Coder Q4_K_M — 48K daily profile

Current daily/experimental coding-agent configuration.

```bash
export LD_LIBRARY_PATH=/opt/rocm/core-10.0/lib
cd ~/llama.cpp

./build-rocm/bin/llama-server \
  -m /srv/models/coding/qwen3-coder-30b-a3b-q4/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --alias qwen3-coder-q4 \
  -c 49152 \
  -np 1 \
  --fit on \
  --fit-target 1024 \
  --jinja \
  --metrics \
  --temp 0.1 \
  --api-key <LOCAL_API_KEY>
```

OpenCode limits:

- model: `local/qwen3-coder-q4`
- context: 49,152
- output: 8,192
- temperature: 0.1
- agent/mode used in current tests: Build

Do not commit real API keys, LAN credentials or secrets.
