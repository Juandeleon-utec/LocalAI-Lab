# Qwen3-Coder Q3 daily profile and OpenCode policy — 2026-10-08

## Scope

This records the **currently reported operational configuration**, not a new formal benchmark.
It supersedes the previous Q4/48K/t0.1 *daily-use recommendation* in the README; it does **not** rewrite or invalidate frozen BENCH-CODE-001 / BENCH-CODE-DEV-002 runs or their manifests.

- Inference: llama.cpp ROCm (`/home/jpdeleon/llama.cpp/build-rocm/bin/llama-server`)
- Model: `/srv/models/coding/qwen3-coder-30b-a3b/Qwen3-Coder-30B-A3B-Instruct-Q3_K_M.gguf`
- Server API alias: `qwen3-coder`
- API: `0.0.0.0:8080`, OpenAI-compatible `/v1/chat/completions`
- Backend: `LD_LIBRARY_PATH=/opt/rocm/core-10.0/lib`
- Memory/context: `--fit on --fit-target 1024 -c 114688 -np 1`
- Chat templates and telemetry: `--jinja --metrics`
- Sampling defaults: `--temp 0.7 --top-p 0.8 --top-k 20 --repeat-penalty 1.05`
- Lifecycle: `llama-qwen-coder.service`, started/stopped using OliveTin; OliveTin controls systemd, not the prompt.
- API authentication: enabled. **Never commit the actual API key.**

The 114,688-token setting is a requested upper context limit; `--fit` may adjust effective allocation. Client request parameters can override server sampling defaults.

## Source files in this repository

- `services/systemd/llama-qwen-coder.service`: shareable systemd template with external key.
- `prompts/coding/qwen-coding-policy-v1.2.md`: policy text to copy into the **application repository** as `AGENTS.md`.
- This document: explanation and checks.

## Installing/updating the service on Linux

The running user's service had the API key directly in `ExecStart`. The committed template avoids publishing it. The existing service is **not** changed merely by pulling Git.

Create a private file and insert your real key locally (do not commit it):

```bash
sudo install -d -m 700 /etc/localai
sudo install -m 600 /dev/null /etc/localai/llama-qwen-coder.env
sudo nano /etc/localai/llama-qwen-coder.env
```

The file must contain one line: `LOCALAI_API_KEY=<your-existing-secret>`.

Check the template's paths and service account before installing it. Then:

```bash
sudo install -m 644 services/systemd/llama-qwen-coder.service /etc/systemd/system/llama-qwen-coder.service
sudo systemctl daemon-reload
sudo systemctl restart llama-qwen-coder.service
sudo systemctl status llama-qwen-coder.service --no-pager
sudo systemctl show llama-qwen-coder.service -p ExecStart
journalctl -u llama-qwen-coder.service -n 80 --no-pager
```

If OliveTin already controls `llama-qwen-coder.service`, it continues to control that unit; no OliveTin change is needed merely to update the unit. If you wish to start via OliveTin, reload systemd and stop the old process, then use the existing OliveTin Start action. Keep API port 8080 accessible only on trusted networks; `0.0.0.0` exposes it on all interfaces.

Validate locally:

```bash
curl -H "Authorization: Bearer $LOCALAI_API_KEY" http://127.0.0.1:8080/health
```

(The shell variable must be set in the invoking shell; merely adding the EnvironmentFile to systemd does not export it there.)

## OpenCode / VS Code

Copy `prompts/coding/qwen-coding-policy-v1.2.md` to **`AGENTS.md` at the root of each application repository** using OpenCode, such as `tabacalera-app/AGENTS.md`. Do not confuse this policy with `llama-server` startup arguments. In the verified setup, OpenCode reads the project `AGENTS.md`; the server does not inject the policy globally and no `opencode.json` edit is needed for `AGENTS.md` discovery.

Observed manual checks, from the user's OpenCode console:
- Policy identifier `QWEN-CODING-POLICY-V1` was recognized with v1.
- After the file was saved and updated, the agent explicitly read `AGENTS.md` and identified v1.1 and then v1.2.
- Under v1.2 the agent inspected `app/package.json`, `backend/package.json`, entry points, README and selected Sequelize model files, and searched for tests.
- It completed a read-only architecture task without observed file modifications.
- Earlier runs had unsupported database inferences; v1.2 prioritizes verified repository evidence.
- These are **qualitative smoke tests**, not evidence of improved coding functional success or controlled A/B measurements.

Sanity prompt (new OpenCode session):

```text
What is your active coding policy identifier?
Respond with the exact identifier only.
```

Expected: `QWEN-CODING-POLICY-V1.2`.

## Reproducibility note

The operational context and sampling settings differ materially from earlier formal benchmark configurations. A benchmark must capture its own exact service flags, model checksum, agent settings, policy content/hash, context, temperature, tool trace and evaluator results. Do not retrospectively associate v1.2 with historical runs.
