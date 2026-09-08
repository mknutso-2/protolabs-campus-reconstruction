# Reproduction and delivery guide

Run the commands below from the repository root unless a block explicitly changes directory. They describe the current scripts. **Visual acceptance and a complete fresh-checkout delivery verification remain separate work:** do not interpret the presence of a command or output file as proof that its result has passed inspection.

## Dependencies

| Component | Use |
| --- | --- |
| Blender 4.2.9 LTS | Scene generation, editable master, Cycles CPU stills, glTF export, motion frames |
| Node.js 22.13 or later and npm | Viewer; dependencies fixed by `viewer/package-lock.json` |
| Python 3.12 and Pillow 10.2.0 | Tested local viewer-asset preparation; Python version/pillow versions observed on the build host |
| FFmpeg with libx264 | Separate executable for `scripts/encode_video.py`; select with `--ffmpeg` or the `FFMPEG` environment variable |
| Git | Source and reproducible input history; private repository access requires authentication |

Blender includes its own Python and `bpy`. Run scene scripts through Blender, not ordinary `python3`. The examples pass absolute script paths using `$PWD` and `--python-exit-code 1` so a Python exception fails the command. The original procedural vegetation and vehicle modules require no downloaded model assets. Blender packs generated image textures and available fonts into the master when saving. The generator uses DejaVu Sans when found at its Linux system path, otherwise Blender's built-in font; typography can differ on another workstation and remains an approximation to the sign.

### Portable Blender on Linux x86-64

The [official Blender 4.2 release directory](https://download.blender.org/release/Blender4.2/) contains the pinned archive and published checksum file. This installs into the ignored `work/` directory and does not require a system-wide Blender installation:

```bash
mkdir -p work/tools
(
  set -e
  cd work/tools
  curl --fail --location --output blender-4.2.9-linux-x64.tar.xz \
    https://download.blender.org/release/Blender4.2/blender-4.2.9-linux-x64.tar.xz
  curl --fail --location --output blender-4.2.9.sha256 \
    https://download.blender.org/release/Blender4.2/blender-4.2.9.sha256
  sha256sum --ignore-missing --check blender-4.2.9.sha256
  tar -xf blender-4.2.9-linux-x64.tar.xz
)
export PROTOLABS_BLENDER="$PWD/work/tools/blender-4.2.9-linux-x64/blender"
"$PROTOLABS_BLENDER" --version
```

Stop if checksum verification fails. The locally acquired archive was 355,259,956 bytes and its recorded SHA-256 was `dfbc127a7d28f9c2175b23bf9d6701b2855f31eedfb391f9a6e60adb24572846`. The extracted installation occupied approximately 1.3 GB. On another operating system use the corresponding official 4.2.9 build and set `PROTOLABS_BLENDER` to its executable.

For the small packaging script, use an existing compatible Python/Pillow environment or an isolated environment:

```bash
python3 -m venv work/package-venv
work/package-venv/bin/python -m pip install Pillow==10.2.0
export PROTOLABS_PYTHON="$PWD/work/package-venv/bin/python"
```

No Python geospatial stack is required to build from the checked-in derived constraints. Reprocessing raw lidar is a different workflow described under [research inputs](#research-inputs).

The build workspace has a portable **FFmpeg 7.0.2-static** executable acquired from the pinned `imageio-ffmpeg==0.6.0` PyPI wheel, without a global installation. Its archive SHA-256 is `c7e46fcec401dd990405049d2e2f475e2b397779df2519b544b8aab515195282`; acquisition URL, binary hash, build configuration, and notices are recorded in the workspace's `work/tools/video/provenance.json` and accompanying files. The wrapper is BSD-2-Clause and the binary reports GPL-3.0-or-later. This workspace tool cache is not part of a fresh source checkout. Use a suitable system FFmpeg or your own verified portable copy, and set `PROTOLABS_FFMPEG` to its actual executable for the explicit `--ffmpeg` examples below. If omitted, the helper uses `FFMPEG`, then `/usr/bin/ffmpeg`.

## Research inputs

`scripts/build_scene.py` reads these small derived inputs directly:

- `research/terrain_grid.json`: local terrain elevations.
- `research/lidar_roof_constraints.json`: roof polygons and fitted planes.
- `research/site-layout.json`: site extent, roads, parking, and landscape traces.
- `research/reference_drone_camera_fit.json`: fitted reference camera information.
- `research/north_context_ground_grid.json`: 5 m ground grid for the northern context.
- `research/north_context_canopy_constraints.json`: 105 inferred canopy-envelope candidates, of which 102 are eligible for scene placement.

Keep the source ledgers alongside those inputs. They record confidence, dates, attribution, and conflicts. The scene uses metres, X east / Y north / Z up. Its local origin is NAD83 UTM15N `(447671.8750643735, 4984591.8364606025)`. Measured NAVD88 elevations are offset by **303.6 m** for the scene. Roof-plane equations return absolute NAVD88 metres; subtract 303.6 when constructing scene geometry. The lidar/aerial datum distinction is documented in `research/geospatial-findings.md`; this is not a claim of survey-grade alignment.

The northern context replaces the earlier uniform forest interpretation with constraints derived from the cached northern LAZ tile. Class 2 returns support the ground grid; filtered class 1 elevated returns support canopy envelopes. Candidate positions are envelope peaks, not measured trunks. Class 1 is not a verified vegetation classification, and height, species, crown shape, and context beyond the cached aerial remain uncertain. The constraints include eligibility decisions and source hashes; retain those qualifications when inspecting the landscape.

Reference photographs are not needed to generate geometry but are needed to evaluate resemblance and populate comparisons. `scripts/acquire_references.py` downloads exactly the three photographs pinned by `research/reference-cache-manifest.json` into `research/images/`. It checks byte sizes and SHA-256 hashes, reuses matching files, and rejects changed or mismatching files without overwriting them. Preserve source attribution and capture-date uncertainty from the manifest and architecture ledger:

```bash
python3 "$PWD/scripts/acquire_references.py" --dry-run
python3 "$PWD/scripts/acquire_references.py"
python3 "$PWD/scripts/acquire_references.py" --verify-only
```

`--dry-run` lists the planned source URLs and paths without network access or writes. `--verify-only` checks an existing cache without downloading or writing files. A publisher changing or removing an image requires a deliberate review of the source snapshot; acquisition does not silently accept replacement content. The current comparison view uses:

| Local reference | Viewer destination |
| --- | --- |
| `protolabs-official-hq-drone.jpg` | `references/hq.jpg` |
| `businessjournal-entrance-2018.jpg` | `references/entrance.jpg` |
| `machine-design-frontage-2024.png` | `references/arrival.png` |

Public reference-image availability does not establish redistribution rights. Cache for authorized research/inspection and keep licensed images out of ordinary source history. County/Nearmap imagery is not asserted to be CC0. OSM-derived geometry retains its attribution and ODbL context in the ledger.

Raw acquisition and processing are now included in [`scripts/research/`](../scripts/research/README.md): `acquire.py`, `process.py`, pinned `requirements.txt`, the source manifest, snapshot SHA-256 records, and `expected_outputs.json`. The following commands create a separate environment and write fresh results outside the authoritative `research/` inputs:

```bash
python3 -m venv work/research-venv
work/research-venv/bin/python -m pip install -r scripts/research/requirements.txt
work/research-venv/bin/python "$PWD/scripts/research/acquire.py" \
  --raw-dir data/research/raw --dry-run
work/research-venv/bin/python "$PWD/scripts/research/acquire.py" \
  --raw-dir data/research/raw --include-reference-photos
work/research-venv/bin/python "$PWD/scripts/research/process.py" \
  --raw-dir data/research/raw --output-dir data/research/derived
```

Acquisition covers two bounded LAZ tiles totaling 174,260,883 bytes, plus the county orthophoto, parcels, and OSM context. Optional official photographs are fetched with `--include-reference-photos`; use the separate `scripts/acquire_references.py` workflow above to populate all three viewer comparison photographs. Immutable source hashes are enforced; mutable-service responses get their own acquisition receipts. Do not silently substitute a newer GIS response for the dated reconstruction snapshot.

The included `scripts/research/derive_canopy.py` independently regenerates the northern ground grid and canopy constraints from `USGS_LPC_MN_CentralMissRiver_B22_4475_49845.laz` (74,129,464 bytes, recorded SHA-256 `772f6ee72e6ba327d653a3a9a10f42e867884f0d748cbc8d1b7f2b54dc699436`). Set `PROTOLABS_NORTH_TILE` to the acquired file's absolute path and write comparison results outside `research/`:

```bash
work/research-venv/bin/python "$PWD/scripts/research/derive_canopy.py" \
  --tile "$PROTOLABS_NORTH_TILE" --output-dir "$PWD/data/research/north-derived"
```

Keep the default one-million-point chunk size when reproducing the recorded grid: the ground subsampling method is defined per read chunk. Compare the derived grids and 102 eligible candidates with the committed constraints before replacing them. The tile ends near local y = 408.15 m, and the cached aerial ends near y = 218.71 m; the script does not establish unseen geometry or extend lidar coverage beyond the source tile.

**Validation scope:** the packaged acquisition script passed its no-network dry-run, Python scripts compiled, processing dependencies imported, and the existing immutable raw sources matched recorded hashes. The complete 174 MB acquisition/processing pipeline was **not rerun** merely to validate packaging. Compare a fresh run's numeric coordinates, elevations, and dimensions with `expected_outputs.json` before accepting replacement inputs; JSON byte hashes can differ because explanatory metadata and formatting changed. Preserve the current inputs until that comparison is complete.

## Generate and open the master

```bash
"$PROTOLABS_BLENDER" --background --python-exit-code 1 \
  --python "$PWD/scripts/build_scene.py" -- --export
"$PROTOLABS_BLENDER" "$PWD/scene/protolabs-campus.blend"
```

The generator creates a new scene and overwrites the generated master and camera JSON. Preserve an edited master or earlier iteration before regenerating. It writes:

| Output | Meaning |
| --- | --- |
| `scene/protolabs-campus.blend` | Editable master with named geometry, materials, evidence notes, and cameras |
| `scene/protolabs-campus.glb` | Full-geometry GLB, when `--export` is supplied |
| `scene/protolabs-campus-viewer.glb` | Browser GLB with approximately 30% of leaf cards retained; automatically exported with `--export` |
| `scene/viewer-export.json` | Master SHA-256, foliage-retention setting, and before/after visible vegetation triangle counts |
| `scene/cameras.json` | Saved camera definitions and reference associations |
| `scene/materials.json` | Linear-color PBR fallback map for procedural materials that glTF does not reproduce directly |

Both GLB exports use Y-up coordinates, apply export transforms, and omit Blender lights/cameras; the viewer creates its own lighting and reads camera/material JSON. They are not expected to reproduce all Cycles node materials exactly. Keep materials, cameras, both models, and the export metadata from the same generation.

The reduced export retains branches and deterministically selects approximately 30% of leaf cards for browser navigation. `scripts/export_viewer.py` restores the original in-memory meshes after export and does not save changes to the master. The packed editable master, full GLB, and Cycles renders retain complete foliage. To regenerate only the browser export from a current saved master:

```bash
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/export_viewer.py"
```

`scene/viewer-export.json` binds the export to the saved master's SHA-256. The packaging script rejects a mismatching master; it does not independently hash the browser GLB, so preserve the exported GLB together with its metadata. Run the command above after deliberately editing and saving a master before staging its updated browser model.

For a quick single-view iteration:

```bash
"$PROTOLABS_BLENDER" --background --python-exit-code 1 \
  --python "$PWD/scripts/build_scene.py" -- \
  --render reference_aerial --width 1440 --samples 40
```

This rebuilds the scene and writes `deliverables/reference_aerial.png`. `--no-trees` is available for geometry diagnosis; such a render cannot establish completed landscape quality. Build defaults are 1440 pixels wide and 40 Cycles samples. The height is two-thirds the width.

## Render fixed views and compare

```bash
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/render_views.py" -- \
  --views reference_aerial --width 1600 --samples 64 --out deliverables/stills
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/render_views.py" -- \
  --views entrance_detail,arrival,campus_overview \
  --width 1600 --samples 48 --out deliverables/stills
```

Available names are `reference_aerial`, `entrance_detail`, `arrival`, and `campus_overview`. Render a subset with a comma-separated `--views` argument. **The current target is 1600 × 1067**, using 64 samples for the aerial and 48 for the other three views; the commands above specify those settings explicitly. The script's fallback defaults remain all four, 1920 × 1280, and 96 samples. `--out` is relative to the repository root. Target settings do not imply every current view has finished rendering or passed inspection.

Use a new output directory for a preserved iteration, for example `--out deliverables/iterations/v04`. Pair reference images, camera transforms, and corresponding full-resolution renders. Record the largest visible discrepancies, correct them, and rerender. The fitted aerial camera has residual uncertainty; the other saved cameras are interpreted viewpoints. Bright reflections or favorable light must not conceal incorrect geometry.

## Motion sample, then cinematic

`render_motion.py` generates a continuous southeast exterior arc with an approach and lens change. It saves `scene/protolabs-motion.blend`, PNG frames, `path.json`, and `render-progress.json`; video encoding is a separate step. **The current sample/full-film target is 1280 × 720, 24 fps, and a six-second path (144 frames).** The planned sample is frames 61–84, a one-second segment near the middle of the path where the camera moves faster than at its eased endpoints. It uses 16 Cycles samples; inspect its quality before retaining that setting for a full render. The latest v06 fixed-view renders, motion sample inspection, and complete encoded movie remain pending. These commands describe the current workflow, not a verified finished cinematic.

Begin with an empty `deliverables/motion-sample/` frame directory, preserving any earlier sample and its manifest under an iteration-specific name. Different master generations or disjoint samples must not share an encoding input directory.

```bash
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/render_motion.py" -- \
  --sample --engine cycles --width 1280 --samples 16 \
  --seconds 6 --start 61 --end 84 --skip-existing
```

Inspect thin edges, foliage, shadows, reflections, noise, clipping, and playback at full resolution. The underlying arc duration is controlled by `--seconds`, so preserve `--seconds 6` when comparing path segments. A middle sample does not test every camera position. The script's unqualified defaults are 1920 pixels wide, 32 samples, 12 seconds, and an ending frame of 48 with `--sample`; explicit arguments are required to reproduce the current settings.

`--skip-existing` resumes valid completed PNG frames without overwriting them. When frames exist, it requires `path.json` and rejects mismatches in the saved master SHA-256, dimensions, fps, path duration, engine, sample count, or motion-blur shutter. A dimension/header/end-marker check decides which matching frames can be skipped; malformed or incomplete frames are rendered again. The path manifest records the source revision, master hash, settings, requested frame range, and representative camera keyframes. The progress file updates when a rendered frame is written; it is not a visual-quality pass and does not update merely because an existing frame was skipped.

Use the source-controlled encoder after all 24 sample frames have completed. `PROTOLABS_FFMPEG` must point to the chosen FFmpeg executable:

```bash
python3 "$PWD/scripts/encode_video.py" \
  --frames-dir deliverables/motion-sample --fps 24 --expected-frames 24 \
  --ffmpeg "$PROTOLABS_FFMPEG" --out deliverables/motion-sample.mp4
```

`encode_video.py` requires contiguous, consistently numbered `frame_NNNN.png` inputs with equal, even dimensions; numbering may begin at 61 for this sample. `--expected-frames` rejects an incomplete or oversized sequence. It preserves an existing output and uses H.264/libx264, CRF 18, yuv420p, and MP4 faststart. It does not interpolate, duplicate, resize, pad, or invent frames. Use a new output name and a separate preserved frame directory for subsequent versions.

After inspecting the middle sample, render and inspect endpoint frames 1 and 144 at the same settings. Omitting `--sample` places these checks in `deliverables/cinematic/`, keeping them out of the sample encoding folder:

```bash
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/render_motion.py" -- \
  --engine cycles --width 1280 --samples 16 --seconds 6 --frame 1 --skip-existing
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/render_motion.py" -- \
  --engine cycles --width 1280 --samples 16 --seconds 6 --frame 144 --skip-existing
```

The `--frame` path writes the requested frame; `--skip-existing` still checks any existing directory's manifest for compatibility. Preserve earlier cinematic frames before changing the master or settings. **Only after sample and endpoint inspection and corrections pass**, render and encode the complete 144-frame sequence:

```bash
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/render_motion.py" -- \
  --engine cycles --width 1280 --samples 16 --seconds 6 \
  --start 1 --end 144 --skip-existing
python3 "$PWD/scripts/encode_video.py" \
  --frames-dir deliverables/cinematic --fps 24 --expected-frames 144 \
  --ffmpeg "$PROTOLABS_FFMPEG" --out deliverables/flythrough.mp4
```

Sampling settings are a starting point, not a guarantee against noise or flicker. Raise quality or correct materials/geometry when inspection warrants it. Eevee is an exposed script option but was not viable as a local production route in this evaluation. The current host uses CPU Cycles.

## Prepare and run the exterior viewer

After the master, reduced browser GLB, matching `viewer-export.json`, and desired stills exist, install the viewer's locked dependencies **before** packaging. The packaging script invokes `npx gltf-transform` from `viewer/`, so reversing this order would leave the optimizer unavailable or trigger an unintended on-demand package lookup:

```bash
(
  cd viewer
  npm ci
)
"$PROTOLABS_PYTHON" "$PWD/scripts/package_viewer.py"
(
  cd viewer
  npm run dev
)
```

Open the local URL printed by the development server; do not open `page.tsx` or the GLB through `file://`. The viewer loads the model over HTTP. Its dependencies and minimum Node version come from `viewer/package.json` and the lockfile. For build validation, run `npm run build` from `viewer/`; `npm run lint` runs the configured source linter.

`package_viewer.py` copies saved cameras, `materials.json`, and terrain to `viewer/public/models/`, checks `scene/viewer-export.json` against the current master's SHA-256, then optimizes `scene/protolabs-campus-viewer.glb` to `models/campus.glb` with Meshopt compression. It uses the lighter browser export rather than reducing the editable master. The optimizer disables further simplification, palette generation, and texture compression. Packaging converts fixed PNG stills to quality-94 JPEGs under `viewer/public/renders/`, stages the three named references, and copies `deliverables/flythrough.mp4` when it exists. It prefers `deliverables/stills/`, falls back to `deliverables/`, and prints pending messages for missing stills or references. **A pending message means the corresponding viewer content is incomplete.** Missing required model, camera, material, or export metadata files cause packaging to fail, as does a mismatching master hash. Review staged files after a failure because some assets are copied before the model check.

A clean viewer source directory completed `npm ci --offline` from the existing local npm cache: 746 packages installed in approximately one minute. This verifies dependency installation with that cache; it does not establish an offline install on a machine without cached packages. Its subsequent production build and the separate fresh-scene validation remain pending at this documentation update.

Orbit: drag to orbit, scroll to approach, right-drag to pan. Walk: drag to look, use WASD or arrow keys to move, and Shift for speed. Saved views restore the named reference viewpoints. Terrain and building bounds are approximations for exterior inspection, not a complete collision simulation. Still views, reference comparisons, and motion are separate tabs.

The model, stills, and locally cached references staged under `viewer/public/` are generated delivery content. Review staging before committing and exclude binary/restricted reference assets from ordinary Git history. Do not publish private or restricted references simply because a local viewer serves them.

## GitHub synchronization

The private project is [mknutso-2/protolabs-campus-reconstruction](https://github.com/mknutso-2/protolabs-campus-reconstruction). Initial publication used the authenticated GitHub connector because browser sign-in did not supply a Git CLI credential or SSH key.

| Initial history | Identifier |
| --- | --- |
| Local initial `main` | `a7041fd` |
| Remote README bootstrap | `3cd04e454e2552fc8917e128c4fa6ea18b00506f` |
| Remote initial four-file `main` | `7abbf121fb45e15c2b98a9419737e24f42ca7fb0` |
| Identical initial local/remote tree | `8c50660280c6302ddaac10ec4e6bd1cb1c6b4db1` |

The connector preserves file/tree contents but does not expose original author/committer dates when creating commits, so equal source trees can have different commit SHAs and histories. These identifiers describe bootstrap history, not the current feature branch. Substantial work uses branches and pull requests with visible-change and verification notes.

After normal Git CLI authentication is configured, fetch and inspect both histories before reconciling them. Preserve existing branches and commits; do not force-push simply to make SHAs match. A new authenticated clone of the remote branch is the simplest clean starting point for normal future pushes. Connector mirroring and local source history must have an explicit mapping until reconciliation is complete.

## Large files, archives, and fresh-checkout verification

The selected approach is **regenerate binary artifacts and distribute versioned archives**, rather than put every `.blend`, GLB, image, and video revision in Git LFS. Commit scene-generation code, small measured constraints, camera definitions, provenance, and dependency locks. Keep dependencies, caches, secrets, raw lidar/imagery, generated scenes, frames, movies, and viewer binary staging out of normal Git history. If irreplaceable manually edited binary assets are introduced later, document their authoritative storage and recovery before relying on them.

For each delivery, include the source revision, source/input identifiers, Blender version, render settings, camera/path definitions, the editable master, GLB, accepted stills/video, and a candid accuracy report. Preserve earlier versions under unique names. Include third-party reference images only where distribution rights permit; otherwise include attribution and acquisition instructions.

Create a SHA-256 manifest for the chosen archive contents and verify it after extraction. The manifest should identify files inside the delivered version rather than merely hash the ZIP itself. Do not mix a newly generated scene with stale camera metadata or renders from another source revision.

Fresh-checkout verification is complete only when another clean working directory can install the documented dependencies, find all required derived inputs, regenerate the master and export, render the saved views, stage the viewer, build it, and inspect the corresponding outputs. The raw-lidar scripts are included, but a complete rerun of that packaged pipeline and a validated UE5 application remain separate documented checks. Until those checks and visual acceptance are recorded, report the project as a reconstruction in progress.
