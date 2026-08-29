# Hardware Platform

## CPU

Intel Core i5-14600KF.

## Memory

64 GB system RAM.

System memory is important because LocalAI-Lab may evaluate models whose quantized footprint exceeds the available GPU VRAM. Partial CPU/RAM offload will therefore be measured explicitly rather than treated as an implementation detail.

## GPU

AMD Radeon RX 9060 XT, 16 GB VRAM.

Primary compute stack: ROCm / HIP.

## Baseline measurements to record

Before model benchmarking, record:

- BIOS version;
- CPU microcode/kernel version;
- RAM configuration and speed;
- GPU model and firmware information;
- ROCm and driver version;
- idle RAM/VRAM usage;
- idle power consumption where measurable;
- temperatures and fan behavior;
- storage model and filesystem.

## Design constraints

The primary expected constraint is GPU memory rather than CPU compute. The platform will therefore prioritize efficient quantization, controlled context sizes and explicit measurement of GPU offload and host-memory use.

## Upgrade philosophy

No hardware upgrade should be justified without measured evidence. Future changes such as 128 GB RAM or a larger-VRAM GPU should be tied to observed bottlenecks and repeated benchmarks.
