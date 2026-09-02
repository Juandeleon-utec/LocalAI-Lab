# Model Integration and Project Onboarding Guide

**Project:** LocalAI-Lab  
**Purpose:** Repeatable procedure for adding a new local GGUF model to the LocalAI-Lab server, exposing it through `llama-server`, connecting it to OpenCode on a Windows/Visual Studio Code workstation, and validating it against an existing software project.

## 1. Scope

This guide is intended for two recurring scenarios:

1. **Add or replace a coding model** on the Ubuntu/ROCm inference server.
2. **Bring an existing development project** into the local coding-agent workflow and compare the local model against a previous hosted-agent workflow.

The current validated reference architecture is:

```text
Windows workstation
└── Visual Studio Code
    └── OpenCode
        └── OpenAI-compatible HTTP API over LAN
            └── llama-server
                └── GGUF coding model
                    └── llama.cpp HIP / ROCm 10
                        └── AMD Radeon RX 9060 XT 16 GB
```

The reference model used during initial validation is Qwen3-Coder-30B-A3B-Instruct Q3_K_M.

---

## 2. Preconditions

Before integrating a new model, confirm that the base server remains healthy.

### Server

```bash
rocminfo | grep -E "Name:|gfx"
~/llama.cpp/build-rocm/bin/llama-cli --list-devices
```

Expected GPU class:

```text
AMD Radeon RX 9060 XT
gfx1200
```

Restore the ROCm development environment after login/reboot if required:

```bash
source ~/rocm10-devel/bin/activate

export ROCM_ROOT="$(rocm-sdk path --root)"
export ROCM_BIN="$(rocm-sdk path --bin)"
export HIP_PATH="$ROCM_ROOT"
export HIP_PLATFORM=amd
export PATH="$ROCM_BIN:$PATH"

SP="$HOME/rocm10-devel/lib/python3.12/site-packages"
export LD_LIBRARY_PATH="$SP/_rocm_sdk_core/lib:$SP/_rocm_sdk_libraries/lib:${LD_LIBRARY_PATH:-}"
```

### Storage

Models are stored under:

```text
/srv/models/
```

Recommended layout:

```text
/srv/models/
├── coding/
├── academic/
├── embeddings/
└── rerankers/
```

Verify mounts before downloading large models:

```bash
findmnt /srv/models
findmnt /srv/data
df -h /srv/models /srv/data
```

---

## 3. Selecting a new model

Record at minimum:

- model family and exact variant;
- model repository;
- GGUF filename;
- quantization;
- file size;
- total parameters;
- architecture type: dense or MoE;
- stated context length;
- license;
- expected tool/function-calling support;
- reason for selecting it.

For a 16 GB GPU, do not decide only from GGUF file size. Runtime memory also includes KV cache, compute buffers, graph memory, and other allocations.

A model close to the VRAM limit should be tested with conservative context length first.

### Recommended first-pass quantization strategy

For coding workloads:

- prefer Q4_K_M when it fits with useful context headroom;
- consider Q3_K_M for larger models when the lower quantization permits substantially more GPU residency;
- avoid assuming that a larger quantization will be faster if it forces significant CPU/RAM offload;
- benchmark both prompt processing and token generation before selecting the operational model.

---

## 4. Downloading the GGUF model

Create a dedicated directory:

```bash
mkdir -p /srv/models/coding/<model-directory>
```

Use the current Hugging Face CLI:

```bash
hf download \
  <owner>/<repository> \
  --include "<exact-model-file>.gguf" \
  --local-dir /srv/models/coding/<model-directory>
```

Before a large download, a dry run is recommended:

```bash
hf download <owner>/<repository> --dry-run
```

This verifies the actual filenames and prevents assumptions based on repository documentation or external mirrors.

After download:

```bash
ls -lh /srv/models/coding/<model-directory>
```

Optional reproducibility record:

```bash
sha256sum /srv/models/coding/<model-directory>/<exact-model-file>.gguf
```

Store the hash in the benchmark or model baseline document.

---

## 5. First local model load

Do not expose the model over the network immediately. First validate direct inference with `llama-cli`.

```bash
cd ~/llama.cpp

./build-rocm/bin/llama-cli \
  -m /srv/models/coding/<model-directory>/<exact-model-file>.gguf \
  --fit on \
  --fit-target 1024 \
  -c 4096 \
  -n 256 \
  -p "Write a small Python function with type hints, validation, a docstring, and unit tests."
```

Capture:

- successful model load;
- model size and quantization;
- GPU/CPU offload information if available;
- peak VRAM;
- prompt throughput;
- generation throughput;
- GPU temperature;
- GPU power;
- obvious output-quality issues.

Monitor the GPU from another terminal during load and generation:

```bash
watch -n 0.5 amd-smi
```

---

## 6. Formal inference benchmark

Run repeatable benchmark workloads before promoting the model to coding-agent use.

### Prompt processing and generation

```bash
./build-rocm/bin/llama-bench \
  -m /srv/models/coding/<model-directory>/<exact-model-file>.gguf \
  --fit-target 1024 \
  -p 512 \
  -n 128 \
  -r 5
```

### Combined workload

```bash
./build-rocm/bin/llama-bench \
  -m /srv/models/coding/<model-directory>/<exact-model-file>.gguf \
  --fit-target 1024 \
  -pg 512,128 \
  -r 5
```

Create a new benchmark ID, for example:

```text
LAILAB-B003
```

Record exact `llama.cpp` commit, ROCm version, kernel, model hash, command line, VRAM, temperature, power and test repetition count.

---

## 7. Exposing the new model with llama-server

Start manually during validation. Do not create `systemd` services until the model configuration is stable.

Example:

```bash
cd ~/llama.cpp

./build-rocm/bin/llama-server \
  -m /srv/models/coding/<model-directory>/<exact-model-file>.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --alias <model-alias> \
  --fit on \
  --fit-target 1024 \
  -c 8192 \
  --jinja \
  --api-key <development-api-key>
```

### Notes

- `--host 0.0.0.0` is required for LAN access.
- `--alias` should be short and stable because clients refer to this value as the model ID.
- `--jinja` is recommended for models used by agents and tool/function calling.
- begin with a conservative context length such as 8192 and increase only after measuring VRAM and stability;
- the development API key is appropriate for LAN validation only and must not be reused for an Internet-exposed endpoint.

---

## 8. API validation from Windows

From Windows PowerShell or CMD:

```bat
curl http://<server-ip>:8080/v1/models -H "Authorization: Bearer <development-api-key>"
```

Then test chat completion:

```bat
curl http://<server-ip>:8080/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer <development-api-key>" ^
  -d "{\"model\":\"<model-alias>\",\"messages\":[{\"role\":\"user\",\"content\":\"Write a Python function with type hints and tests.\"}],\"max_tokens\":512,\"temperature\":0.2}"
```

Confirm:

- HTTP request succeeds;
- authentication succeeds;
- returned `model` matches the configured alias;
- output is complete;
- server-side generation speed remains close to direct inference benchmark results.

---

## 9. Connecting OpenCode to the new model

OpenCode runs on the Windows development machine while inference remains on the Linux server.

### Install/verify OpenCode

```powershell
npm install -g opencode-ai
opencode --version
```

### Project-local configuration

Create `opencode.json` in the project root. Replace alias, URL and context values as needed.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "local/<model-alias>",
  "provider": {
    "local": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LocalAI-Lab",
      "options": {
        "baseURL": "http://<server-ip>:8080/v1",
        "apiKey": "<development-api-key>"
      },
      "models": {
        "<model-alias>": {
          "name": "<human-readable-model-name>",
          "limit": {
            "context": 8192,
            "output": 4096
          }
        }
      }
    }
  }
}
```

Keep the OpenCode context limit aligned with the context configured in `llama-server`.

Start the agent from the project directory:

```powershell
opencode
```

---

## 10. New-project onboarding procedure

Use this procedure before allowing the agent to make broad changes to an existing software project.

### Step 1 — Protect the existing project

Ensure the project is under Git version control.

```powershell
git status
git branch --show-current
```

Create a dedicated experiment branch:

```powershell
git switch -c experiment/localai-agent
```

Do not test directly on the production/default branch.

### Step 2 — Ask for inspection only

First prompt:

```text
Inspect this repository and explain:
- application purpose;
- technology/framework;
- project structure;
- build process;
- local database technology;
- major dependencies;
- QR scanning implementation;
- risks or missing information.

Do not modify any files.
```

The purpose is to determine whether the model correctly understands the existing codebase before it is allowed to edit it.

### Step 3 — Establish a baseline build

Before asking the agent to change code, run the project's normal build/tests manually and record the result.

Examples depend on the mobile framework:

```text
Flutter        -> flutter test / flutter build apk
React Native   -> npm test / Gradle build
Android/Kotlin -> ./gradlew test / ./gradlew assembleDebug
.NET MAUI      -> dotnet test / dotnet build
```

A failed baseline must not later be attributed to the local model.

### Step 4 — Small controlled modification

Ask for one bounded change with explicit constraints.

Example:

```text
Add a duplicate-detection rule before saving a scanned QR code.
If the same value already exists in the local database, show a user-visible warning and do not create another row.

Before editing, explain which files you intend to modify.
Then implement the change, run the relevant tests/build command, and summarize the result.
Do not refactor unrelated code.
```

### Step 5 — Review Git changes

```powershell
git status
git diff
```

Check for:

- unexpected file rewrites;
- dependency changes;
- formatting churn;
- generated files;
- security-sensitive changes;
- deletion of existing behavior.

### Step 6 — Validate on emulator/device

For mobile applications, unit tests alone are not sufficient. Test at minimum:

1. camera permission flow;
2. QR detection;
3. storage of scanned value;
4. app restart and persistence;
5. duplicate behavior;
6. malformed QR content;
7. empty/rapid repeated scans;
8. local database migration behavior if schema changes were made.

---

## 11. Suggested first real-world experiment: QR mobile application

An existing simple mobile application that scans QR codes and stores them in a local database is an appropriate first real project because it has a clear input/output workflow and limited scope.

### Existing workflow to reproduce

The previous development workflow was approximately:

```text
Claude chat
    ↓ generates/suggests code
Claude Code
    ↓ applies/organizes code in repository
Mobile app build/test
```

The LocalAI-Lab experiment changes this to:

```text
Developer / VS Code
    ↓
OpenCode
    ↓ tool calls, repository reads/writes, build commands
llama-server over LAN
    ↓
Local coding model on RX 9060 XT
```

### Phase A — Understanding test

Ask OpenCode:

```text
Analyze this mobile application without modifying it.
Explain how QR scanning works, where scanned values are persisted, the local database schema, and the complete data flow from camera scan to stored record.
Identify the files responsible for each stage.
```

Score manually:

- correct framework identification;
- correct database identification;
- correct QR library identification;
- correct file/data-flow identification;
- hallucinated components;
- number of tool calls;
- elapsed time.

### Phase B — Controlled feature

A good first feature is:

```text
Add a scan-history screen showing the locally stored QR values sorted by most recent first.
Do not change the QR scanning behavior.
Do not replace the existing database library.
Use the project's existing architecture and style.
Run the available tests/build after the change.
```

This tests repository understanding, UI code, database queries, navigation and build tooling without requiring a major redesign.

### Phase C — Functional modification

Second feature:

```text
Prevent duplicate QR values from being saved within a configurable time window.
Show a clear message when the scan is ignored as a duplicate.
Preserve all existing stored data.
Add tests where the framework makes this practical.
```

### Phase D — Comparison with the previous Claude-generated implementation

For a meaningful comparison, evaluate the same task using the existing application state or equivalent Git commit.

Record:

| Metric | Local Qwen/OpenCode | Previous Claude workflow |
|---|---:|---:|
| Task completed | | |
| Build succeeded | | |
| Tests passed | | |
| Human corrections | | |
| Files changed | | |
| Tool calls | | |
| Wall-clock time | | |
| Prompt/input tokens | | |
| Generated tokens | | |
| GPU peak VRAM | | N/A |
| GPU power/temperature | | N/A |
| Functional defects | | |
| Code-quality observations | | |

Avoid comparing only subjective code style. Build success, functional correctness and required human intervention are more useful engineering metrics.

---

## 12. Model replacement checklist

Before declaring a new model operational:

- [ ] Exact GGUF file identified and downloaded to `/srv/models`.
- [ ] SHA-256 recorded.
- [ ] License recorded.
- [ ] Direct `llama-cli` inference succeeds.
- [ ] VRAM peak measured.
- [ ] GPU temperature/power observed.
- [ ] PP512 and TG128 benchmarked.
- [ ] Combined benchmark recorded.
- [ ] `llama-server` starts successfully.
- [ ] `/v1/models` succeeds from Windows.
- [ ] `/v1/chat/completions` succeeds from Windows.
- [ ] OpenCode connects using the new alias.
- [ ] Repository read-only inspection succeeds.
- [ ] Controlled file write succeeds.
- [ ] Project baseline build is recorded.
- [ ] Agent-driven project build/test succeeds.
- [ ] At least one real task is completed.
- [ ] Results are stored as a new LocalAI-Lab experiment/benchmark.

---

## 13. Rollback procedure

If a model or agent experiment becomes unstable:

1. Stop `llama-server` with `Ctrl+C`.
2. Restart the previously validated model using its known command line.
3. On the Windows repository, inspect changes:

```powershell
git status
git diff
```

4. Preserve useful experimental results before discarding changes.
5. Return to the pre-experiment branch/commit as appropriate.

Do not delete a failed experiment without recording why it failed. Negative results are useful for model selection and reproducibility.

---

## 14. Documentation rule

Every model promoted into LocalAI-Lab should have two records:

1. **Inference benchmark** — throughput, memory, power, software versions and exact model artifact.
2. **Task-level agent evaluation** — real repository task, build/tests, tool calls, human intervention and correctness.

A fast model is not automatically a good coding agent. Model selection should ultimately be based on both inference efficiency and task completion quality.
