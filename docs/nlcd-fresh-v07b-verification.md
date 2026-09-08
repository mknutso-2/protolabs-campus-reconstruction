# Fresh v07b NLCD verification

The independent read-only audit passed for the clean source `e58086642ca3672792686064294eeb6997b5b73b` after build/export completed on 2026-09-07. This note covers the added NLCD layer, its exported geometry/materials, and fixed cameras. Paint, apron, protected near geometry, browser runtime and final still/motion acceptance are separate checks.

| Artifact | SHA-256 |
|---|---|
| Saved master | `7dd2ff5a1253f1153e70c4ba09a1bb7806c3d326b950d91c629635bb5cc43cc0` |
| Full GLB | `0e62654690caddb1368b1a1c7d7105b6e57fcf405d0ed6abd1d50808316e5b59` |
| Browser GLB before viewer packaging | `b3b3f1fcc696eeff4d435b7ac89e78d67dd29573669f891d3cf5a7dadec11c83` |

The saved master contains exactly **347 inferred multi-crown groups in 36 merged patch objects**, totaling **481,636 triangles**. Every selected cell and all eight neighboring pixels satisfy the pinned forest-class rule. Measured stored vertices remain at least **1.004150 m inside their own 30 m cell**. Root-centroid raycasts against the actual regional terrain found **0 m ground error**; maximum stored height error against the inferred placement receipt was **0.000000944 m**. These checks verify geometry against its disclosed inputs, not measured current canopy height or forest density.

The audit compared each patch's exact triangle-position multiset, grouped by material, against both GLBs. All 36 patches matched the saved master in both exports despite glTF vertex splitting. Material base color, roughness and metallic factors also matched. The browser exporter therefore retained this NLCD topology; the leaf-card reduction did not affect it. The viewer export receipt's master and payload hashes matched the actual files. This check precedes later viewer material preparation, compression and browser runtime checks.

All four actual saved cameras—`reference_aerial`, `entrance_detail`, `arrival` and `campus_overview`—matched their recorded position, Euler rotation and lens within Blender float storage precision, with `clip_end = 4500`. The new `cameras.json` is byte-identical to the preceding `a6632753…` master's camera JSON.

The audit loaded the master with Blender 4.2.9 and one thread. It performed no render or save, and verified that the master file hash remained unchanged. Scratch evidence and reproduction scripts are under `work/nlcd-context/fresh-v07b/`: `audit_master.py`, `audit-master.log`, `master-audit.json`, `audit_glbs.py` and `glb-audit.json`. The production artifact directory is `work/final-source-v07b/scene/`.

The [land-cover evidence and geometric limits](nlcd-context-evidence.md) still apply. The isolated preview showed a thin irregular far woodland improvement while broad open ground remained; the audit does not establish source-like continuous woodland or final photographic acceptance. The later full-size still review is recorded below; motion has not been verified by this audit.


The independent review opened both completed 1600×1067 PNGs and verified their image hashes against receipts bound to this master:

| Still | SHA-256 | Land/water observation |
|---|---|---|
| `reference_aerial` | `f2a5d3eccf0be2fd8729271dcf6e46ab3d8caee185d01e7362c07c0a7b41f495` | Far forest additions agree with the accepted isolated preview. Broad tan ground and gaps remain. No new major woodland platform or near-tree crowding was detected. The pond is mostly roof-occluded. |
| `campus_overview` | `7d3f30d46cc277bf2eb16443555e2542820791ba69c750ef0f972d962880eebe` | The pond is visibly flat and the former folded/raised western tip is gone; the shoreline remains coarse. A thin dark line at the main/north terrain join needs a bounded correction. |

The overview's line begins near pixel `(606,35)` and follows the projected shared `y=220` boundary. A read-only check of the full GLB found **81 matching boundary vertices with the north surface 0.119908–0.120754 m above the main surface**. Source inspection identifies the cause: the main mesh uses `tz−0.12`, while the north mesh starts its existing 10 m blend at unlowered `ground()`. The root task was notified to use the actual rendered main-edge elevation at that blend's start; no geometry was changed by this review. This issue is distinct from the verified NLCD layer and prevents an unqualified landscape acceptance of this particular master. Receipts: `work/nlcd-context/fresh-v07b/still-review.json` and `ground-join-audit.json`.
