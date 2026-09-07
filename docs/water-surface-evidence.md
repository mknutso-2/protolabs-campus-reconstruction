# Flat pond surface correction

The earlier generator draped both water polygons over the local terrain and added the same offset used for other landscape surfaces. The overview render exposed a raised, folded reflective sheet. `scripts/water_finish.py` replaces only those two water meshes with a horizontal surface clipped to their traced footprints and the existing modeled basin. The surrounding measured terrain is unchanged.

## Level evidence

[The constraints](../research/water-surface-constraints.json) use the already cached northern USGS tile `USGS_LPC_MN_CentralMissRiver_B22_4475_49845.laz`, SHA-256 `772f6ee72e6ba327d653a3a9a10f42e867884f0d748cbc8d1b7f2b54dc699436`. Its source URL and the campaign's 2022-04-25…2022-06-02 dates are recorded there; the individual tile flight date is not established. No new lidar download was needed.

The two water outlines come from the Spring 2026 county-aerial traces in `research/site-layout.json`. The main outline is medium confidence and the narrow southwest inlet is low confidence. Lidar was read in one-million-point chunks and filtered to the outlines' bounding box with a 10 m margin. There are **no class9 water returns** in that bounded selection. Class2 returns inside the main outline provide a useful alternative constraint:

- 106,099 class2 returns have median elevation 292.49 m NAVD88 and interquartile range 292.49–292.55 m.
- A 5 m inward polygon-distance filter leaves 54,115 interior class2 returns. Their most frequent 0.01 m elevation bin is 292.49 m, containing 30,726 points.
- 48,824 interior points, or 90.2%, lie within 0.06 m of that mode. They occupy 1625 one-metre horizontal cells across approximately 197×92 m. Their median is 292.49 m, their 5th–95th percentile interval is 292.48–292.51 m, and a diagnostic plane fit has RMS residual 0.01088 m.

This broad, nearly horizontal low-return population supports **292.49 m NAVD88 as an inferred pond level**, equivalent to scene z = −11.11 m after subtracting 303.6 m. Class2 labels do not certify water; the mode window is not a confidence interval. The level is dated lidar evidence, not a current water survey. Seasonal change between 2022 and the 2026 outline is unresolved. The inlet shares the same level as a connected-water interpretation.

The stored constraints retain both outlines, class counts and elevation percentiles, interior-mode statistics, coordinate systems and method limits. The analysis used NumPy and laspy/lazrs against the exact cached tile. Working scripts and diagnostics are in `work/pond-water/`: `analyze.py`, `derive_level.py`, `point-analysis.json`, `level-analysis.json` and `pond-points.npz`. Scene reproduction consumes only the committed constraints; it does not require those working caches or raw lidar.

## Geometry and integration

Call after the site water polygons and `Measured rolling ground` exist, before saving or exporting:

```python
from water_finish import apply_water_finish

water_report = apply_water_finish(ROOT)
bpy.context.scene['Water surface report'] = json.dumps(water_report)
```

The current builder applies it after monument finishing and before material finishing. The helper first clips the actual rendered terrain triangles to areas at least 0.01 m below the chosen level. It then intersects those pieces with convex triangles from each original water outline. All resulting water vertices are placed at the same world elevation. Thus the water stays inside the aerial trace and cannot climb the modeled bank. The 0.01 m threshold prevents coincident faces; it is not a water-depth claim.

The basin is the existing 5 m rendered ground, including its −0.12 m base offset and interpolated missing-return bins. It is not bathymetry. Approximately 20% of the main aerial outline and 48% of the inlet are excluded where that modeled ground would lie above the fixed surface. This reduction exposes the disagreement between the dated waterline and modeled basin instead of raising or depressing the measured ground to hide it.

Only the two water objects receive new mesh data. Their names, transforms, material references and the surrounding scene remain intact. The module performs no network access, save or export. A repeated invocation is a no-op; a partially applied state is rejected.

## Isolated verification

A water-only study loaded the fresh v07 master with SHA-256 `b1d83d71b06d7e57c0d157d29ffe8b8025675aeaffb3211ebb0c42118bb9e2a1`. The former main water ranged from z = −11.032 to −9.709 m and the inlet from −11.010 to −10.143 m. The corrected surfaces are both flat at −11.11 m.

| Water object | Traced area | Retained flat area | Retained fraction | Triangles |
| --- | ---: | ---: | ---: | ---: |
| pond_open_water | 6042.59 m² | 4844.99 m² | 80.18% | 2850 |
| pond_southwest_inlet | 74.59 m² | 39.10 m² | 52.42% | 43 |

Construction took 0.31 s. All face normals point upward; maximum plane error is 0.000000344 m and the minimum measured face-center clearance above the actual terrain is 0.010118 m. Every protected mesh coordinate hash, original object transform and unrelated data link remained unchanged. Repeated invocation created no meshes. The master file hash stayed unchanged and no master was saved or exported.

The 900×600 overview preview used 20 Cycles CPU samples and three threads, completing in 59.07 s. Inspection confirmed that the raised/folded tip was resolved and the horizontal water reads coherently at that scale. This accepts the bounded geometry correction, with the dated class2-derived level and waterline uncertainty above; it does not establish current hydrology or final material/motion quality.

The working result is `work/pond-water/flat-water-preview.png`, with `preview-report.json`, `preview.py` and `preview.log`. The source constraints SHA-256 used in that check is `c50dde64c62393a1ae1927800f2560fa5f49b54397500ff1c71a11f9c4b2db9f`.
