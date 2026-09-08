# Runtime evaluation

Evaluated September 7, 2026. **Blender 4.2.9 LTS with CPU Cycles is the tested production path for this iteration.** The browser glTF viewer is the interactive exterior route. No validated UE5 build is currently delivered.

## Observed workstation

| Item | Observed value |
| --- | --- |
| Operating system | Ubuntu 24.04.4 LTS, x86-64 |
| CPU | Intel Core i7-3610QM, 2.30 GHz base, 4 cores / 8 threads |
| Installed memory | Approximately 8 GB; Linux `MemTotal` reported 8,026,500 kB |
| Graphics devices | Intel third-generation integrated graphics and NVIDIA GK107M GeForce GTX 660M, from `lspci` |
| Blender | Portable 4.2.9 LTS, build hash `a10f621e649a` |
| Blender archive | 355,259,956 bytes; extracted installation approximately 1.3 GB |

The render generator explicitly selects Cycles CPU and six render threads. It uses denoising and adaptive sampling. Graphics devices being enumerated does not establish a working accelerated rendering backend; GPU rendering is not asserted by this project.

## Measured draft renders

The initial frontage render logs recorded the following values on this workstation. These are observations of earlier scene revisions, not delivery-resolution forecasts or measures of fidelity.

| Draft | Cycles samples | Logged render time | Blender logged peak memory |
| --- | ---: | ---: | ---: |
| First frontage iteration | 24 | 1 min 4.15 s | 258.06 MB |
| Second frontage iteration | 40 | 2 min 22.38 s | 362.48 MB |

The logs did not record image dimensions in their completion summaries, so those timings are not normalized to a particular output resolution. Blender's reported peak is its own memory accounting, not total process RSS or total workstation usage. Scene construction, later geometry, denoising, concurrent applications, texture loading, and higher resolutions can alter both time and memory substantially. Raw logs are scratch artifacts rather than source-controlled dependencies.

An isolated Eevee test encountered an EGL configuration warning and was extremely slow with high memory demand on the available software graphics route. It was terminated. Although `render_motion.py` exposes an Eevee option, Eevee is **not validated for local production** and is not the documented default.

## Unreal Engine 5 decision

Epic's current Linux guidance recommends 32 GB RAM, a GeForce 2080-class graphics card, and at least 8 GB graphics memory. Its Linux quickstart also calls out Vulkan's sensitivity to low VRAM and recommends a dedicated GPU with substantial VRAM. These are recommendations for smooth editor operation, not a claim that 8 GB system RAM alone makes every UE application impossible. Sources checked September 7, 2026: [Linux development requirements](https://dev.epicgames.com/documentation/unreal-engine/linux-development-requirements-for-unreal-engine) and [Linux development quickstart](https://dev.epicgames.com/documentation/unreal-engine/linux-development-quickstart-for-unreal-engine).

The observed GTX 660M / 8 GB machine is well below that recommended configuration. No UE5 editor, scene import, packaged application, or performance measurement has been validated here. Installing a large engine does not resolve those constraints. A production UE5 walkthrough therefore remains an open task for suitable hardware; this iteration uses the browser viewer to support exterior inspection.

The browser renderer and Blender Cycles use different material, lighting, shadow, and reflection implementations. The glTF viewer is useful for spatial inspection and navigation; it should not be treated as a pixel-identical reproduction of the Blender stills. Browser performance and WebGL availability must be checked on the target device. Approximate navigation bounds are not surveyed building collision geometry.

## Capacity and acceptance

Allow space for the approximately 1.3 GB Blender installation, npm dependencies, source data, the editable master, and both current and preserved render iterations. Motion is saved as PNG frames before encoding; disk use grows with frame count and resolution. Exact final storage and render-time requirements must be measured after the delivery settings and corrected scene are fixed.

Before any full cinematic, render a short sample at the actual delivery resolution and inspect thin edges, leaf silhouettes, shadows, reflections, noise, motion, and clipping in playback. Inspect representative later segments as well as the opening. A successful render or low memory figure does not establish photographic appearance, resemblance, or temporal stability.

## GTX 660M follow-up — September 7, 2026

Read-only checks confirmed PCI `01:00.0`, NVIDIA GK107M GeForce GTX 660M `[10de:0fd4]` (Lenovo subsystem `[17aa:3977]`), using `nouveau`, on Ubuntu 24.04.4 LTS with kernel `7.0.0-31-generic`. Host-side Blender `_cycles.available_devices` checks returned CPU only for both CUDA and OptiX; no NVIDIA CUDA driver library, `nvidia-smi`, or `/dev/nvidia*` was found. CPU remains the active motion-render path.

The GPU's CUDA compute capability is **3.0**, and the installed Blender 4.2.9 bundle contains `kernel_sm_30.cubin.zst`. Its local Cycles UI source also specifies a CUDA minimum of 3.0, versus 5.0 for OptiX. Thus CUDA architecture support is present in this exact build, while **OptiX is unsupported by this card**. A Blender downgrade or rebuild is not indicated solely by its architecture. Sources: [NVIDIA legacy CUDA table](https://developer.nvidia.com/cuda/gpus/legacy) and the inspected Blender bundle's `4.2/scripts/addons_core/cycles/properties.py`, lines 1730–1740.

The driver path remains unresolved. NVIDIA places PCI `0FD4` in the legacy **470.xx** branch. However, the current Ubuntu candidate `nvidia-driver-470` (`470.256.02-0ubuntu0.24.04.5`) is transitional: it depends on `nvidia-driver-535`, whose candidate (`535.309.01-0ubuntu0.24.04.2`) in turn depends on `nvidia-driver-580` (`580.173.02-0ubuntu0.24.04.1`). This chain does not provide genuine legacy 470. Sources: [NVIDIA legacy driver list](https://www.nvidia.com/en-us/drivers/unix/legacy-gpu/), [Ubuntu's 470 package](https://packages.ubuntu.com/noble-updates/nvidia-driver-470), and local APT candidate/dependency metadata.

Older genuine 470 packages remain indexed, but compatibility with kernel `7.0.0-31` was **not established**. No matching prebuilt 470 module package was found in the available indexes; installed kernel headers do not prove the driver will build or load. NVIDIA documents that its [kernel interface is built for the target kernel](https://download.nvidia.com/XFree86/Linux-x86_64/470.256.02/README/installdriver.html). No packages were installed, drivers changed, reboots performed, or GPU benchmarks run. A working driver would still require explicit CUDA/GPU selection because the generator selects CPU. Any rendering speedup remains unmeasured.
