#!/usr/bin/env bash
# Read-only prerequisite inspection for Qwen3-4B-Instruct-2507 benchmark.
set -euo pipefail
echo '=== BENCH-QUANT-RAG-001: Qwen preflight ==='
printf 'host: '; hostname
printf 'date_utc: '; date -u +%Y-%m-%dT%H:%M:%SZ
printf 'git_ref: '; git branch --show-current 2>/dev/null || true
printf 'git_sha: '; git rev-parse HEAD 2>/dev/null || true
printf 'python: '; python3 --version
printf 'available_space:\n'; df -h /srv/data "$HOME" 2>/dev/null || true
printf 'rocm_utilities:\n'
command -v rocminfo || true
command -v rocm-smi || true
echo '=== existing llama.cpp installations (limited paths) ==='
for root in "$HOME/llama.cpp" /opt/llama.cpp /srv/llama.cpp /srv/data/llama.cpp "$HOME"/llama.cpp-*; do
  [[ -d "$root" ]] || continue
  printf 'root: %s\n' "$root"
  if [[ -d "$root/.git" ]]; then
    git -C "$root" rev-parse --short HEAD || true
  fi
  for binary in "$root/build/bin/llama-server" "$root/build/bin/llama-quantize" "$root/build/bin/llama-cli" "$root/build/bin/llama-model-loader"; do
    [[ -x "$binary" ]] && printf 'binary: %s\n' "$binary"
  done
  [[ -f "$root/convert_hf_to_gguf.py" ]] && printf 'converter: %s\n' "$root/convert_hf_to_gguf.py"
done
echo '=== llama.cpp currently-running commands (read-only) ==='
ps -eo pid,args | grep -E '[l]lama-server|[l]lama-cli' | cut -c1-230 || true
echo '=== Hugging Face downloader ==='
python3 - <<'PY'
try:
    import huggingface_hub
    print('huggingface_hub:', huggingface_hub.__version__)
except ImportError:
    print('huggingface_hub: not installed in this Python')
PY
echo '=== Qwen official model revision ==='
python3 - <<'PY'
try:
    from huggingface_hub import HfApi
    info=HfApi().model_info('Qwen/Qwen3-4B-Instruct-2507')
    print('model: Qwen/Qwen3-4B-Instruct-2507')
    print('revision:', info.sha)
except Exception as exc:
    print('revision unavailable:',type(exc).__name__,str(exc))
PY
