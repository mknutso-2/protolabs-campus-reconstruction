# Campus tree-height evidence

The 92 visually traced campus tree centers previously received generic 12–14 m assets with random scale factors. The resulting trees could exceed 18 m. Local analysis of the two cached 2022 USGS lidar tiles supports substantially lower envelopes for several prominent foreground trees. This is an evidence correction, not a fit of tree height to the photograph.

[The keyed constraints](../research/campus-tree-constraints.json) contain every original tree-array index, tree ID, pixel center and local coordinate. **53 of 92 traces are eligible** for a local height constraint; 40 have higher relative confidence. The remaining traces retain null recommended heights and explicit reasons, rather than receiving a fabricated measurement. Eligibility means adequate local evidence for a canopy envelope, not a surveyed trunk, verified species, or 2026 tree inventory.

## Foreground findings

The current-model values below were read without modification from the early v07 master, SHA-256 `d9df348a833ca58acf88706daffe429203f9ee8fa8cc1c66187476d220f03c0c`. Model height is actual transformed mesh bottom-to-top height. Lidar height is the conservative local canopy-envelope estimate above a class-2 ground plane.

| Original index / ID | Local x, y (m) | Model height (m) | Lidar envelope height (m) | Relative confidence |
|---|---|---:|---:|---|
| 9 / tree_010 | −23.330, −25.733 | 11.284 | 8.562 | Higher |
| 10 / tree_011 | −5.593, −25.999 | 13.887 | 8.537 | Higher |
| 12 / tree_013 | 36.337, −26.251 | 13.683 | 8.613 | Higher |
| 14 / tree_015 | 70.804, −26.251 | 18.354 | 9.406 | Medium; offset support |
| 85 / tree_086 | 45.339, −58.897 | 14.732 | 6.992 | Higher |

Tree_015 is the conspicuous foreground-left tree in the fitted aerial. Its original mesh top is local z=17.693 m, whereas the supported canopy top is z=8.964 m. Its original center/top projects near y=260 pixels in the 1200 × 800 reference camera, explaining why it intrudes into the sun/sky region. That projected point describes the modeled vertical centerline top, not the entire crown silhouette. The photograph was used to identify the visible discrepancy; the replacement height came from lidar independently.

Tree_015 has 368 accepted elevated returns in 11 connected one-metre cells, no nearby class-6 building returns and no roof-plan exclusion. Its closest supported cell is 2.915 m from the approximate trace center, so confidence remains medium. A separate wider 8 m diagnostic finds a 40-cell crown component with a 9.451 m p95 envelope, consistent with the primary estimate. This does not establish the exact trunk position or width.

Tree_012/index 11 and tree_014/index 13 are **ineligible** at their traced centers: only six and 44 elevated returns respectively survive the height filter, without sufficient connected canopy. An 8 m diagnostic finds neighboring crown components roughly 5–6 m east. These may reflect trace displacement, different trees or change between 2022 and 2026; the derivation does not automatically reassign those neighboring heights to the exact traced centers. The later scene-only neighborhood estimates are listed below and leave both original recommended heights null. Tree_084/index 83 has no supported elevated returns within its primary or wider diagnostic circle. Absence of returns does not prove absence of a 2026 tree.

Across the 41 eligible constraints that match currently instantiated aerial-traced scene trees, the median model-to-lidar height ratio is 1.774, and 32 exceed 1.25. This selected comparison supports an oversizing problem; it is not a growth-rate estimate or an error statistic for every campus tree. North-context instances are separate and already use their own envelope constraints.

## Source and method

No new lidar was downloaded. Both source files, byte counts, exact SHA-256 hashes, bounds, dates and URLs are recorded in the constraint JSON and [source acquisition manifest](../scripts/research/sources.json):

- `USGS_LPC_MN_CentralMissRiver_B22_4475_49845.laz`, 74,129,464 bytes.
- `USGS_LPC_MN_CentralMissRiver_B22_4475_49840.laz`, 100,131,419 bytes.

Attribution: USGS 3DEP, Woolpert, NV5 and Minnesota Geospatial Information Office. The project collection interval is 25 April–2 June 2022; individual flight dates are not established. Publication was 14 September 2023. The centers and approximate crown radii come from the cached Hennepin County/Nearmap Spring 2026 aerial and its existing visual trace, typically uncertain by 2–5 m. Lidar NAD83(2011)/UTM15N coordinates are numerically aligned to the aerial's NAD83/UTM15N frame, retaining possible submeter datum uncertainty. Local z is NAVD88 GEOID18 metres minus 303.6 m.

The derivation verifies both cached LAZ hashes and reads them in one-million-point chunks. It retains 1,065,122 class-1, class-2 or class-6 points within 8 m of the existing traces. It then:

1. Fits a local ground plane to all class-2 returns within 4 m, with one robust MAD outlier pass. At least 20 points, RMS residual ≤0.4 m and slope ≤0.7 are required.
2. Queries class-1 returns within the traced crown radius plus 1.5 m, bounded to 3–6 m. Heights outside 2–30 m above the local plane are excluded.
3. Removes points inside cached building polygons with a 1 m buffer. Class-6 roof returns are counted separately and never used as canopy. The masks are approximate and can remove legitimate overhanging foliage.
4. Computes p95 height in one-metre cells containing at least three returns, requiring connected support of at least six cells. Nearly flat envelopes, poorly centered support, building-overlap traces or incomplete tile coverage are ineligible.
5. Uses p95 of the accepted cell envelopes as the height constraint. It records ground, top elevation, support counts and p95/p99 diagnostics independently.

LAS class 1 is **unclassified**, not certified vegetation. Broad support, local height variation and roof masks reduce pole/lamp/roof contamination but cannot guarantee object identity. The 2022 leaf-off/partial-leaf acquisition can miss twigs or canopy tops. Occlusion, trace displacement, neighboring crowns and the four-year time gap limit interpretation. No arbitrary 2026 growth allowance is added.

`observed_connected_envelope_diameter_m` describes the portion sampled inside the query circle. It can be clipped by that circle or split between neighboring crowns and **must not be used as a measured full crown diameter**. Retain a separately documented inferred or aerial-traced width when applying height constraints.

## Reproduction and integration

[derive_campus_trees.py](../scripts/research/derive_campus_trees.py) uses the pinned research environment. After the normal bounded source acquisition, run from the repository root:

```bash
.venv-research/bin/python scripts/research/derive_campus_trees.py \
  --tile-dir data/research/raw \
  --osm-buildings data/research/raw/osm_buildings.json \
  --output research/campus-tree-constraints.json
```

The optional `--cache` writes a disposable near-trace point cache; it is not a scene dependency and should remain outside Git. Changing the dynamic OSM response can change a regenerated roof mask; the delivered JSON records the exact mask-input hash used for this analysis. The delivered constraint file itself is a small source-controlled scene input.

Use the original `tree_array_index` **before** filtering overlaps with north-context candidates, and confirm the row's tree ID and pixel center against the layout. The integrated `scripts/campus_trees.py` scales the actual mesh bottom-to-top extent to `canopy_height_m`. It places the bottom at the generator's nominal five-metre `ground(x,y)` interpolation, preserving the supported height. Each object stores source and scene ground values; the report additionally stores their difference. For eligible rows this difference shifts the supported absolute canopy top, apart from independent source rounding. An inferred fallback has no measured top to shift, so its ground adjustment must not be described as an error against a measured canopy top. It does not claim that the adjusted absolute top is a millimetre-accurate lidar match. Keep horizontal scale separate; do not use one isotropic random multiplier to undo the constrained height. Preserve the existing deduplication against north-context canopy envelopes. Ineligible rows must remain explicitly inferred or be omitted after a separate visual decision; their null heights are not zero-height measurements.

Workspace diagnostics include `work/motion-review/campus-tree-current-vs-lidar.json`, `foreground-tree-radius8-diagnostic.json`, the local point cache and derivation log. No building, roof, camera, existing vegetation source file or master scene was edited by this research task.

For ineligible but clearly visible 2026 trees, a neighboring-height median can be an explicitly **inferred neighborhood estimate**. A reasonable confidence gate is at least two eligible neighbors within about 30 m in the same planting strip/setting, at least one higher-confidence neighbor, comparable ground elevations (within about 2 m), and a neighbor height range no larger than 4 m. Prefer higher-confidence rows and avoid building-margin cases. These distance/spread limits are reconstruction decisions, not biological growth laws. If the gate fails, or the aerial feature could be a shadow or pole, omit the uncertain instance or leave it for review instead of assigning the former random tall asset. Do not store a fallback in the measured constraint fields. Tree_012 and tree_014 have additional nearby ~8.6 m envelope evidence in the wider diagnostic, which supports a local ~8.5–9 m interpretation without measuring those exact centers.

The applied neighborhood fallback additionally requires a trace to be at least 8 m from the cached building plan and neighbors to lie within 8 m in at least one horizontal axis, as a conservative proxy for the same planting strip. Two higher-confidence neighbors are preferred when available. Instances failing the gate are omitted explicitly; the keyed source constraints are unchanged. The exact per-instance decision, neighbor IDs, dimensions and ground adjustments are saved in the Blender scene’s `Campus tree report` property. The geometry check validates modeled heights and contact with the recorded nominal ground value. It does not ray-cast the rendered surface meshes.


## Independently checked integration counts

A Blender 4.2.9 fixture invoked the actual `add_campus_trees()` helper with the committed inputs and the generator's own extracted `ground()` and `pixel()` functions. It used three tiny source meshes with different heights and nonzero local bottoms, so incorrect bottom offsets or indexing would be visible numerically. No full campus was generated, rendered or saved.

| Decision across all 92 original rows | Count | Meaning |
|---|---:|---|
| Lidar-supported height instantiated | 41 | Eligible local envelope; rendered crown form and aerial width remain inferred |
| Neighborhood height instantiated | 6 | Explicit inference from eligible neighboring constraints; source height/top remain null |
| Omitted for north-envelope overlap | 13 | 12 eligible and 1 ineligible trace within the existing 6 m overlap rule; separate north instances provide that context |
| Omitted for insufficient height evidence | 32 | Ineligible rows failing the neighborhood gate; omission is a reconstruction decision, not proof of an absent 2026 tree |

The result is **47 campus tree instances**, separate from the 102 eligible northern envelopes. The helper preserves all **92 original array indices, IDs and pixel centers** in its report before filtering. Asset choice uses the original index modulo three, not the compacted placement index. Source layout and constraint hashes remained unchanged. The two rows with null ground, tree_063/index 62 and tree_076/index 75, were omitted instead of receiving invented ground or height values.

The six actual inferred heights are:

| Original index / ID | Inferred height (m) | Eligible neighbor IDs used |
|---|---:|---|
| 11 / tree_012 | 8.575 | tree_011, tree_013 |
| 13 / tree_014 | 9.0095 | tree_013, tree_015 |
| 44 / tree_045 | 13.650 | tree_047, tree_050 |
| 45 / tree_046 | 13.937 | tree_048, tree_050 |
| 51 / tree_052 | 13.805 | tree_049, tree_050 |
| 52 / tree_053 | 14.045 | tree_047, tree_048 |

Each value is the median of the named source constraints, not a new lidar measurement at the ineligible center. The eligible source-neighbor pool includes rows whose campus instance was omitted for north overlap; their measured-envelope evidence remains usable independently of which scene collection represents them. Two higher-confidence neighbors were used for tree_012 and tree_053; the other four use one higher-confidence and one medium-confidence neighbor. All original ineligible `canopy_height_m` and `top_z` fields remain null.

The instantiated supported heights span **3.261–17.127 m**. Their nominal scene-ground adjustments span **−0.202–+0.227 m**, and the absolute modeled top shifts by the same amount within source rounding and float storage. The inferred rows' ground adjustments span −0.143–+0.037 m, without implying measured tops. In the deliberately offset mesh fixture, maximum height error was **0.0000021 m** and maximum bottom error against the nominal callback was **0.00000091 m**. These small arithmetic errors establish correct scaling/contact with the callback; they do not reduce the source's metre-scale crown-position uncertainty.

Actual surface contact remains a visual check. The generator builds the base terrain's vertices at the grid elevation **minus 0.12 m**, while some grass/rock overlays use `ground()+0.11 m`; triangulation can add interpolation differences. A tree base at nominal ground can therefore sit slightly above the bare base mesh or inside an overlay. The fixture and geometry checker do not establish intersection with every rendered surface. This distinction replaces an earlier unqualified claim of rendered-ground contact; no placement or generator change was made during this review.

The tested module SHA-256 is `150e9457e605f5ce41e3548c74bdc0602de15b6eb7330a4e02ed42421475ba44`; its keyed constraint SHA-256 is `0241c43e6a586b1943ed074dc21a83beb9c7376334f4686dbb640bae092642ac`. The fixture, complete decision report and validation receipt are retained under `work/campus-tree-review/` in the build workspace. The helper is intended to run once during fresh generation; repeated-call idempotence is not claimed. The revised full scene, tree silhouettes, omitted visible planting, surface contact and motion still require integrated inspection.
