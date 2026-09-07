# Fresh v07 source verification — cd7cf70

**Clean generation, both GLB exports, the bounded geometry checker and independent saved-master inspection pass for `cd7cf7066aeb4850ab9de171d9ef45e01434442f`.** The 1200 × 800 aerial probe was inspected: the revised fascia, lettering, secondary door and fuller crowns form a coherent improvement. Its sparse distant context remains unfinished. This checkpoint does not accept all four production stills, motion, the browser payload or the final delivery.

Verified on 7 September 2026. The earlier [v06 verification record](fresh-checkout-verification.md) remains unchanged. This v07 archive predates both the expanded distant-context layer and the font pin introduced by `e8b974909d7521b2ca1c9137c685245732036819`; neither later change is covered by this clean build.

## Source and inputs

The source was extracted with `git archive` into the separate workspace directory `work/fresh-scene-v07-frontage`. It contains **92 tracked files** from tree `5d4567786dc09a5d82f894a7a3654a8dd2b930db`. Recreating that exact source archive for the subsequent audit produced SHA-256 `8867cbac25051a06d3abf614c1be96f6493ec17034415dbd5e2ea1639dc557d9`.

Only the hash-checked material cache was copied into the clean source directory; existing scene binaries and uncommitted generator files were not used. The independent audit verified all **11 default material/HDRI files**, including the optional Spruit environment, against their recorded byte sizes and SHA-256 hashes. The active environment remains Qwantani Sunset Pure Sky. No raw lidar reprocessing or new network acquisition was necessary for this check.

After generation, every archived source file still matches the committed bytes except the expected regenerated `scene/materials.json`. That file has 27 fallback entries instead of the committed 26: it adds `Lower fascia subtle panel joints` and updates the asphalt, mown-grass and prairie-meadow albedos to the current shader values. This is documented output regeneration, not a claim that the old material metadata baseline was unchanged. The four-camera JSON remains byte-identical to the archived source baseline.

The archived generator still loaded the host's system DejaVu Sans font. The later font-pinning change copies those exact bytes into source assets and has separate selection, outline-geometry and packing checks documented in [reproduction](reproduction.md#pinned-font-for-offline-reproduction). This checkpoint alone does not prove that the pre-pin source reproduces typography on an operating system without that font.

## Generation and artifacts

The build used **Blender 4.2.9 LTS**, build `a10f621e649a`. Its log ends with both export receipts, `SCENE_READY 2546` and `Blender quit`. It generated a new editable master, full GLB, browser GLB and metadata, and rendered one **1200 × 800, 32-sample Cycles** aerial probe. The render log records **85.36 seconds including image saving**; no total build-duration figure was captured in the source receipt.

Equivalent commands, with `PROTOLABS_VERIFY` set to the absolute extracted source directory and `PROTOLABS_BLENDER` to the executable, are:

```bash
"$PROTOLABS_BLENDER" --background --python-exit-code 1 \
  --python "$PROTOLABS_VERIFY/scripts/build_scene.py" -- \
  --export --render reference_aerial --width 1200 --samples 32

"$PROTOLABS_BLENDER" --background "$PROTOLABS_VERIFY/scene/protolabs-campus.blend" \
  --threads 1 --python-exit-code 1 \
  --python "$PROTOLABS_VERIFY/scripts/check_geometry.py" -- \
  --root "$PROTOLABS_VERIFY" --output "$PROTOLABS_VERIFY/geometry-check.json"
```

The second command opens the generated master for checking and does not save it. The independent inspection also reopened it with one Blender thread, without generation, rendering, scene repair or saving.

| Regenerated artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `scene/protolabs-campus.blend` | 54,952,984 | `b1d83d71b06d7e57c0d157d29ffe8b8025675aeaffb3211ebb0c42118bb9e2a1` |
| `scene/protolabs-campus.glb` | 45,994,640 | `9d8f85c27bad1b9542b86814059922ee6268d16bdec59b3086953e28ac7c0c2c` |
| `scene/protolabs-campus-viewer.glb` | 42,936,560 | `1684d4cf2ff3c315fcb8d4baaba40772dcc16d6047c0b6283a78f94ba56cfc1d` |
| `scene/viewer-export.json` | 414 | `312500a627f9b249e9b7452bba3f7b5fa7941cf3e2e0937bd2bd2b4532fa8ec4` |
| `scene/cameras.json` | 1,393 | `852823aa47e727b08bdd79a2fbe89161f614a495ec14196eb23bc9cd1dd9ae1a` |
| `scene/materials.json` | 3,907 | `bed9911ee5ae5504e48089ee49a69c543b3664157ce6ed6d46600c4354fc9d8a` |
| `deliverables/reference_aerial.png` | 1,266,372 | `d23cacb588212d4588a26c648f51d03ef7a86d644a0c16f714638109b787560d` |

Both GLBs have valid `glTF` magic, version 2, declared lengths equal to actual byte lengths, and parseable JSON chunks. Each contains **1,984 meshes and 2,512 nodes**. These are the original exports; browser Meshopt packaging, visual parity and navigation were not repeated here. Their hashes identify this run rather than guaranteeing binary determinism across Blender environments.

## Saved-master foliage and placement

The reopened master contains **2,546 objects**. All three `Maple canopy` source meshes retain **10,000 individual leaf cards and 22,988 triangles each**, including 20,000 leaf triangles. No mesh named `browser foliage` is saved. The visible vegetation total is **10,354,092 triangles**, matching the export receipt's full-source count; the temporary reduced export records **4,036,672 triangles**. The master SHA-256 in that receipt agrees with the saved file and remained unchanged after inspection. Browser reduction therefore did not replace the complete source foliage in this master.

The campus-tree report accounts for all 92 aerial traces:

| Placement decision | Count |
| --- | ---: |
| Lidar-supported height | 41 |
| Inferred neighborhood height | 6 |
| Omitted for insufficient height evidence | 32 |
| Omitted to avoid overlap with a north envelope | 13 |

There are exactly **47 instantiated campus trees**. Their actual heights agree with recorded construction heights within **0.000000866 m**, and their lowest vertices agree with recorded scene ground within **0.000000889 m**. All **102 north canopy-envelope objects** remain present. These small errors verify the transforms against their input values; they do not establish surveyed vegetation, exact trunks, species, current growth or precise crown forms. The 2022 lidar/2026 aerial qualifications and inferred-neighbor distinctions remain applicable.

This source still uses the earlier **four distant belts and 300 placements**, with inferred heights, sparse EPQS ground samples and approximate per-belt terrain. Its saved report explicitly identifies that limited layer. The subsequent eight-belt expansion is a different source revision and requires its own fresh check.

## Geometry, camera and finish checks

The archived geometry report passes the source cube winding regression and all three representative closed boxes: main occupied volume, lower logo canopy and dark monument sign. Every box is closed and outward-facing with positive local signed volume. The reported canopy box volume is its unscaled local mesh volume; it is not the fitted assembly's world volume. The distant surround top, z=−12.453000069 m, stays about **0.422 m** below the lowest measured terrain vertex at z=−12.031000137 m. The checker also found no failed campus-height or north-envelope top comparisons. It is a bounded regression check, not a full topology or collision audit.

The fixed aerial camera matches its reference fit within **0.000001077 m position**, **0.0000000305 radians Euler rotation**, and **0.000000701 mm focal length**, consistent with Blender floating-point storage. The master retains **AgX Medium High Contrast, exposure −0.35, gamma 1.05**, the fitted lower fascia, the revised wordmark and the interpreted secondary door. The inspection confirmed these saved-state properties; it did not rewrite them.

The rendered probe was inspected at its full 1200 × 800 size. The corrected lower fascia no longer blankets the brick window run; the identity placement, narrow door and fuller crowns are coherent with the proposed corrections. Its far background still consists of sparse separate belts over an overly flat ground horizon. These observations support the frontage/crown checkpoint and the need for expanded context. They do not establish photographic equivalence, all-camera appearance or a finished landscape.

## Receipts and remaining scope

Workspace evidence is retained in:

- `work/fresh-scene-v07-frontage/fresh-source-receipt.json`: source and generated-output hashes with root inspection status.
- `work/fresh-scene-v07-frontage.log`: generation, render and both export logs.
- `work/fresh-scene-v07-frontage-geometry.json`: passing archived geometry report.
- `work/motion-review/fresh-v07-artifact-validation.json`: independent source, material-cache, GLB and image integrity checks.
- `work/motion-review/fresh-v07-master-inspection.json`: independent read-only master, full foliage, tree-report, camera and finish checks.

The required production set remains **four 1600 × 1067 stills at 64 samples each**, with their master/image-bound JSON receipts in `deliverables/stills/`. The probe above is separate from that set. No complete delivery-resolution motion sample, full film, current viewer packaging/navigation, private publication or final release archive is accepted by this checkpoint. The expanded-context source and newly pinned font must be included in the later final clean build.
