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

The [land-cover evidence and geometric limits](nlcd-context-evidence.md) still apply. The isolated preview showed a thin irregular far woodland improvement while broad open ground remained; the audit does not establish source-like continuous woodland or final photographic acceptance. The four production stills were rendering when this note was written, and motion had not been verified.
