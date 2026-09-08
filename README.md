# Protolabs · Maple Plain campus reconstruction

An editable, evidence-led exterior reconstruction of Protolabs headquarters at **5540 Pioneer Creek Drive, Maple Plain, Minnesota**. The project combines Blender scene generation, a browser exterior viewer, fixed-camera renders, and a reference comparison workflow.

**Status: v0.1 research reconstruction, inspected.** Public evidence was acquired on September 7, 2026. Spring 2026 aerial imagery and 2022 lidar constrain the site plan, roofs, and terrain; older ground photographs constrain visible architectural detail. These sources do not prove every feature exists in the same condition today. This is not a surveyed digital twin, and full fidelity or photorealism is not claimed. The complete cinematic has passed its delivery-resolution image and playback review.

The [clean v07c build](docs/fresh-checkout-v07c.md) generated the editable master, both GLBs and all four **1600 × 1067, 64-sample** stills. All four images have been inspected. The final static set includes corrected entrance returns, pavement markings and joints, a flat pond, a continuous terrain join and conservative distant woodland coverage. Earlier iterations through v06 remain intact in the comparison gallery. The [accuracy account](docs/accuracy-summary.md) explains the remaining synthetic surfaces, repeated vegetation and uncertain fine detail. The accepted motion sample was followed by the complete 144-frame render and encoded film. The [complete-film review](research/v07c-cinematic-review.json) accepted it with documented limits at 01:55:53 UTC on September 8, 2026. Current local viewer checks have passed within their recorded scope, and all 12 final viewer assets have passed packaging. Final local movie integration and an actual extracted-archive build passed; see [delivery verification](docs/delivery-verification.md). Private-site publication requires the user's separate approval; no upload or deployment has occurred.

The confirmed headquarters parcel is 7.00 acres. Adjacent parking, buildings, and landscape provide context and are not all Protolabs-owned property. See [geospatial findings](research/geospatial-findings.md) and the [architecture source ledger](research/architecture-sources.json).

## Open the delivery

The versioned local bundle `protolabs-campus-0.1.0.zip` contains the inspected assets, source, Git history and integrity manifest. Its adjacent `.json` and `.sha256` record the final archive hash. See [delivery verification](docs/delivery-verification.md) for the actual extraction/build check and [accuracy limits](docs/accuracy-summary.md).

| Deliverable | Location inside the extracted project |
| --- | --- |
| Editable Blender master | `scene/protolabs-campus.blend` |
| Exterior walkthrough | `viewer/`: run `npm ci`, `npm run build`, then `npm start` |
| Four fixed-view stills | `deliverables/stills/` |
| Six-second film | `deliverables/flythrough.mp4` |
| Editable film scene | `scene/protolabs-motion.blend` |
| Reference and iteration gallery | Open `deliverables/comparison/index.html` |

The private [GitHub project](https://github.com/mknutso-2/protolabs-campus-reconstruction) contains reproducible source. Large binaries are supplied in the local archive; a source-only checkout recreates them with the guide below. The walkthrough's 12 model/image/movie payload files are already included in the archive.

## Build and inspect

Use **Blender 4.2.9 LTS** for the editable master and CPU Cycles rendering. The viewer requires **Node.js 22.13 or later** and npm. Set `PROTOLABS_BLENDER` to the Blender executable, then run these commands from the repository root:

```bash
python3 "$PWD/scripts/material_quality.py" --download
"$PROTOLABS_BLENDER" --background --python-exit-code 1 \
  --python "$PWD/scripts/build_scene.py" -- --export
"$PROTOLABS_BLENDER" --background "$PWD/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python "$PWD/scripts/render_views.py" -- \
  --views reference_aerial,entrance_detail,arrival,campus_overview \
  --width 1600 --samples 64 --out deliverables/stills
```

Material acquisition is now required before a fresh v07 generation. It uses ordinary Python, downloads 16.3 MB of pinned CC0 textures/HDRIs including an optional environment, and verifies sizes and SHA-256 hashes. See [material provenance](docs/material-provenance.md). These licensed surface proxies are separate from the attributed company photographs used for comparison.

The Blender build regenerates the packed editable master, full GLB, cameras, and material metadata under `scene/`. It applies the entrance, monument, water, apron, parking and material finish helpers automatically, and uses the original vehicle and vegetation modules. The lower fascia helper reads [its fixed-camera fit and uncertainty](research/frontage-fascia-fit.json); this is photo-inferred geometry with an interpreted depth. Its hidden terminal segment rises to meet the entrance header, superseding one occluded aerial corner pick; it is not a measured structural specification. It also calls `scripts/export_viewer.py` to produce `protolabs-campus-viewer.glb` with approximately 30% of campus/north leaf cards retained for browser navigation. Named distant woodland leaf-card objects use existing opaque crown proxies fitted to their original bounds; solid distant and NLCD canopy groups remain intact. The master and rendered foliage keep their full geometry. [The bounded performance check](docs/viewer-performance.md) records this browser-only approximation and its measured limits. `scene/viewer-export.json` records SHA-256 hashes for both the master and browser GLB, plus foliage reduction; packaging verifies both files before optimization.

The render command writes all four fixed views to `deliverables/stills/`. The current production target is **1600 × 1067 and 64 Cycles samples for every view**. Each PNG has a matching JSON receipt binding its image and master hashes, camera and render settings. The separate `deliverables/reference_aerial.png` remains an iteration probe and cannot replace the final aerial. The v07c set has passed full-image inspection with documented limitations; the preserved v06 set used an earlier sample budget. The film is 1280 × 720 at 24 fps over six seconds. The 24-frame sample (61–84) and endpoints 1/144 passed the [recorded inspection](docs/motion-review.md#v07c-sample-accepted-for-full-film-rendering--7-september-2026) at 16 Cycles samples, including actual encoded playback. Mild pixel-level foliage and roof texture variation was accepted. All 144 film frames finished at 01:41:05 UTC on September 8, 2026; the resulting movie passed complete decoding and actual normal/fullscreen playback. Independent image review also passed, and the film is accepted for versioned delivery with the fine-detail variation and scenery/material limitations retained in the [motion record](docs/motion-review.md).

The source preserves full foliage in the Blender master and uses separate geometry for distant context. [Campus-tree evidence](docs/campus-tree-evidence.md), [distant terrain and woods](docs/distant-context.md), [water-level evidence](docs/water-surface-evidence.md), and [parking corrections](docs/parking-markings.md) distinguish measured inputs from inferred placement, shape, seasonal condition and fine detail.

Follow [the reproduction guide](docs/reproduction.md) to acquire Blender, prepare viewer assets, start the local viewer, render a motion sample, and package a versioned delivery. The guide distinguishes implemented commands from acceptance checks that still require inspection.

Install viewer dependencies with `npm ci` inside `viewer/` **before** running `scripts/package_viewer.py`: packaging invokes the locked glTF optimizer through `npx` on the reduced browser GLB. Acquire the three comparison photographs with `python3 "$PWD/scripts/acquire_references.py"`, or check an existing cache without network access with `python3 "$PWD/scripts/acquire_references.py" --verify-only`. The committed reference manifest pins their sizes and SHA-256 hashes.

Browser packaging preserves full-precision terrain positions and distinct mean surface colors; see [the material and export checks](docs/viewer-materials.md). Its generated `scene/viewer-package.json` binds the optimized model to the master, source GLB and palette. The final receipt also hashes all 12 generated viewer assets: model/camera/terrain/material data, four JPEG stills, three reference images and the movie. Release packaging includes those exact files, verifies copied assets against their originals and requires the successful lossless-position check. An extracted complete delivery can install viewer dependencies and build directly without repackaging its visual assets.

Raw lidar acquisition and processing scripts are included under [scripts/research](scripts/research/README.md). The northern context uses a derived 5 m ground grid and 102 eligible canopy-envelope candidates; they are not surveyed trunks or verified species. Original pipeline packaging passed its dry-run, imports and source checks; the full raw-data pipeline was not rerun for that check. The separate canopy derivation was rerun against its hash-verified cached tile.

The [clean v06 source verification](docs/fresh-checkout-verification.md) passed master generation, both exports, canopy placement, complete master foliage, camera/material baselines and the corrected geometry checker. Viewer revision `5bf2a27` passed lint, clean dependency installation, production build and local navigation checks, including visible walk controls and rotated exterior footprints. The offline dependency install reused an existing npm cache; it does not promise offline installation without that cache. The subsequent [fresh v07 frontage check](docs/fresh-checkout-v07.md) also passed generation, exports and bounded geometry checks. The [clean v07c verification](docs/fresh-checkout-v07c.md) covers the final integrated static source, exports and four production images. Motion and hosted delivery are tracked separately.

## Project records

| Record | Purpose |
| --- | --- |
| [Accuracy account](docs/accuracy-summary.md) | Current evidence and visible limitations |
| [Current static verification](docs/fresh-checkout-v07c.md) | Clean source, exact artifacts and four inspected stills |
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

[PR #7](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/7) and [PR #8](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/8) are merged. [PR #9](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/9) contains the final v07 delivery changes. The archive manifest identifies its local source revision; GitHub records the integration into main.

Reference photography has its own rights. Public access does not establish a redistribution license. Preserve publisher attribution and fetch references locally where required; do not treat them as freely licensed texture assets or include them in a public artifact bundle without appropriate rights.

UE5 has been evaluated; the glTF browser viewer is the selected exterior walkthrough, and Blender remains the editable master. A future UE5 application and a complete raw-research reacquisition are optional follow-up work. See the [runtime evaluation](docs/runtime-evaluation.md) for the host evidence and limitations.
