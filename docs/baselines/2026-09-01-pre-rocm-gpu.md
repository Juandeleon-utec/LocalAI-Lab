# Pre-ROCm GPU Baseline — 2026-09-01

## Purpose

Record the Radeon RX 9060 XT state immediately before installing ROCm.

## Validation commands

```bash
uname -r
lspci -nnk -s 03:00.0
ls -l /dev/dri/
ls -l /dev/kfd
```

## Recorded state

### Kernel

```text
7.0.0-30-generic
```

### GPU

```text
03:00.0 VGA compatible controller [0300]: Advanced Micro Devices, Inc. [AMD/ATI] Device [1002:7590] (rev c0)
        Subsystem: ASUSTeK Computer Inc. Device [1043:0639]
        Kernel driver in use: amdgpu
        Kernel modules: amdgpu
```

### DRM devices

```text
/dev/dri/card1
/dev/dri/renderD128
```

`renderD128` is owned by the `render` group.

### HSA/KFD device

```text
/dev/kfd
```

`/dev/kfd` is present and owned by the `render` group.

## Interpretation

The RX 9060 XT is correctly detected by PCIe and bound to the `amdgpu` kernel driver. The DRM render node and KFD compute device are present, so the kernel-side prerequisites for ROCm compute are available.

This state follows an earlier unsuccessful initialization attempt under kernel `6.8.0-138-generic`, where `amdgpu` reported a fatal GPU initialization error and probe error `-22`. After moving to kernel `7.0.0-30-generic`, the GPU initializes successfully.

ROCm has not yet been installed at this baseline point.

## Next validation target

After ROCm installation, confirm:

```bash
rocminfo
hipconfig
```

The expected LLVM/HSA target for the RX 9060 XT is:

```text
gfx1200
```
