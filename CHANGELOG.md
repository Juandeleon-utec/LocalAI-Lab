# Changelog

All notable changes to LocalAI-Lab will be documented here.

## [Unreleased] - 2026-09-02

### Added

- Formal benchmark **LAILAB-B002** for Qwen3-Coder-30B-A3B-Instruct Q3_K_M on the Radeon RX 9060 XT.
- Persistent storage layout using dedicated SSD mount points:
  - `/srv/models` for coding, academic, embedding, and reranker models.
  - `/srv/data` for datasets, papers, Qdrant data, benchmarks, and backups.
- Manual `llama-server` deployment using the validated Qwen3-Coder model.
- OpenAI-compatible API exposed over the local network for development testing.
- API-key authentication for the LAN validation endpoint.
- Windows + Visual Studio Code client validation.
- OpenCode 1.18.27 installation and connection to the local `llama-server` backend.
- End-to-end agent validation documentation under `docs/agents/`.
- Controlled repository-write validation from OpenCode.
- Local Python virtual environment and pytest setup for agent experiments.

### Validated

- Qwen3-Coder-30B-A3B-Instruct Q3_K_M reaches approximately 69.1 tok/s TG128 in direct `llama-bench` testing.
- The same model reaches approximately 64.2 tok/s in a small OpenAI-compatible API request from the Windows workstation.
- LAN communication between the Windows development workstation and the Ubuntu inference server.
- OpenCode repository exploration and multi-tool execution.
- OpenCode reasoning over B001 and B002 benchmark records.
- OpenCode creation of files inside a controlled experiment directory.

### Pending

- Capture a successful agent-driven pytest run.
- Validate a complete autonomous edit-test-fix-retest loop.
- Add systemd service management after manual benchmark validation is complete.
- Configure backup automation.
- Evaluate Qwen Code and Aider against the same backend.

## [0.1.0] - 2026-08-29

### Added

- Project name defined as **LocalAI-Lab**.
- Private GitHub repository initialized.
- Initial hardware platform defined:
  - Intel Core i5-14600KF
  - 64 GB RAM
  - AMD Radeon RX 9060 XT 16 GB
- Ubuntu Server 24.04 LTS selected as initial operating-system candidate.
- ROCm selected as GPU compute platform.
- `llama.cpp` selected as initial inference-engine candidate.
- Two operating profiles defined: coding and academic research/RAG.
- Qwen3-Coder family selected as initial coding-model candidate.
- Qwen3 family and alternative models identified for academic evaluation.
- Qwen3-Embedding and Qwen3-Reranker families identified as RAG candidates.
- Reproducibility, telemetry and future publication potential established as project requirements.
