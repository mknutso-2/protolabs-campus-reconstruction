# Reproduction and delivery guide

Run the commands below from the repository root unless a block explicitly changes directory. They describe the current scripts. **V06 clean master/export verification and four-view inspection are complete; v07 integrated material/lighting acceptance and the full delivery remain open.** Do not interpret the presence of a command or output file as proof that its result has passed inspection.

The v06 master, both models, four stills, camera/material metadata and snapshot hashes are preserved in `deliverables/iterations/v06/`. Motion was deliberately not rendered for v06 because the reviewed stills exposed synthetic materials and lighting. The current v07 probe is pending visual acceptance; the current-revision motion sample, full film, private hosted site and versioned delivery archive are not complete.

## Dependencies

| Component | Use |
| --- | --- |
| Blender 4.2.9 LTS | Scene generation, editable master, Cycles CPU stills, glTF export, motion frames |
| Node.js 22.13 or later and npm | Viewer; dependencies fixed by `viewer/package-lock.json` |
| Python 3.12 and Pillow 10.2.0 | Tested local viewer-asset preparation; Python version/pillow versions observed on the build host |
| FFmpeg with libx264 | Separate executable for `scripts/encode_video.py`; select with `--ffmpeg` or the `FFMPEG` environment variable |
| Git | Source and reproducible input history; private repository access requires authentication |

Blender includes its own Python and `bpy`. Run scene scripts through Blender, not ordinary `python3`. The examples pass absolute script paths using `$PWD` and `--python-exit-code 1` so a Python exception fails the command. The original procedural vegetation and vehicle modules require no downloaded model geometry. V07 additionally requires the small CC0 surface/HDRI cache acquired below. Blender packs used scan images, generated leaf textures, the active HDRI and available fonts into the master when saving. The generator uses DejaVu Sans when found at its Linux system path, otherwise Blender's built-in font; typography can differ on another workstation and remains an approximation to the sign.

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

### Required v07 material acquisition

Before generating a fresh master, acquire the files pinned by `research/material-assets.json`:

```bash
python3 "$PWD/scripts/material_quality.py" --download
```

This acquisition entry point uses only Python's standard library. It verifies each exact byte size and SHA-256, reuses correct files, and preserves mismatching existing files while reporting an error. The default set totals **16,298,653 bytes**, including the optional Spruit environment; it excludes two rejected research candidates. No individual file exceeds 7 MB, and the downloader enforces a 15 MB file limit. Binary inputs remain in ignored `research/material-assets/`; the source manifest and script belong in Git.

The default surface set uses Poly Haven CC0 asphalt, leafy grass and fine concrete scans. The facade remains tinted precast without brick courses. Default illumination uses Qwantani Sunset Pure Sky, whose approximately 6.08° sun is oriented toward the reference's photographically inferred 5.46° elevation and 156.06° local XY azimuth. The source is a lighting proxy, not a sky captured at Protolabs. Spruit Sunrise is an optional unregistered landscape backdrop containing off-site objects; inspect all cameras before using it. Acquisition and image packing do not prove a visually convincing result. See [material provenance](material-provenance.md) for licenses, full hashes, controls and limitations.

The build workspace has a portable **FFmpeg 7.0.2-static** executable acquired from the pinned `imageio-ffmpeg==0.6.0` PyPI wheel, without a global installation. Its archive SHA-256 is `c7e46fcec401dd990405049d2e2f475e2b397779df2519b544b8aab515195282`; acquisition URL, binary hash, build configuration, and notices are recorded in the workspace's `work/tools/video/provenance.json` and accompanying files. The wrapper is BSD-2-Clause and the binary reports GPL-3.0-or-later. This workspace tool cache is not part of a fresh source checkout. Use a suitable system FFmpeg or your own verified portable copy, and set `PROTOLABS_FFMPEG` to its actual executable for the explicit `--ffmpeg` examples below. If omitted, the helper uses `FFMPEG`, then `/usr/bin/ffmpeg`.

## Research inputs

`scripts/build_scene.py` reads these small derived inputs directly:

- `research/terrain_grid.json`: local terrain elevations.
- `research/lidar_roof_constraints.json`: roof polygons and fitted planes.
- `research/site-layout.json`: site extent, roads, parking, and landscape traces.
- `research/reference_drone_camera_fit.json`: fitted reference camera information.
- `research/north_context_ground_grid.json`: 5 m ground grid for the northern context.
- `research/north_context_canopy_constraints.json`: 105 inferred canopy-envelope candidates, of which 102 are eligible for scene placement.
- `research/material-assets.json` and the acquired `research/material-assets/` files: v07 scanned surface and low-sun lighting proxies, consumed by `material_quality.py`.

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

The generator creates a new scene and overwrites the generated master and camera JSON. Preserve an edited master or earlier iteration before regenerating. Its current sequence builds the geometry and original assets, applies `visual_finish.apply_visual_finish()`, applies `material_quality.apply_material_quality(ROOT)`, exports camera/material fallbacks, packs used images/fonts, and saves before exporting the GLBs. Missing or mismatching required scan/HDRI files cause an error rather than silently falling back to the former surfaces.

`visual_finish.py` adds the verified 13-stripe/50-star flag pattern, smooth cylinder shading and an inferred pale paired entrance portal while preserving measured massing, terrain, flagpole location and cameras. Portal dimensions and static cloth pose remain interpreted. The revised `vehicles.py` supplies original generic sedan/SUV geometry with curved bodies, real wheel apertures and corrected materials; isolated construction/export and asset-preview checks are documented in [vehicle provenance](vehicle-provenance.md). Vehicle occupancy remains inferred. The generator leaves the reference-visible foreground court empty rather than recreating the earlier repeated bright car rows. These module-level checks do not constitute acceptance of the integrated v07 image.

It writes:

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

`scene/viewer-export.json` records SHA-256 hashes for the saved master and browser GLB. Packaging verifies both files before optimization and rejects missing or mismatching hashes. The preserved v06 receipt predates the browser-GLB hash and intentionally cannot pass this newer packaging gate; regenerate a current export and receipt together. Run the command above after deliberately editing and saving a master before staging its updated browser model.

The clean v06 archive at `1f8b4b9` generated 2,303 objects and both GLBs in 226.347 seconds. Reopened inspection verified all 102 eligible canopy placements, unchanged camera/material JSON baselines, and 8,000 leaves/18,212 triangles in each complete source tree mesh. The reduced foliage did not leak into the saved master. The corrected checker from `6208e82` passed against that unchanged master; its 1.6 mm comparison tolerance accounts for independently rounded research top values. The original 1 mm false failure and the earlier real inward-normal defect are preserved in [fresh source verification](fresh-checkout-verification.md). V07 changes require a new generation/inspection and are not covered by that v06 pass.

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

Available names are `reference_aerial`, `entrance_detail`, `arrival`, and `campus_overview`. Render a subset with a comma-separated `--views` argument. **The current target is 1600 × 1067**, using 64 samples for the aerial and 48 for the other three views; the commands above specify those settings explicitly. V06 completed and inspected this set, now preserved in `deliverables/iterations/v06/`; its synthetic surface response prompted the v07 probe. The v07 four-view set must follow successful probe review. The script's fallback defaults remain all four, 1920 × 1280, and 96 samples. `--out` is relative to the repository root.

Each final PNG has a matching JSON receipt recording its camera, saved-master and image SHA-256 hashes, dimensions, samples, Blender version, camera matrix and lens. All four final views, including `reference_aerial.png`, belong in `deliverables/stills/`. The separate `deliverables/reference_aerial.png` is an iteration probe. The render receipt starts with `inspection: "pending"`; actual final inspection is recorded separately in `deliverables/delivery-review.json` as described below.

Use a new output directory for a preserved iteration, for example `--out deliverables/iterations/v07/stills`. Pair reference images, camera transforms, and corresponding full-resolution renders. Record the largest visible discrepancies, correct them, and rerender. The fitted aerial camera has residual uncertainty; the other saved cameras are interpreted viewpoints. Bright reflections or favorable light must not conceal incorrect geometry.

## Motion sample, then cinematic

`render_motion.py` generates a continuous southeast exterior arc with an approach and lens change. It saves `scene/protolabs-motion.blend`, PNG frames, `path.json`, and `render-progress.json`; video encoding is a separate step. **The current sample/full-film target is 1280 × 720, 24 fps, and a six-second path (144 frames).** The planned sample is frames 61–84, a one-second segment near the middle of the path where the camera moves faster than at its eased endpoints. It uses 16 Cycles samples; inspect its quality before retaining that setting for a full render. V06's four stills were reviewed, and its motion run was deliberately deferred for the v07 material/lighting correction. The v05 opening sample remains historical engineering evidence in [motion review](motion-review.md); it does not approve the revised scene or faster middle section. Current-revision sample inspection and the complete encoded movie remain pending.

Begin with an empty `deliverables/motion-sample/` frame directory, preserving any earlier sample and its manifest under an iteration-specific name. Different master generations or disjoint samples must not share an encoding input directory.

```bash
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/render_motion.py" -- \
  --sample --engine cycles --width 1280 --samples 16 \
  --seconds 6 --start 61 --end 84 --skip-existing
```

Inspect thin edges, foliage, shadows, reflections, noise, clipping, and playback at full resolution. The underlying arc duration is controlled by `--seconds`, so preserve `--seconds 6` when comparing path segments. A middle sample does not test every camera position. The script's unqualified defaults are 1920 pixels wide, 32 samples, 12 seconds, and an ending frame of 48 with `--sample`; explicit arguments are required to reproduce the current settings.

`--skip-existing` resumes valid completed PNG frames without overwriting them. When frames exist, it requires `path.json` and rejects mismatches in the saved master SHA-256, complete camera-path fingerprint, dimensions, fps, path duration, engine, samples, shutter, Blender version, sampling/denoising controls or PNG settings. The camera fingerprint covers the generated transform and lens at every frame of the complete path. PNG validation checks dimensions, chunk CRCs and decompressed scanlines; malformed or incomplete frames are rendered again. The path manifest records the source revision, master hash, settings, requested frame range, representative camera keyframes and full-path fingerprint. Progress records report rendered and skipped counts; they do not establish visual quality. `--output-dir` selects an isolated frame/manifest directory for a test, but the script still saves `scene/protolabs-motion.blend`, so use a separate checkout when that native file must also be isolated.

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

The `--frame` path renders the requested frame, or preserves it when `--skip-existing` finds a compatible manifest and valid PNG. Preserve earlier cinematic frames before changing the master or settings. **Only after sample and endpoint inspection and corrections pass**, render and encode the complete 144-frame sequence:

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

`package_viewer.py` copies saved cameras, `materials.json`, and terrain to `viewer/public/models/`, checks the current master and browser GLB against both SHA-256 hashes in `scene/viewer-export.json`, then optimizes `scene/protolabs-campus-viewer.glb` to `models/campus.glb` with Meshopt compression. It uses the lighter browser export rather than reducing the editable master. The optimizer disables further simplification, palette generation, and texture compression. Packaging converts fixed PNG stills to quality-94 JPEGs under `viewer/public/renders/`, stages the three named references, and copies `deliverables/flythrough.mp4` when it exists. It prefers `deliverables/stills/`, falls back to `deliverables/`, and prints pending messages for missing stills or references. **A pending message means the corresponding viewer content is incomplete.** Missing required model, camera, material, or export metadata files cause packaging to fail, as does a missing or mismatching master/browser-GLB hash. Review staged files after a failure because some assets are copied before the model check.

A clean viewer dependency installation completed with `npm ci --offline` from the existing local npm cache: 746 packages installed in approximately one minute. Viewer revision `5bf2a27` also passed lint, production build and local navigation checks, including the visible walk controls and handling of rotated exterior footprints. This verifies installation with the available cache, not an offline installation on a machine without cached packages. These checks cover the tested viewer/source state and v06 payload; new v07 master, material fallback, stills and motion assets must be repackaged and checked before delivery. The private hosted site has not yet been published.

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

The current v07 work is on local branch `feat/reference-lighting`. At this documentation update it has not yet been mirrored to GitHub. Preserve the latest source/tree mapping and visual-check notes when publishing this branch; the existing draft PR and earlier mirrors do not imply that every current local change is already remote.

After normal Git CLI authentication is configured, fetch and inspect both histories before reconciling them. Preserve existing branches and commits; do not force-push simply to make SHAs match. A new authenticated clone of the remote branch is the simplest clean starting point for normal future pushes. Connector mirroring and local source history must have an explicit mapping until reconciliation is complete.

## Large files, archives, and fresh-checkout verification

The selected approach is **regenerate binary artifacts and distribute versioned archives**, rather than put every `.blend`, GLB, image, and video revision in Git LFS. Commit scene-generation code, small measured constraints, camera definitions, provenance, and dependency locks. Keep dependencies, caches, secrets, raw lidar/imagery, generated scenes, frames, movies, and viewer binary staging out of normal Git history. If irreplaceable manually edited binary assets are introduced later, document their authoritative storage and recovery before relying on them.

For each delivery, include the source revision, source/input identifiers, Blender version, render settings, camera/path definitions, the editable master, GLB, accepted stills/video, and a candid accuracy report. Preserve earlier versions under unique names. Include third-party reference images only where distribution rights permit; otherwise include attribution and acquisition instructions.

### Record inspection and create a versioned archive

Finish and inspect all four production stills, the motion sample, and the complete encoded film. Inspect the film in playback for motion, noise and flicker; a successful decode only verifies file integrity and timing. Regenerate the offline gallery after inspecting all four final views:

```bash
python3 "$PWD/scripts/build_comparison.py" --latest-version v07 --reviewed-latest
```

This mode uses `deliverables/stills/reference_aerial.png` and requires matching per-view receipts from the current master. Open the resulting `deliverables/comparison/index.html`, check its images and comparison control, and retain the documented limitations. Commit the completed source and documentation before creating the review receipt; release packaging requires a clean Git worktree and binds the review to its full HEAD revision. Generated deliverables remain ignored by Git.

Create the exact required receipt scaffold only after all release inputs exist. This command hashes the required files without marking any inspection complete and preserves an existing receipt:

```bash
python3 - <<'PY'
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path('scripts').resolve()))
from package_release import REQUIRED_FILES, file_sha

receipt = {
    'schema_version': 1,
    'source_revision': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'master_sha256': file_sha(Path('scene/protolabs-campus.blend')),
    'reviewed_at_utc': None,
    'still_review': 'pending',
    'motion_sample_review': 'pending',
    'motion_review': 'pending',
    'notes': '',
    'reviewed_files': {name: file_sha(Path(name)) for name in REQUIRED_FILES},
}
with Path('deliverables/delivery-review.json').open('x') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
PY
```

For the actual inspected bytes, set `still_review`, `motion_sample_review`, and `motion_review` to the exact value `"inspected"`; set `reviewed_at_utc` to the actual ISO 8601 UTC review time, such as `YYYY-MM-DDTHH:MM:SS+00:00`; and write nonempty `notes` describing the inspection and remaining approximations. `reviewed_files` must retain every path from `REQUIRED_FILES` mapped directly to its lowercase SHA-256 string. It covers both editable scenes, both GLBs, export/camera/material metadata, four PNGs and their render receipts, both MP4s and path manifests, and the gallery HTML/manifest. Do not change generated per-view receipts merely to change their render-time pending label: the separate final review binds those receipts by hash. Any later change to source or artifact bytes requires updating the relevant review and hashes before packaging.

Choose a new semantic version and unused destination, then run:

```bash
python3 "$PWD/scripts/package_release.py" \
  --version 0.1.0 \
  --ffmpeg "$PROTOLABS_FFMPEG" \
  --output "$PWD/../protolabs-campus-0.1.0.zip"
```

The script verifies the review, per-view PNG integrity and master/image hashes, browser-export hashes, matching sample/film paths and settings, complete film coverage, and gallery hashes against the final stills. FFmpeg fully decodes both MP4s and checks frame count, dimensions, fps and presentation cadence against their path manifests. The archive includes the clean committed source, a Git history bundle, required deliverables and review, source-image cache, preserved iteration comparison assets and selected material inputs. Raw lidar, frame sequences and installed dependencies are restored through the documented workflows. The iteration probe is not substituted for the final aerial.

`DELIVERY-MANIFEST.json` records each archived file's bytes and SHA-256, the source/master identifiers and video verification results. Every payload is read back and checked before publication. The script preserves an existing ZIP or receipt, stages files beside the chosen destination, and publishes the ZIP with `.sha256` and `.json` sidecars without overwriting existing files. Verify the ZIP checksum and manifest after extraction as well; archive integrity is separate from visual acceptance.

The packaging implementation passed an isolated 64 × 36 synthetic fixture covering a valid release, stale reviewed image, mismatching still/master receipt, accidental probe substitution, truncated film, existing-sidecar preservation and publication-failure rollback. Its workspace receipt is `work/motion-review/release-packaging-validation.json`. That fixture did not package or approve the unfinished production assets.

The v06 clean master/export checks, preserved four-view inspection and tested viewer installation/build/navigation are completed evidence. They do not constitute a complete v07 delivery run. That requires a clean directory to acquire the now-required material inputs, regenerate the updated master and both exports, render and inspect the saved views, pass the motion gate, stage matching viewer assets, build and inspect them, and verify the final archive after extraction. Private site publication and the complete encoded film also remain pending. The raw-lidar scripts are included, but a complete rerun of the packaged 174 MB pipeline and a validated UE5 application remain separate documented checks. Until those checks and visual acceptance are recorded, report the project as a reconstruction in progress.
