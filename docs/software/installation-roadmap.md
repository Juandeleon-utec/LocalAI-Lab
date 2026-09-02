# LocalAI-Lab Installation Roadmap

## Purpose

This document defines the reproducible installation sequence for the LocalAI-Lab server. The objective is not only to obtain a functional system, but also to preserve enough technical evidence to reproduce experiments and support future publications.

The installation is intentionally staged. Each phase has prerequisites, validation criteria, and evidence that must be recorded before proceeding.

## Baseline platform

- CPU: Intel Core i5-14600KF
- RAM: 64 GB
- GPU: AMD Radeon RX 9060 XT 16 GB
- GPU architecture: RDNA4 / gfx1200
- OS target: Ubuntu Server 24.04.4 LTS
- GPU compute stack: ROCm 7.2.x initially
- Primary inference engine: llama.cpp with HIP/ROCm

The RX 9060 XT is officially supported by current ROCm releases and is identified as `gfx1200`. Ubuntu 24.04.4 is also a supported ROCm operating system. Exact package versions must be pinned and recorded during installation.

---

# Phase 0 — Firmware and hardware baseline

## Goal

Capture a clean hardware baseline before installing the AI software stack.

## Actions

1. Update motherboard BIOS to a known stable release.
2. Confirm Resizable BAR / Above 4G Decoding state and record it.
3. Confirm XMP memory configuration and memory frequency.
4. Confirm NVMe model and firmware.
5. Confirm GPU model, VBIOS version and PCIe link width.
6. Disable unnecessary motherboard devices only if there is a clear reason.
7. Record ambient temperature when thermal benchmarks are performed.

## Evidence to store

- BIOS version and date
- CPU identification
- RAM size, channels, speed and timings
- motherboard model
- GPU model and VBIOS
- NVMe model and firmware
- PSU model and nominal power

## Exit criterion

Hardware inventory is complete and committed to the repository.

---

# Phase 1 — Operating system installation

## Goal

Install a minimal, stable and reproducible Linux environment.

## Target

Ubuntu Server 24.04.4 LTS.

## Recommended disk layout

The exact size depends on the final NVMe capacity, but separate model/data directories logically from the operating system.

Suggested mount layout:

```text
/
/opt/localai
/var/lib/localai
/srv/models
/srv/datasets
/srv/qdrant
/srv/benchmarks
```

Physical partitions are optional; directories may initially reside on the same filesystem.

## Core packages

Update the linux server
```text
sudo apt update
sudo apt full-upgrade -y
sudo apt autoremove -y
sudo apt autoclean
```

Set time to Montevideo/UY
```text
sudo timedatectl set-timezone America/Montevideo
```

Install only after recording the clean OS state:


```text
openssh-server
curl
wget
git
vim or nano
htop
btop
lm-sensors
pciutils
usbutils
jq
build-essential
cmake
ninja-build
pkg-config
python3
python3-venv
python3-pip
```


Install command line
```text
sudo apt install -y \
git \
curl \
wget \
vim \
nano \
htop \
btop \
tmux \
screen \
tree \
jq \
unzip \
zip \
rsync \
build-essential \
cmake \
pkg-config \
python3 \
python3-pip \
python3-venv \
pciutils \
usbutils \
lshw \
lm-sensors \
smartmontools \
nvme-cli \
net-tools \
iproute2 \
dnsutils
```

Result:

git --version
python3 --version
cmake --version
gcc --version
lspci | head


## Baseline capture

Record at minimum:

```bash
cat /etc/os-release
uname -a
uname -r
lscpu
free -h
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL
lspci -nn
ip addr
```

Save raw output under a dated experiment/baseline directory.

## Exit criterion

- headless boot works;
- SSH access works;
- system reboots cleanly;
- hardware inventory is reproducible;
- no ROCm or LLM software has been installed yet.

---

# Phase 2 — Remote administration and security

## Goal

Make the server remotely manageable before installing the AI workload.

## Components

- OpenSSH
- SSH public-key authentication
- firewall using UFW or nftables
- Fail2ban: optional, especially if SSH is exposed publicly
- Tailscale or WireGuard for remote private access

## Recommended policy

Prefer VPN-only administrative access. Do not directly expose model APIs, Qdrant or Open WebUI to the public Internet.

## Exit criterion

The server can be administered remotely after a reboot without requiring a local monitor or keyboard.

---

# Phase 3 — Monitoring and measurement baseline

## Goal

Install measurement tools before ROCm and inference software so the server can be characterized from the beginning.

## Tools

Initial candidates:

- `lm-sensors`
- `btop`
- `iostat` / `sysstat`
- `smartmontools`
- `time`
- `/usr/bin/time -v`
- AMD ROCm monitoring utilities after ROCm installation

Optional later:

- Prometheus
- node_exporter
- Grafana

Do not deploy the full Prometheus/Grafana stack during initial validation unless required. Raw reproducible measurements are more important than dashboards at this stage.

## Baseline measurements

Capture:

- idle CPU utilization;
- idle RAM utilization;
- GPU idle state when available;
- temperatures;
- storage throughput baseline;
- system power if a reliable external or software measurement is available.

## Exit criterion

A baseline measurement procedure exists before LLM inference is introduced.

---

# Phase 4 — AMD GPU driver and ROCm

## Goal

Validate the RX 9060 XT as a compute device before compiling llama.cpp.

## Initial target

ROCm 7.2.x with the exact patch version selected at installation time and pinned in the experiment metadata.

AMD currently lists the RX 9060 XT as an officially supported RDNA4 GPU with LLVM target `gfx1200`.

## Required validation

Record:

```bash
uname -r
lspci -k | grep -EA3 'VGA|Display'
rocminfo
hipconfig
```

Confirm that the GPU is exposed as:

```text
gfx1200
```

Also capture installed package versions.

## Functional test

Run at least one small HIP/ROCm compute test before installing any LLM.

## Exit criterion

- GPU detected correctly;
- `rocminfo` completes successfully;
- HIP runtime is usable;
- `gfx1200` is confirmed;
- exact ROCm and kernel versions are recorded.

---

# Phase 5 — llama.cpp build and inference baseline

## Goal

Compile the primary inference engine directly against ROCm and establish the first controlled inference benchmark.

## Build principle

Build from a specific git commit, not an unspecified moving `master` state.

The upstream ROCm build configuration currently includes `gfx1200` among supported AMD GPU targets.

Example build strategy:

```bash
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
git checkout <PINNED_COMMIT>
cmake -S . -B build \
  -DGGML_HIP=ON \
  -DAMDGPU_TARGETS=gfx1200 \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
```

The final commands used must be captured verbatim in the repository.

## First benchmark model

Use a small model first. The purpose is to validate the inference path, not model quality.

After the stack is stable, introduce the first Qwen coding model.

## Measurements

Record separately:

- model load time;
- prompt processing / prefill tokens per second;
- generation tokens per second;
- time to first token when measurable;
- total inference time;
- peak RAM;
- peak VRAM;
- GPU utilization;
- CPU utilization;
- GPU temperature;
- power and energy where reliable.

## Exit criterion

A repeatable `llama-bench` / inference run can be executed from a clean reboot and produces machine-readable results.

---

# Phase 6 — Model storage and model registry

## Goal

Avoid unmanaged GGUF files and ensure every benchmark can identify the exact model artifact.

## Proposed directory

```text
/srv/models/
  coding/
  academic/
  embedding/
  reranker/
```

## Metadata per model

Record:

- model name;
- upstream repository;
- revision/tag;
- original precision;
- quantization;
- local filename;
- file size;
- SHA-256 hash;
- license;
- download date.

Do not commit model weights to GitHub.

## Exit criterion

Every model used by LocalAI-Lab has a traceable model manifest.

---

# Phase 7 — OpenAI-compatible inference service

## Goal

Turn llama.cpp into a stable local service that coding agents and research clients can call.

## Initial design

Two mutually exclusive main service profiles:

```text
localai-code.service
localai-research.service
```

Only one large LLM should be loaded at a time initially.

A common API endpoint should be exposed only on localhost or the private VPN interface.

## Required features

- systemd service definitions;
- explicit model path;
- explicit context size;
- explicit GPU offload settings;
- explicit API port;
- restart policy;
- structured log capture.

## Exit criterion

The inference service starts reproducibly after reboot and can be switched manually between coding and research profiles.

---

# Phase 8 — Container runtime

## Goal

Provide isolated deployment for supporting services while keeping the primary inference engine measurable and easy to profile.

## Components

- Docker Engine
- Docker Compose v2

## Design decision

Initially keep `llama.cpp` native/systemd for direct GPU measurements and run auxiliary services in containers.

This avoids containerization becoming an uncontrolled variable in early inference benchmarks.

## Exit criterion

Docker is installed, versions are recorded, and persistent storage locations are explicitly defined.

---

# Phase 9 — Vector database

## Goal

Deploy the persistent storage layer for academic RAG.

## Initial candidate

Qdrant.

Initial self-hosted deployment can use Docker with persistent storage. Qdrant exposes REST on port 6333 and gRPC on 6334 by default. These ports should not be exposed publicly.

## Required validation

- persistent collection survives restart;
- health endpoint works;
- backup/export procedure documented;
- exact image digest or version pinned.

## Exit criterion

Qdrant is persistent, private, version-pinned and backed up.

---

# Phase 10 — Embedding and reranking services

## Goal

Add the retrieval models independently from the main generative LLM.

## Candidates

- Qwen3-Embedding family
- Qwen3-Reranker family

## Evaluation before production

Compare at least two practical configurations if resources permit:

1. embedding only;
2. embedding + reranking.

Record retrieval latency, memory footprint and retrieval quality.

## Exit criterion

The RAG retrieval path is benchmarkable independently from final LLM generation.

---

# Phase 11 — Academic RAG ingestion pipeline

## Goal

Create a traceable path from PDF to evidence-grounded answer.

## Components to implement/evaluate

- PDF text extraction;
- metadata extraction;
- section-aware parsing;
- chunking;
- embedding;
- vector indexing;
- retrieval;
- reranking;
- citation/source reconstruction.

## Reproducibility rule

Do not silently change parsing or chunking strategies. Each experiment must record:

- parser version;
- chunk size;
- chunk overlap;
- embedding model;
- embedding dimensionality;
- retrieval top-k;
- reranker;
- final context top-k.

## Exit criterion

A fixed set of papers can be deleted, re-ingested and produce equivalent indexes and documented evaluation results.

---

# Phase 12 — Research user interface

## Goal

Provide a practical browser interface for research and writing tasks.

## Initial candidate

Open WebUI.

The project officially supports Docker and OpenAI-compatible APIs, which fits the planned llama.cpp service architecture.

## Deployment rules

- pin a stable image version/digest;
- use persistent volumes;
- expose only through VPN or reverse proxy;
- back up application data;
- do not use rolling `main` tags for reproducible production deployments.

## Exit criterion

The UI can query the research model and RAG services without direct public exposure.

---

# Phase 13 — Coding-agent stack

## Goal

Deploy and benchmark local coding agents against the same OpenAI-compatible endpoint.

## Candidates

- OpenCode
- Qwen Code
- Aider

These tools should be evaluated independently before choosing a default.

## Required instrumentation

Capture per task when possible:

- total elapsed time;
- model inference time;
- input/output tokens;
- agent iterations;
- tool calls;
- commands executed;
- files modified;
- tests executed;
- tests passed;
- human intervention.

## Exit criterion

At least one local coding agent can complete a controlled repository task reproducibly.

---

# Phase 14 — Telemetry and benchmark automation

## Goal

Convert manual measurements into machine-readable benchmark records.

## Required output

Prefer JSON/JSONL/CSV raw records that can later be processed into publication tables.

Each run should include an ID such as:

```text
run_YYYYMMDD_model_quant_context_task_repeat
```

## Minimum metadata

- timestamp;
- git commit;
- OS version;
- kernel;
- ROCm version;
- llama.cpp commit;
- model hash;
- model quantization;
- context configuration;
- sampling configuration;
- task ID;
- repetition number;
- timing metrics;
- RAM/VRAM metrics;
- thermal metrics;
- outcome metrics.

## Exit criterion

A complete benchmark can be launched from a script and produces a self-contained result directory.

---

# Phase 15 — Production hardening

## Goal

Move from experimental server to reliable daily-use service without losing reproducibility.

## Components

- backup jobs;
- log rotation;
- health checks;
- disk-space monitoring;
- service restart policies;
- firewall review;
- secrets management;
- documented update policy;
- rollback procedures.

## Important policy

Production updates must not silently invalidate experiments. New ROCm, kernel, inference engine or model versions should create a new documented environment revision.

## Exit criterion

Server can recover from reboot and service failure without manual reconstruction.

---

# Proposed execution schedule

The schedule is milestone-driven rather than calendar-driven. Do not proceed to the next stage until the exit criterion is met.

| Milestone | Main work | Depends on | Expected output |
|---|---|---|---|
| M0 | Hardware/BIOS inventory | Hardware assembled | Hardware baseline |
| M1 | Ubuntu Server installation | M0 | Clean OS baseline |
| M2 | SSH/VPN/security | M1 | Remote headless management |
| M3 | Monitoring baseline | M1 | Idle/system baseline |
| M4 | ROCm validation | M1-M3 | Confirmed gfx1200 compute |
| M5 | llama.cpp | M4 | Reproducible inference baseline |
| M6 | Model registry | M5 | Traceable model artifacts |
| M7 | LLM API/systemd | M5-M6 | Stable code/research services |
| M8 | Docker/Compose | M2 | Auxiliary service runtime |
| M9 | Qdrant | M8 | Persistent vector database |
| M10 | Embeddings/reranker | M4, M9 | Retrieval services |
| M11 | RAG pipeline | M9-M10 | Reproducible paper ingestion |
| M12 | Open WebUI | M7, M11 | Research UI |
| M13 | Coding agents | M7 | Local coding workflow |
| M14 | Automated telemetry | M5-M13 | Publication-ready raw data |
| M15 | Production hardening | all previous | Stable LocalAI-Lab v1 |

## Suggested installation order by practical sessions

### Session 1 — Bare server

M0 → M1 → M2 → M3

Do not install ROCm yet. Capture the clean baseline.

### Session 2 — GPU compute

M4 → small HIP validation → GPU baseline measurements

### Session 3 — Inference engine

M5 → M6 → first small-model benchmark

### Session 4 — Main coding model

M7 → initial Qwen coder → coding inference benchmark

### Session 5 — Supporting infrastructure

M8 → M9 → persistence and backup validation

### Session 6 — Academic retrieval

M10 → M11 → fixed academic-document test corpus

### Session 7 — User interfaces

M12 → M13

### Session 8 — Experimental automation

M14 → repeated benchmarks → statistical analysis workflow

### Session 9 — Production

M15

---

# Versioning policy

For reproducibility, avoid recording only names such as "latest".

Always record exact versions for:

- Ubuntu release;
- kernel;
- AMD GPU driver;
- ROCm;
- Docker;
- container image digest/tag;
- llama.cpp commit;
- model revision and SHA-256;
- Python;
- key Python libraries;
- coding agent version;
- Qdrant;
- Open WebUI.

A software update that can affect performance should be treated as a new experimental environment revision.
