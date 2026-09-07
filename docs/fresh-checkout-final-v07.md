# Final v07 clean-source verification — e9ed871

**Clean generation, both GLB exports, the geometry checker and the independent saved-master audit pass for source `e9ed8710a0a901b0ee21744a27561241998254e1`.** This checkpoint verifies construction and artifact integrity. It does not accept the four final stills, motion, browser appearance/performance or release packaging. The earlier [v07 checkpoint](fresh-checkout-v07.md) remains unchanged.

Verified on 7 September 2026 using Blender **4.2.9 LTS**, build `a10f621e649a`. The clean local clone at `work/final-source-v07` contains **105 tracked files**, tree `0650793e4719b5e0c8f3d015a9769b26792ead47`, with independent Git objects. Its initial clean-state receipt records that only **11 checksum-verified material/HDRI cache files** were copied before generation. The audit independently rechecked all 11 files and the tracked font/license hashes; no prior scene binaries, local generator changes or new downloads were used.

After generation, every tracked file matches its committed bytes except regenerated `scene/materials.json`. Its **30 fallback entries** comprise the prior 27 plus `DistantCanopy_Group_0/1/2`; current asphalt, mown-grass and meadow albedos match the saved materials. Camera JSON remains byte-identical to source. The active tone is **AgX Medium High Contrast, exposure −0.35, gamma 1.05**; the retained coated-glass values also match the source settings.

## Saved artifacts

The build log ends with both exports, `SCENE_READY 3400` and `Blender quit`. These hashes identify the completed clean generation; they do not promise binary determinism across platforms.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `scene/protolabs-campus.blend` | 59,396,976 | `a6632753e411a1b63d9bef90614a80a259ffd2620021107668b1f8a0ac8c0155` |
| `scene/protolabs-campus.glb` | 45,311,368 | `0cd803bf8d9fd921533fc1c69c155c0d633bbb63e4d9c2210fe89fc730288dc6` |
| `scene/protolabs-campus-viewer.glb` | 42,253,288 | `82ef1a95a6f9691b65bb63c41f6904e77529c18f52430c8f953fce23a8f5d7ef` |
| `scene/viewer-export.json` | 564 | `d02bec16a3ffb0440cb982a61e1c921a867caf1eb936a8eeee23df5ae033a022` |
| `scene/materials.json` | 4,336 | `1d2bf0cde7655713e1be23f2eea214a35ebf3adf746e15ba327e9746afb3bac0` |
| `scene/cameras.json` | 1,393 | `852823aa47e727b08bdd79a2fbe89161f614a495ec14196eb23bc9cd1dd9ae1a` |

Both GLBs have version-2 headers, correct declared lengths and complete parseable JSON/BIN chunks. Each contains **1,944 meshes, 3,366 nodes, 49 materials and 14 embedded images**, with no external image URI. The browser export receipt binds its GLB and master hashes. This structural check does not replace runtime inspection or later Meshopt packaging checks.

## Independent saved-master checks

The audit reopened the completed master with one Blender thread, after build/export ended, without rendering, repairs or saving. It also reopened the prior clean master only to compare protected geometry. The final master hash remained unchanged.

- **Typography:** all five text objects use the packed **759,720-byte DejaVu Sans Book** font, SHA-256 `ae7b7855e115a5966d8b1b3f80f254ccc117ec86f9965e202ee2940453837280`. This pins the selected substitute, not exact corporate typography.
- **Foliage:** all three source templates retain **10,000 leaf cards and 22,988 triangles**. No temporary browser-reduction mesh is saved. The master has **47 campus trees** (41 lidar-supported heights, six inferred neighborhood heights), **102 north envelopes**, and **1,200 distant instances**: 270 full trees, 869 existing 2,000-card meshes and 61 inferred remote crown groups. The browser exporter preserves those 869 already-reduced instances. Visible vegetation counts agree with its receipt: **15,737,024** source triangles and **9,840,564** browser triangles.
- **Protected geometry:** mesh coordinates, face topology and transforms exactly match prior master `b1d83d71b06d7e57c0d157d29ffe8b8025675aeaffb3211ebb0c42118bb9e2a1` for the two near lidar grounds, canted ribbon roof, main occupied volume and entrance apron. Campus height/base construction errors are below **0.000001 m**; this is transform consistency, not survey accuracy.
- **Regional ground:** one **50 m source DEM**, with 64,216 vertices and 126,952 triangles, supplies the regional surface. No face center enters its two measured-ground holes, and all distant-tree centers remain outside the protected near grids. Its external 75 m transition and inferred woody belts remain regional scenery, not measured detailed landscaping.
- **Water:** both basin-clipped meshes are horizontal at local **Z −11.109999657 m**. Ground ray casts at all water vertices give at least **0.0099878 m** clearance, consistent with the intended 0.01 m offset and float precision. The water level is a dated lidar-supported interpretation; this does not establish current water elevation or bathymetry.
- **Parking and entrance:** corrected paint has **zero vertices inside the apron**, matches terrain plus 0.04 m within 0.000001 m, and replaces 38 old row stripes plus ten old aisle curves. Its row counts are 5/6/9/10, not official capacity. The final fascia segment terminates at **Z 4.02 m**, superseding the occluded aerial bottom-right pick. All **seven required closed-box checks** pass. All four cameras agree with their saved records within floating-point precision.

## Evidence and remaining review

Workspace receipts are `work/final-source-v07-inputs.json`, the completed build/export and geometry stage logs, `work/motion-review/final-v07-artifact-validation.json`, and `work/motion-review/final-v07-master-inspection.json`. The audit scripts and log are retained beside the latter receipts. The background job continues separately with four **1600 × 1067, 64-sample** stills and their hash-bound receipts in the clean clone's `deliverables/stills/`.

No still or motion is accepted by this document. Final visual review must bind the completed four images and any motion sample/film to this master, and later packaging must bind the actual reviewed viewer and delivery files. The model remains an evidence-led exterior reconstruction with dated geospatial inputs and documented photo interpretations.

## Subsequent aerial review: revised master required

The first completed full-resolution aerial from source `e9ed871` / master `a6632753e411a1b63d9bef90614a80a259ffd2620021107668b1f8a0ac8c0155` was inspected and revealed parking dividers partially occluded by the asphalt. The passing numeric paint check above compares vertices with the bilinear terrain sampler; it does not establish clearance above the actual triangulated asphalt surface. Generation and the bounded checks remain valid receipts for this source, but the paint needs surface-conforming correction and a revised master with new artifact hashes. This checkpoint has **no final-delivery acceptance**; it must not be reused as visual approval for the revised build.

The remaining three full stills were also inspected, with all four image hashes, PNG integrity and render receipts verified in `work/motion-review/final-v07-still-review.json`. The entrance exposed protruding/floating sidewalk-joint curves; the overview confirms the former folded water surface is gone. Apart from the pavement issues, no additional major new mesh-intersection blocker was identified. Sparse regional scenery, simplified shoreline and architectural/planting details remain fidelity limitations. All four stills remain unaccepted for final delivery.

A subsequent bounded [apron joint helper](../scripts/apron_finish.py) preserves the ten original XY lines where they lie inside the apron, clips them with a 0.025 m boundary margin, and follows the actual evaluated top triangles. It includes every crossed triangle edge and at most 0.10 m spacing; it never uses the bilinear terrain sampler. The existing 0.01 m radius sits 0.008 m into the concrete as an interpreted shallow dark joint. Apron/curb geometry and all other objects remain unchanged. Integrate with `from apron_finish import apply_apron_finish; apply_apron_finish(ROOT)` after the apron exists and before final material/export passes.

An isolated **576 × 171, 32-sample** entrance crop was inspected: the protruding lines are gone and the retained joints are subtle and flush. The fixture's 1,105 centerline/intermediate samples agree with actual top minus 0.008 m within **0.000001 m**; boundary clearance is at least **0.0249999 m**, and the evaluated visible cap rises at most **0.000761 m** above the surface. Only ten curve data blocks change; all other meshes/transforms, object count and saved master hash are unchanged, and a repeated call is identical. The receipt is `work/motion-review/apron-finish-validation.json`. This local correction still requires integration into the revised master and full-view review.

A final crop diagnostic identified a separate triangular overlap: the rock bed was 0.34 mm above the apron at one pixel, but below it nearby. Both source slabs had nominal top Z 0.16 m before different terrain triangulations. The revised `apply_apron_finish` now subtracts the **actual apron footprint** from the existing rock triangles, preserving exposed elevations and materials. It produces two closed, outward-facing rock components and no rock vertex/triangle center strictly inside the apron; 211 interior rays miss the rock, and 30 exposed-surface samples retain elevations within **0.000008 m**. The **576 × 171, 32-sample** crop was independently and root-inspected: the interior triangular patch is gone. Fresh and earlier joint-marker upgrade paths pass. The intended changes are explicitly **ten joint curve data blocks plus `Facade landscape river stones` mesh data**; apron, curbs, other meshes/transforms and saved master remain unchanged. See `work/motion-review/apron-rock-finish-validation.json` and `apron-upgrade-validation.json`. The next fresh-source audit must record this intended rock-mesh difference separately from protected geometry.
