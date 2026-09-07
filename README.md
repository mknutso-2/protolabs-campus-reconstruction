# Protolabs · Maple Plain campus reconstruction

An editable, evidence-led exterior reconstruction of Protolabs headquarters at **5540 Pioneer Creek Drive, Maple Plain, Minnesota**. The project combines Blender scene generation, a browser exterior viewer, fixed-camera renders, and a reference comparison workflow.

**Status: work in progress.** Public evidence was acquired on September 7, 2026. Spring 2026 aerial imagery and 2022 lidar constrain the site plan, roofs, and terrain; older ground photographs constrain visible architectural detail. These sources do not prove every feature exists in the same condition today. This is not a surveyed digital twin, and full fidelity or photorealism is not claimed. The cinematic must pass a delivery-resolution motion inspection before it is considered complete.

The four **v06** stills were rendered, inspected and preserved with their master, models and snapshot manifest under `deliverables/iterations/v06/`. Their synthetic surface response prompted **v07** work on scanned materials, low-sun lighting, glazing, entrance details and generic vehicles. The v07 integrated probe is pending visual acceptance. No v06 motion sequence was rendered; the current-revision sample, complete film, private hosted viewer and final archive remain pending. The latest working branch is `feat/reference-lighting`, currently local until its source is mirrored to GitHub.

The confirmed headquarters parcel is 7.00 acres. Adjacent parking, buildings, and landscape provide context and are not all Protolabs-owned property. See [geospatial findings](research/geospatial-findings.md) and the [architecture source ledger](research/architecture-sources.json).

## Build and inspect

Use **Blender 4.2.9 LTS** for the editable master and CPU Cycles rendering. The viewer requires **Node.js 22.13 or later** and npm. Set `PROTOLABS_BLENDER` to the Blender executable, then run these commands from the repository root:

```bash
python3 "$PWD/scripts/material_quality.py" --download
"$PROTOLABS_BLENDER" --background --python-exit-code 1 \
  --python "$PWD/scripts/build_scene.py" -- --export
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/render_views.py" -- \
  --views reference_aerial --width 1600 --samples 64
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/render_views.py" -- \
  --views entrance_detail,arrival,campus_overview --width 1600 --samples 48
```

Material acquisition is now required before a fresh v07 generation. It uses ordinary Python, downloads 16.3 MB of pinned CC0 textures/HDRIs including an optional environment, and verifies sizes and SHA-256 hashes. See [material provenance](docs/material-provenance.md). These licensed surface proxies are separate from the attributed company photographs used for comparison.

The Blender build regenerates the packed editable master, full GLB, cameras, and material metadata under `scene/`. It applies `visual_finish.py` and `material_quality.py` automatically, and uses the revised original `vehicles.py` module. It also calls `scripts/export_viewer.py` to produce `protolabs-campus-viewer.glb` with approximately 30% of the leaf cards retained for browser navigation. The master and rendered foliage keep their full geometry. `scene/viewer-export.json` records SHA-256 hashes for both the master and browser GLB, plus foliage reduction; packaging verifies both files before optimization.

The remaining commands render four fixed views to `deliverables/stills/`. The current still target is 1600 × 1067, with 64 samples for the aerial and 48 for the other views. V06 completed this set; v07 must pass its probe before replacing it. The motion target is 1280 × 720 at 24 fps over six seconds. Its planned 24-frame sample covers frames 61–84 in the middle of the path, followed by checks of endpoint frames 1 and 144. Sample inspection and the complete encoded film remain pending. A saved camera and a completed render provide comparison inputs, not automatic visual acceptance.

Follow [the reproduction guide](docs/reproduction.md) to acquire Blender, prepare viewer assets, start the local viewer, render a motion sample, and package a versioned delivery. The guide distinguishes implemented commands from acceptance checks that still require inspection.

Install viewer dependencies with `npm ci` inside `viewer/` **before** running `scripts/package_viewer.py`: packaging invokes the locked glTF optimizer through `npx` on the reduced browser GLB. Acquire the three comparison photographs with `python3 "$PWD/scripts/acquire_references.py"`, or check an existing cache without network access with `python3 "$PWD/scripts/acquire_references.py" --verify-only`. The committed reference manifest pins their sizes and SHA-256 hashes.

Raw lidar acquisition and processing scripts are included under [scripts/research](scripts/research/README.md). The northern context uses a derived 5 m ground grid and 102 eligible canopy-envelope candidates; they are not surveyed trunks or verified species. Original pipeline packaging passed its dry-run, imports and source checks; the full raw-data pipeline was not rerun for that check. The separate canopy derivation was rerun against its hash-verified cached tile.

The [clean v06 source verification](docs/fresh-checkout-verification.md) passed master generation, both exports, canopy placement, complete master foliage, camera/material baselines and the corrected geometry checker. Viewer revision `5bf2a27` passed lint, clean dependency installation, production build and local navigation checks, including visible walk controls and rotated exterior footprints. The offline dependency install reused an existing npm cache; it does not promise offline installation without that cache. These checks do not validate the new v07 material integration or complete the delivery gates.

## Project records

| Record | Purpose |
| --- | --- |
| [Project brief](docs/brief.md) | Scope, milestones, and acceptance gates |
| [Prioritized backlog](docs/backlog.md) | Work remaining in the reconstruction |
| [GitHub issues](https://github.com/mknutso-2/protolabs-campus-reconstruction/issues) | Prioritized tracked work |
| [Reproduction guide](docs/reproduction.md) | Setup, generation, render, export, viewing, and delivery |
| [Runtime evaluation](docs/runtime-evaluation.md) | Tested host, measured draft renders, and UE5 decision |
| [Fresh source verification](docs/fresh-checkout-verification.md) | Verified v06 build/export and retained historical geometry checks |
| [Material provenance](docs/material-provenance.md) | CC0 asset hashes, acquisition, lighting alignment and shader limitations |
| [Canopy evidence](docs/canopy-evidence.md) | Northern ground and vegetation-envelope constraints |
| [Geospatial sources](research/geospatial-sources.json) | Parcel, aerial, lidar, and footprint provenance |
| [Architecture sources](research/architecture-sources.json) | Published images, dates, attribution, and confidence |
| [Geometry notes](research/geometry-notes.md) | Visible architectural observations and unresolved details |
| [Vegetation provenance](docs/vegetation-provenance.md) | Original tree/shrub geometry and packed leaf textures |
| [Vehicle provenance](docs/vehicle-provenance.md) | V07 original vehicle assets, isolated checks and placement limitations |

## Source control and large files

The [GitHub project](https://github.com/mknutso-2/protolabs-campus-reconstruction) is private. Source, small geometric constraints, camera definitions, dependency locks, and provenance belong in Git. Blender files, GLB exports, renders, video, dependencies, and raw reference caches are regenerated or supplied in versioned archives with SHA-256 manifests. Git LFS is not required for the current source-first workflow.

Reference photography has its own rights. Public access does not establish a redistribution license. Preserve publisher attribution and fetch references locally where required; do not treat them as freely licensed texture assets or include them in a public artifact bundle without appropriate rights.

UE5 has been evaluated but is not delivered as a validated application on the current GTX 660M / 8 GB host. The glTF browser viewer provides the exterior inspection route; Blender remains the master. See the [runtime evaluation](docs/runtime-evaluation.md) for the evidence and limitations.
