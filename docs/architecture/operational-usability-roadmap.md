# Operational Usability and Reproducibility Roadmap

**Status:** Planned implementation  
**Scope:** LocalAI-Lab server usability, service control, academic project workflow and benchmark hygiene.

## Objective

LocalAI-Lab should satisfy two requirements at the same time:

1. remain a measurable and reproducible experimental platform;
2. be practical enough for normal daily use without reconstructing long shell commands or relying on SCP for routine work.

The operational layer must therefore improve convenience without becoming hidden experimental state.

## Target architecture

```text
                           Browser / workstation
                                  |
             +--------------------+--------------------+
             |                    |                    |
          OliveTin             Open WebUI          File manager
          control              chat / RAG          project files
             |                    |                    |
             |                    |              /srv/data/projects/
             |                    |
             |              +-----+------+
             |              |            |
             |          llama.cpp      Ollama
             |              |
             +---------- systemd / versioned wrappers
                            |
                    AMD Radeon RX 9060 XT
```

Initial implementation candidates:

- **OliveTin** — lightweight operational control panel;
- **Open WebUI** — local-model chat and convenience Knowledge/RAG interface;
- **Copyparty** — lightweight browser-based project/file management;
- **systemd + repository-versioned wrapper scripts** — process lifecycle and reproducible service profiles.

A custom web application is intentionally deferred. It should only be introduced if the lightweight components become a demonstrated limitation.

## Design principles

### Usability

A normal session should not require remembering model launch commands, process IDs or SCP syntax.

### Reproducibility

A convenient button must ultimately call a versioned configuration or script. Formal benchmark commands and frozen artifacts remain authoritative.

### Separation of concerns

- OliveTin controls processes and operational actions.
- Open WebUI provides interactive chat/document convenience.
- Browser file management handles project files.
- Formal benchmark/RAG runners remain separate from convenience interfaces.

### One large GPU model at a time

Starting another large model should use a controlled transition:

```text
STOP current model
-> verify process termination
-> verify VRAM release
-> START requested model
-> health/readiness check
-> READY
```

## Planned filesystem layout

```text
/srv/data/projects/
  <project>/
    sources/
    notes/
    extracted/
    index/
    output/
```

The source directory is user-controlled input. Generated extraction/index data and final outputs should remain separated.

## Planned repository layout

Candidate structure:

```text
configs/
  olivetin/
  open-webui/

services/
  systemd/
  profiles/

scripts/
  localai-start-profile
  localai-stop-profile
  localai-switch-profile
  localai-create-project
  localai-index-project
  localai-benchmark-preflight
```

Exact names may change during implementation; the key requirement is that operational configuration remains versioned.

## Implementation checklist

### A. Service wrappers

- [ ] Inventory currently validated manual launch commands.
- [ ] Create one versioned profile per validated `llama-server` configuration.
- [ ] Create systemd unit or wrapper for Qwen3-Coder.
- [ ] Create systemd unit or wrapper for Qwen3.6.
- [ ] Add Ollama lifecycle control.
- [ ] Add JupyterLab lifecycle control.
- [ ] Add status/health commands.
- [ ] Add recent-log commands.
- [ ] Verify clean VRAM release on stop.
- [ ] Prevent accidental concurrent loading of incompatible large models.

### B. OliveTin

- [ ] Install OliveTin.
- [ ] Bind initially to the trusted LAN only.
- [ ] Enable authentication.
- [ ] Version `config.yaml`.
- [ ] Add start/stop/status/log buttons for validated model profiles.
- [ ] Add Ollama buttons.
- [ ] Add Jupyter buttons.
- [ ] Add GPU, VRAM, RAM, disk and port checks.
- [ ] Add STOP ALL.
- [ ] Add safe model-switch actions.
- [ ] Add benchmark-preflight action.
- [ ] Restrict sudo to narrowly scoped commands/scripts.

### C. Open WebUI

- [ ] Deploy Open WebUI.
- [ ] Connect it to `llama-server` using the OpenAI-compatible API.
- [ ] Connect it to Ollama.
- [ ] Validate model selection.
- [ ] Create an Academic Reviewer convenience profile.
- [ ] Keep benchmark prompts independent from this profile.
- [ ] Validate document upload.
- [ ] Validate persistent Knowledge collections.
- [ ] Validate source/citation visibility.
- [ ] Determine which Open WebUI processing steps must be recorded before any formal quality experiment uses it.

### D. Browser file/project management

- [ ] Deploy Copyparty or equivalent maintained lightweight file manager.
- [ ] Restrict visible/writeable roots.
- [ ] Expose `/srv/data/projects/`.
- [ ] Enable authenticated project-folder creation.
- [ ] Validate drag-and-drop file upload.
- [ ] Validate upload of PDF, DOCX, BibTeX, Markdown and datasets.
- [ ] Keep system/model directories inaccessible from the normal file UI.

### E. Project creation

- [ ] Implement `localai-create-project <name>`.
- [ ] Validate project names against path traversal and shell injection.
- [ ] Create the standard project directory structure.
- [ ] Expose project creation as an OliveTin action.
- [ ] Decide whether project metadata should include a small manifest.

### F. Project indexing

- [ ] Implement `localai-index-project <name>`.
- [ ] Inventory files and hashes before ingestion.
- [ ] Avoid reprocessing unchanged files where practical.
- [ ] Preserve source path and document identity.
- [ ] Preserve page/section metadata for academic traceability.
- [ ] Add project Knowledge collection creation/update.
- [ ] Add index status action.
- [ ] Keep convenience Open WebUI indexes separate from frozen formal RAG indexes.

### G. Academic Reviewer workflow

Target daily flow:

```text
1. Browser -> create project
2. Browser -> upload papers/documents
3. OliveTin -> index project
4. Open WebUI -> choose Academic Reviewer
5. Open WebUI -> choose project Knowledge
6. Ask questions / review / compare documents
7. Preserve useful outputs under project output/
```

Acceptance checks:

- [ ] Ask a question grounded only in uploaded sources.
- [ ] Identify the source document supporting the answer.
- [ ] Test a question whose answer is absent and verify that the workflow does not confidently invent it.
- [ ] Compare information across at least two project documents.
- [ ] Validate handling of an updated/replaced source file.
- [ ] Preserve enough metadata to later reproduce a formal version of the workflow if desired.

### H. Laboratory vs benchmark mode

#### Laboratory mode

Convenience services may be active:

- OliveTin;
- Open WebUI;
- Copyparty;
- Ollama;
- JupyterLab;
- manually selected model services.

#### Benchmark mode

Formal experiments should use:

- exact frozen model/configuration;
- exact launch command/profile hash;
- clean runtime checks;
- known ports;
- no residual containers/processes;
- explicit GPU state;
- run-specific telemetry;
- immutable task inputs;
- independent evaluation after candidate freeze.

Checks:

- [ ] Implement a benchmark preflight script.
- [ ] Detect listeners on benchmark-sensitive ports.
- [ ] Detect residual containers.
- [ ] Detect stale model processes.
- [ ] Record active services.
- [ ] Confirm GPU availability.
- [ ] Do not allow convenience interfaces to rewrite frozen benchmark files.
- [ ] Preserve contamination findings as experimental evidence rather than hiding them.

## Usability metrics

Efficiency is not only tokens/s. The operational platform should also measure selected human-workflow costs when useful:

- number of terminal commands required;
- number of manual steps to switch workloads;
- time to start a validated model;
- time to create and populate a project;
- time to switch from document upload to first grounded query;
- number of undocumented/manual corrections required;
- recovery steps after a failed service start.

These measurements are secondary to formal model-quality metrics but useful for judging whether the local platform is practically usable.

## Near-term implementation order

1. Create stable service wrappers for validated `llama-server` profiles.
2. Install and configure OliveTin.
3. Add status/health/GPU controls and safe model switching.
4. Deploy Open WebUI and validate chat against `llama-server`.
5. Add browser file/project management.
6. Standardize `/srv/data/projects/<project>/`.
7. Implement create-project and index-project scripts.
8. Connect project sources to convenience Knowledge/RAG.
9. Validate Academic Reviewer workflow.
10. Add benchmark-preflight/clean-state workflow.
11. Only then consider a custom unified UI if the lightweight stack is insufficient.

## Success criterion

The operational layer is successful when the server can be used comfortably from a browser for normal work while a formal benchmark can still be reproduced from explicit, versioned and auditable inputs without depending on hidden state created by those convenience tools.
