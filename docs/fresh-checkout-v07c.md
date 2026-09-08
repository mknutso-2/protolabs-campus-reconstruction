# Clean v07c static verification

**Static verification is complete for clean source `e29ad4b9e9a4a15c3de4772288c105aca2bd8a56`.** The source generated the packed master, full and raw browser GLBs, passed the geometry checks, and produced four actual **1600×1067, 64-sample** stills inspected by the root reviewer. This checkpoint preceded the later accepted sample and current local viewer inspection, recorded separately in [motion review](motion-review.md) and [browser verification](viewer-verification.md). The later [complete-film review](../research/v07c-cinematic-review.json) accepted the film with documented limits on September 8, 2026, and final local movie integration passed. This static record does not certify motion, approved private deployment, release packaging or photographic equivalence.

The independent local clone at `work/final-source-v07c` began clean, using tree `e1c06d628b8f56922f7ce00506a9fafabb339425`. Only **11 pinned material/HDRI cache inputs totaling 16,298,653 bytes** were copied: nine asphalt, grass and concrete maps plus two HDRIs. Their sizes and SHA-256 hashes were independently rechecked against `work/final-source-v07c-inputs.json`; no prior binary scenes or outputs were used. Geospatial inputs were the tracked derived JSONs. The checkout still reports no tracked changes after generation.

Blender **4.2.9 LTS**, build `a10f621e649a`, completed generation/export and the geometry stage. The seven required closed-box winding checks and below-ground surround check passed. The master is 86,596,088 bytes; full GLB 54,917,528 bytes; raw browser GLB 50,520,632 bytes. These hashes identify these verified files, not a promise of cross-platform binary determinism.

| Artifact | SHA-256 |
|---|---|
| `scene/protolabs-campus.blend` | `3d861d6c2e1c54f7c144d52c5e74f21568b18d047a326631405c9da1956b8e5a` |
| `scene/protolabs-campus.glb` | `2916b2fe580ff1e25296fc3110c7cacbc363fc7d570fe3b5cad7f0024f474860` |
| `scene/protolabs-campus-viewer.glb` | `3dae8303843f07867e092581844c6ccc43d90616bb40819cc3d3623ef588a876` |
| `scene/viewer-export.json` | `536acbe48985d24fa2fc4438bc46b464cc3adbcd8af404087c554feee8ebc798` |
| `scene/cameras.json` | `852823aa47e727b08bdd79a2fbe89161f614a495ec14196eb23bc9cd1dd9ae1a` |
| `scene/materials.json` | `1d2bf0cde7655713e1be23f2eea214a35ebf3adf746e15ba327e9746afb3bac0` |
| `reference_aerial.png` | `1f9dea29ad94af94883b18f64cc50afd845cf949cfd185115fcebf197d05d6d3` |
| `reference_aerial.json` | `2ce2403ea7da86084caf974c21cc020fcd94619d4d0284972b40c67c9819bc7d` |
| `entrance_detail.png` | `94f2bdf47e14f2cff7b8b1967367941e26bd21e13891c753cb5b0b0af6105d1e` |
| `entrance_detail.json` | `d537b5c92fdc9721f380f4d041761b5c2643e1342e5ad9e047097a2b58f66d2c` |
| `arrival.png` | `4ba39ec52830b22611d73b730738ad6d70ce71cc16289346e399f23cf0446c38` |
| `arrival.json` | `eb940e4424154874866043db2799794d9a2d985d3cc58ed54cd90ba4873872db` |
| `campus_overview.png` | `09dfef91f67d09f9e13fd2eff8b82a76bf634d5780c035df3fe748409123302c` |
| `campus_overview.json` | `14ff18894324b403635ed398654780dae0769ef2456553579a10a3cd315899b7` |

All 14 hashes above were checked against the actual files. Each still PNG passed integrity/dimension checks; its receipt records 64 samples and binds it to master `3d861d6c…`. The viewer receipt binds that master to raw browser GLB `3dae8303…`. Later prepared/optimized browser bytes and their separate checks belong to the [companion browser verification](viewer-verification.md).

The root's completed static inspection is recorded at **2026-09-07 23:13 UTC** in `work/v07c-still-review.json`, superseding the job record's earlier rendering/inspection-pending status. The aerial shows legible frontage, crowns and corrected parking/apron; the entrance and arrival views show coherent fascia, truss, glazing and foreground transitions without a newly exposed overlap. The overview shows the former ground seam removed and the pond flat. Broad open background, smooth terrain, coarse shoreline, repeated planting, interpreted details and synthetic material/reflection response remain visible limits; see the [accuracy summary](accuracy-summary.md).

An independent read-only comparison with preserved master `7dd2ff5a…` confirmed the bounded join correction: main terrain coordinates/topology unchanged; **81 shared `y=220` vertices match exactly**; only 162 north vertices at `y=220/225` change; north geometry at and beyond `y=230` remains identical. Only two regional boundary vertices change, by −0.059944 and −0.060226 m. All **1,388 protected tree/template/cluster objects** retain their links/transforms, and all **45 unique source meshes** retain coordinate/topology hashes. The actual full-size overview was independently inspected with its hash verified: the seam is absent, the flat pond holds, and no new major visible artifact from the correction was found. No render or save was performed by that clean-master audit. Details and the earlier failure remain in the [terrain-join record](terrain-join-correction.md).

Workspace evidence consists of `work/final-source-v07c-job.json`, its build/export and geometry logs, `work/final-source-v07c-inputs.json`, `work/v07c-still-review.json`, and `work/terrain-join-fix/fresh-v07c/{audit-report,overview-review}.json`. [Reproduction instructions](reproduction.md), the [earlier clean-source checkpoint](fresh-checkout-final-v07.md), and the [v07b NLCD audit](nlcd-fresh-v07b-verification.md) preserve the method and relevant history. This static checkpoint does not certify motion, runtime deployment or release packaging.


## Source continuity after the static build

A Git comparison from clean build revision `e29ad4b9e9a4a15c3de4772288c105aca2bd8a56` to `fc53ab50a30920c1aadc11b8d759af570cd3dbf1` found no changes to the master scene generator, finish helpers, vegetation/vehicle modules, pinned font, asset definitions or measured research inputs. The only changed production scripts in those trees are the motion path, comparison gallery, viewer packager and release packager; the changed research files are four motion/browser review records. This establishes source continuity for the accepted static build without treating later documentation or browser-interface changes as a new master render. It does not replace the separate motion, browser, publication and archive checks.
