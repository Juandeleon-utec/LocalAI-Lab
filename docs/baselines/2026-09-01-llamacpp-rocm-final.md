# Phase 5 Final Baseline — llama.cpp on ROCm / gfx1200

Date: 2026-09-01

## Purpose

Close Phase 5 by recording a reproducible native `llama.cpp` build using the AMD ROCm/HIP backend on the Radeon RX 9060 XT (`gfx1200`).

## Host baseline

- OS: Ubuntu 24.04.4 LTS
- Kernel: `7.0.0-30-generic`
- CPU: Intel Core i5-14600KF
- Memory: 64 GB class, ~62 GiB visible
- GPU: AMD Radeon RX 9060 XT 16 GB
- ROCm architecture: `gfx1200`
- VRAM reported by llama.cpp: `16304 MiB`
- ROCm development environment: `~/rocm10-devel`
- ROCm root used for compilation: `~/rocm10-devel/lib/python3.12/site-packages/_rocm_sdk_devel`

## llama.cpp revision

- Repository: `ggml-org/llama.cpp`
- Commit: `b96806d96061049a5b574269b049bf6241d63d46`
- Short commit: `b96806d96`
- Tag/build: `b10752`
- llama.cpp version: `0.3.0-dev`
- Compiler reported by binary: `Clang 23.0.0`

## Build configuration

The build used the ROCm SDK from the dedicated Python virtual environment and explicitly avoided mixing CMake packages from `/opt/rocm`.

Key CMake options:

```bash
cmake -S . -B build-rocm \
  -G Ninja \
  -DCMAKE_PREFIX_PATH="$ROCM_ROOT" \
  -DCMAKE_IGNORE_PREFIX_PATH="/opt/rocm" \
  -DCMAKE_C_COMPILER="$ROCM_ROOT/lib/llvm/bin/clang" \
  -DCMAKE_CXX_COMPILER="$ROCM_ROOT/lib/llvm/bin/clang++" \
  -DCMAKE_HIP_COMPILER="$ROCM_ROOT/lib/llvm/bin/clang" \
  -Dhip_DIR="$ROCM_ROOT/lib/cmake/hip" \
  -DAMDDeviceLibs_DIR="$ROCM_ROOT/lib/cmake/AMDDeviceLibs" \
  -Damd_comgr_DIR="$ROCM_ROOT/lib/cmake/amd_comgr" \
  -DGGML_HIP=ON \
  -DAMDGPU_TARGETS=gfx1200 \
  -DCMAKE_HIP_ARCHITECTURES=gfx1200 \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_BUILD_TESTS=OFF
```

Build command:

```bash
cmake --build build-rocm -j"$(nproc)"
```

Build completed successfully with the final target linked:

```text
[592/592] Linking CXX executable bin/llama
```

## Runtime libraries

The resulting binary links against the HIP backend and ROCm libraries from the virtual environment, including:

- `libggml-hip.so.0`
- `libamdhip64.so.7`
- `libhipblas.so.3`
- `librocblas.so.5`
- `librocsolver.so.0`
- `libhipblaslt.so.1`
- `libamd_comgr.so.3`
- `libhsa-runtime64.so.1`

No unresolved ROCm libraries were reported by `ldd`.

## Device detection

`llama-bench --help` initialized the ROCm backend and reported:

```text
ggml_cuda_init: found 1 ROCm devices (Total VRAM: 16304 MiB):
  Device 0: AMD Radeon RX 9060 XT, gfx1200 (0x1200), VMM: no, Wave Size: 32, VRAM: 16304 MiB
```

This confirms that the built `llama.cpp` binaries can initialize the ROCm backend and detect the target GPU as `gfx1200`.

## Available GPU controls

The built tools expose the expected runtime controls for model offload and benchmarking, including:

- `--device`
- `--list-devices`
- `--n-gpu-layers` / `--gpu-layers`
- `--main-gpu`
- `--split-mode`
- `--tensor-split`
- `--kv-offload`
- `--flash-attn`
- `--fit`
- `--fit-target`

## Phase 5 result

**PASS**

Criteria satisfied:

1. `llama.cpp` configured successfully with `GGML_HIP=ON`.
2. The build completed successfully for `gfx1200`.
3. The runtime links against the dedicated ROCm/HIP SDK libraries.
4. The HIP backend is present as `libggml-hip.so`.
5. `llama-bench` detects one ROCm GPU: AMD Radeon RX 9060 XT.
6. Reported architecture is `gfx1200` and VRAM is 16304 MiB.

## Next phase

Proceed to first-model validation with a small GGUF model before testing larger coding and academic models. Initial measurements should capture model load time, VRAM/RAM usage, prompt-processing throughput, generation throughput, stability, temperature, and power where available.
