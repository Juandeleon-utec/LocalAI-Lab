# Development Workstation

This machine is distinct from the LocalAI-Lab inference server.

## Role

Primary roles:

- Windows development workstation;
- Visual Studio Code / coding-agent client;
- repository review and manual testing;
- optional BENCH-CODE-001 staging host if the same machine is selected and frozen for all compared candidates.

It must not be confused with the AMD inference server when reporting local LLM hardware or energy measurements.

## Hardware

- CPU: AMD Ryzen 7 5700G
- RAM: 32 GB
- GPU: NVIDIA GeForce GTX 1050, 4 GB VRAM

## Benchmark interpretation

The GTX 1050 is not used for LocalAI-Lab LLM inference. BENCH-CODE-001 candidate applications are Node.js/MySQL workloads and do not require GPU acceleration, so this workstation is technically sufficient for functional staging and manual review.

If it is selected as the formal BENCH-CODE-001 staging host, the exact operating system build, Node.js version, Docker/container-runtime version, MySQL image digest and allocated CPU/RAM must be frozen and recorded before formal runs.

## Separation of roles

```text
Development workstation
Ryzen 7 5700G / 32 GB / GTX 1050
  -> VS Code / OpenCode / Claude Code client
  -> repository interaction
  -> optional staging/manual review

Inference server
Intel i5-14600KF / 64 GB / RX 9060 XT 16 GB
  -> llama.cpp / ROCm
  -> local Qwen inference
  -> local-model telemetry

Benchmark/staging role
  -> fixed host selected before formal runs
  -> Node.js candidate execution
  -> MySQL
  -> external hidden evaluator
```
