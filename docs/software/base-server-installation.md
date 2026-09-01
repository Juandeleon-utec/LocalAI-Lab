# Phase 1 — Base Server Installation

This document records the commands executed during the initial LocalAI-Lab server setup after reinstalling Ubuntu Server on the 500 GB Kingston NVMe drive.

The purpose of this file is procedural reproducibility. Only installation/execution commands and the final validation commands are included.

## 1. System update

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt autoremove -y
sudo apt autoclean
```

## 2. Hostname

```bash
sudo hostnamectl set-hostname ia-server
```

## 3. Time zone

```bash
sudo timedatectl set-timezone America/Montevideo
```

## 4. Base utilities and development tools

```bash
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

## 5. Hardware sensor detection

```bash
sudo sensors-detect
```

## 6. Final validation

```bash
lsb_release -a
uname -a
hostnamectl
timedatectl
free -h
lspci | grep -E "VGA|Display|3D"
lsblk -o NAME,SIZE,MODEL,TYPE,MOUNTPOINTS
git --version
python3 --version
cmake --version
gcc --version
sensors
```
