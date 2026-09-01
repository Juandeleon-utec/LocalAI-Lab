# Phase 1 Final Baseline — 2026-09-01

## Validation command set

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

## Recorded system state

### Operating system

- Ubuntu Server 24.04.4 LTS (Noble Numbat)
- Kernel: `6.8.0-138-generic`
- Architecture: `x86_64`
- Hostname: `ia-server`

### CPU

- Intel Core i5-14600KF
- 14 physical cores
- 20 logical CPUs
- Maximum reported frequency: 5.3 GHz
- L3 cache: 24 MiB
- Single NUMA node
- Intel VT-x available

### Memory

- Installed/visible RAM: approximately 62 GiB
- Idle memory used during capture: approximately 1.0 GiB
- Swap: 8 GiB

### System disk

- Device: `/dev/nvme0n1`
- Model: Kingston SNV2S500G
- Capacity: 465.8 GiB usable
- EFI: 1 GiB
- `/boot`: 2 GiB
- LVM PV: 462.7 GiB
- Root LV: 100 GiB ext4 mounted at `/`

### Additional storage detected

Two SATA disks were also detected:

- `/dev/sda`: REAPER C, approximately 953.9 GiB
- `/dev/sdb`: REAPER C, approximately 953.9 GiB

`/dev/sda` still contains an older Ubuntu LVM installation (`ubuntu-vg/ubuntu-lv`). Because that volume group remains present, the newly installed NVMe LVM volume group is currently named `ubuntu-vg-1`.

This should be reviewed before the storage layout is finalized.

### GPU state at baseline

The AMD Radeon RX 9060 XT was not yet installed at the time of this baseline.

Detected display adapter:

- NVIDIA GeForce GT 610 (`10de:104a`)

This GPU is temporary and is not part of the intended LocalAI-Lab compute configuration.

### Network

Two Ethernet interfaces were detected:

- `enp4s0`: Realtek RTL8125 2.5GbE — active
- `enp5s0`: Realtek RTL8111/8168/8411 Gigabit Ethernet — inactive

Active IPv4 address at capture time:

```text
192.168.2.238/24
```

The address was assigned dynamically by DHCP.

## Phase 1 interpretation

The clean Ubuntu installation on the Kingston NVMe is operational and SSH/network access is functional.

Before moving to ROCm, the following storage issue should be resolved or explicitly accepted:

- old Ubuntu LVM metadata remains on `/dev/sda`;
- the current root LV uses only 100 GiB of the 462.7 GiB NVMe LVM physical volume;
- the final storage layout for models, datasets, RAG indexes and benchmark output has not yet been defined.

The GPU compute baseline will be captured separately after installation of the Radeon RX 9060 XT.
