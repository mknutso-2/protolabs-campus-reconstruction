# Protolabs · Maple Plain campus reconstruction

An editable, evidence-led exterior reconstruction of Protolabs headquarters at **5540 Pioneer Creek Drive, Maple Plain, Minnesota**. The project combines Blender scene generation, a browser exterior viewer, fixed-camera renders, and a reference comparison workflow.

**Status: work in progress.** Public evidence was acquired on September 7, 2026. Spring 2026 aerial imagery and 2022 lidar constrain the site plan, roofs, and terrain; older ground photographs constrain visible architectural detail. These sources do not prove every feature exists in the same condition today. This is not a surveyed digital twin, and full fidelity or photorealism is not claimed. The cinematic must pass a delivery-resolution motion inspection before it is considered complete.

The confirmed headquarters parcel is 7.00 acres. Adjacent parking, buildings, and landscape provide context and are not all Protolabs-owned property. See [geospatial findings](research/geospatial-findings.md) and the [architecture source ledger](research/architecture-sources.json).

## Build and inspect

Use **Blender 4.2.9 LTS** for the editable master and CPU Cycles rendering. The viewer requires **Node.js 22.13 or later** and npm. Set `PROTOLABS_BLENDER` to the Blender executable, then run these commands from the repository root:

```bash
"$PROTOLABS_BLENDER" --background --python-exit-code 1 \
  --python "$PWD/scripts/build_scene.py" -- --export
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/render_views.py" -- \
  --views reference_aerial --width 1600 --samples 64
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/render_views.py" -- \
  --views entrance_detail,arrival,campus_overview --width 1600 --samples 48
```

The first command regenerates the packed editable master, full GLB, cameras, and material metadata under `scene/`. It also calls `scripts/export_viewer.py` to produce `protolabs-campus-viewer.glb` with approximately 30% of the leaf cards retained for browser navigation. The master and rendered foliage keep their full geometry. `scene/viewer-export.json` records the master SHA-256 and foliage reduction; viewer packaging requires that metadata to match the current master.

The remaining commands render four fixed views to `deliverables/stills/`. The current still target is 1600 × 1067, with 64 samples for the aerial and 48 for the other views; the latest v06 full-view renders remain pending. The motion target is 1280 × 720 at 24 fps over six seconds. Its planned 24-frame sample covers frames 61–84 in the middle of the path, followed by checks of endpoint frames 1 and 144. Sample inspection and the complete encoded film remain pending. A saved camera and a completed render provide comparison inputs, not automatic visual acceptance.

Follow [the reproduction guide](docs/reproduction.md) to acquire Blender, prepare viewer assets, start the local viewer, render a motion sample, and package a versioned delivery. The guide distinguishes implemented commands from acceptance checks that still require inspection.

Install viewer dependencies with `npm ci` inside `viewer/` **before** running `scripts/package_viewer.py`: packaging invokes the locked glTF optimizer through `npx` on the reduced browser GLB. Acquire the three comparison photographs with `python3 "$PWD/scripts/acquire_references.py"`, or check an existing cache without network access with `python3 "$PWD/scripts/acquire_references.py" --verify-only`. The committed reference manifest pins their sizes and SHA-256 hashes.

Raw lidar acquisition and processing scripts are included under [scripts/research](scripts/research/README.md). The northern context now uses a derived 5 m ground grid and 102 eligible canopy-envelope candidates, with provenance and `scripts/research/derive_canopy.py` included. The candidates constrain inferred vegetation height and position; they are not surveyed trunks or verified species. Original pipeline packaging passed its dry-run, imports, and source checks; the full raw-data pipeline was not rerun for that check. A clean viewer dependency installation with `npm ci --offline` completed using the existing package cache (746 packages, approximately one minute); the subsequent build and fresh scene validation remain separate checks.

## Project records

| Record | Purpose |
| --- | --- |
| [Project brief](docs/brief.md) | Scope, milestones, and acceptance gates |
| [Prioritized backlog](docs/backlog.md) | Work remaining in the reconstruction |
| [GitHub issues](https://github.com/mknutso-2/protolabs-campus-reconstruction/issues) | Prioritized tracked work |
| [Reproduction guide](docs/reproduction.md) | Setup, generation, render, export, viewing, and delivery |
| [Runtime evaluation](docs/runtime-evaluation.md) | Tested host, measured draft renders, and UE5 decision |
| [Geospatial sources](research/geospatial-sources.json) | Parcel, aerial, lidar, and footprint provenance |
| [Architecture sources](research/architecture-sources.json) | Published images, dates, attribution, and confidence |
| [Geometry notes](research/geometry-notes.md) | Visible architectural observations and unresolved details |
| [Vegetation provenance](docs/vegetation-provenance.md) | Original tree/shrub geometry and packed leaf textures |
| [Vehicle provenance](docs/vehicles-provenance.md) | Original vehicle assets and their limitations |

## Source control and large files

The [GitHub project](https://github.com/mknutso-2/protolabs-campus-reconstruction) is private. Source, small geometric constraints, camera definitions, dependency locks, and provenance belong in Git. Blender files, GLB exports, renders, video, dependencies, and raw reference caches are regenerated or supplied in versioned archives with SHA-256 manifests. Git LFS is not required for the current source-first workflow.

Reference photography has its own rights. Public access does not establish a redistribution license. Preserve publisher attribution and fetch references locally where required; do not treat them as freely licensed texture assets or include them in a public artifact bundle without appropriate rights.

UE5 has been evaluated but is not delivered as a validated application on the current GTX 660M / 8 GB host. The glTF browser viewer provides the exterior inspection route; Blender remains the master. See the [runtime evaluation](docs/runtime-evaluation.md) for the evidence and limitations.
