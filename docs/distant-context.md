# Distant woodland context

`scripts/distant_context.py` adds eight woodland interiors from [the attributed aerial and elevation record](../research/distant-woodland.json). The source images show large open marsh, creek channels, a lake and residential clearings between wooded areas. Those openings remain outside the woodland layer. The imagery is used for tracing and review, never as a scene texture or composited backdrop.

The first four-belt version put 300 separated trees only north of local y = 405 m. Its geometry checks passed, but the integrated reference image showed small isolated groups and a largely empty horizon. That image check motivated this revision. The actual camera rays also reach wooded ground west of the measured grids, so a blanket northern cutoff was geographically inappropriate.

## Evidence and coverage

The original Spring 2026 county image covers local x = −1000…700 m and y = 250…1200 m. Two bounded additional exports cover x = −1500…600 m / y = −100…1500 m at 0.667 m per output pixel, and x = −3500…−1200 m / y = −300…1100 m at 1 m per output pixel. The manifest records the [Hennepin County aerial service](https://gis.hennepin.us/arcgis/rest/services/Imagery/UTM_Aerial_2026/MapServer), exact request URLs and returned extents, acquisition timestamps, image byte counts and SHA-256 hashes. Public availability does not establish a texture or redistribution license.

| Belt | Evidence-supported area | Treatment |
| --- | --- | --- |
| wood-01 | Northwest woods south of the curved road | Original eligible trace |
| wood-02 | Western woods between residential clearings | Original eligible trace |
| wood-03 | Northern creek island | Original eligible trace |
| wood-04 | Northeast creek belt | Original eligible trace |
| wood-05 | Coarse mixed residential outline | **Excluded**, retaining its original rejection |
| wood-06 | Wooded marsh edge west of the adjoining industrial building | Added trace; three EPQS ground samples |
| wood-07 | Woody strip below western residential clearings | Added trace; one EPQS sample |
| wood-08 | Western woodland interior west of residential yards | Added trace; one EPQS sample; unresolved canopy groups |
| wood-09 | Far-west creek's wooded east bank outside an estate lawn | Added, tightened trace; one EPQS sample; unresolved canopy groups |

The added polygons record their manually annotated pixel boundaries and annotation-image dimensions. Their horizontal boundary uncertainty is approximately 12 m for the nearer image and 20 m for the western image. Independent visual review found no obvious house inclusion in wood-06/07/08, noted a reed fringe on wood-08's western edge, and recommended tightening wood-09 away from the creek. The final polygon implements that tightening and retains a conservative crown inset. This review establishes neither species nor canopy height.

Six new queries to [USGS EPQS](https://apps.nationalmap.gov/epqs/) supplement the five original recorded queries. The added DEM elevations range from 288.151855469 m at the far-west bank to 293.690124512 m at the residential-edge strip. Scene z subtracts the existing 303.6 m reference elevation. Responses report 1 m source resolution and the acquisition-date string `4/3/2023`; that string is preserved without assuming it is a lidar flight date. NAVD88 follows the USGS CONUS convention, while the individual response does not explicitly identify the datum/geoid. These are interpolated DEM samples, not surveyed controls.

The fixed reference camera's horizontal rays span approximately 101.56°–171.38° in the local XY plane. Its far-left ray crosses real marsh before reaching woodland roughly 3.4 km away. A 4500 m camera clipping distance admits that supported distant context. A continuous regional DEM surface now extends to ±4500 m. The approximate underlay stays below its minimum, at the minimum of the measured and regional grids minus 0.5m (approximately z = −24.58m). Distant homes and roads remain incomplete, while the 50m DEM resolves broad intervening relief rather than individual banks or berms. The finite 9km domain remains an approximation of the full visible region.

## Integration and placement

Call after the distant ground surround and the three original vegetation mesh templates exist, before saving or exporting:

```python
from distant_context import add_distant_context

distant_report = add_distant_context(ROOT, collection, tree_assets)
```

`ROOT` is the repository root, `collection` receives the new context objects, and `tree_assets` contains exactly the three original mesh templates. The function writes no files and returns a serializable provenance and placement report. A second invocation raises before mutation. The caller must create a material-bearing `Distant ground surround` below the regional DEM minimum (z = −24.0798 m in the recorded grid). The module uses that material without changing it; the caller also controls the camera clipping distance and surround extent.

The actual measured grid rectangles remain protected: main x = −180…240 m / y = −170…220 m, and north x = −170…230 m / y = 60…405 m. All eight traces are disjoint from both rectangles. Existing campus trees, the 102 northern lidar candidates, original templates, their materials and measured terrain are unchanged.

Deterministic dart sampling uses seed 554017 and overlapping inferred crowns. Ordinary nominal crowns are 7–12 m wide with center spacing 0.66 times crown width. Remote canopy groups span 22–32 m with spacing 0.63 times group width. Candidate centers must clear a 6–8 m minimum polygon inset and half the nominal crown plus 2 m. A further actual-mesh-radius check keeps the entire rotated crown at least 2 m inside the traced boundary. A proportional instance budget retains the initial evenly distributed dart samples in each belt and caps the layer at 1200 objects. The budget and density are presentation choices, not a tree inventory.

All canopy heights remain inferred belt ranges, approximately 10–20 m. Individual positions, species, crown widths, age and rotation are interpretations. Distances controlling representation are fixed distances from the reference camera, so geometry does not switch or pop during navigation or animation:

- At 700 m or closer, context instances share the original full vegetation meshes.
- Beyond 700 m, separate 2000-card meshes retain all woody faces, UVs and source mesh extrema. Card selection is deterministic and stratified across 3D spatial bins. Original templates and all near-campus foliage stay intact.
- Beyond 2000 m, wood-08/09 use three compact meshes of overlapping irregular crown lobes. Each represents an unresolved group of crowns, not a giant measured tree. Their matte foliage colors and silhouette are artistic approximations within the supported land cover.

The context card meshes retain `CampusVeg_` materials, while their `context_leaf_cards` mesh marker tells the viewer exporter to preserve the already reduced 2000-card geometry. Unmarked full meshes still use the normal 30% browser reduction. Remote canopy-group materials use a separate prefix, so the exporter does not mistake solid crown faces for individual leaf cards. The export receipt records preserved context LOD instances. The same master bounds define requested height and nominal crown width for every representation, and meshes are linked across instances. A no-render Blender check confirmed exact source bounds, 2000 retained cards per context mesh, deterministic repeated meshes/sampling, and unchanged original 10000-card assets. Applying the old extra 30% pass in that test produced 615 cards/4218 triangles; that overly sparse double reduction is now deliberately skipped.

`add_distant_context` invokes `regional_ground.add_regional_context_ground` automatically. The helper creates one continuous surface from [the committed regional grid](../research/regional_context_ground_grid.json), with holes exactly matching the existing main ground rectangle and the rendered north extension above y =220m. It does not create separate woodland platforms. A 75m transition outside those holes blends the difference between the coarse DEM and actual measured boundary elevations; the measured meshes themselves remain unchanged. Boundary raycasts use a 1mm inward fallback only if float precision misses an edge. Extra vertices along these seams interpolate the 50m data and do not imply higher source resolution.

Trees and canopy groups are raycast onto the actual continuous terrain triangles, placing the lowest asset vertex on that surface. Sparse EPQS point responses remain in the woodland manifest as cross-checks, but no longer flatten each whole belt to one elevation. The 50m grid differs from those points by approximately −0.568…+3.847m, with the largest discrepancy at the narrow northeast creek belt; coarse resampling does not resolve every bank. Neither this DEM nor the original wetland fill is bathymetry.

## Regional DEM provenance and reproduction

The [official USGS 3DEP bare-earth ImageServer](https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer?f=pjson) supplies one F32 band. One bounded `exportImage` request used `rasterFunction=None`, TIFF/F32, bilinear resampling, EPSG:26915 and 181×181 pixels. Its 9050m pixel-edge extent puts sample centers exactly at local −4500…4500m in 50m steps. All 32761 values are finite and valid. The downloaded 263355-byte TIFF has SHA-256 `45ca8bd77a0456db03de55dc9a785d0325d7572a7dbf8eae64df4e2195045fa0`; the full request, returned extent, service metadata hash and acquisition timestamp are embedded in the grid JSON.

Raw elevations range 279.520233…324.559052m. Scene values subtract 303.6m and are rounded to 0.0001m, yielding −24.0798…20.9591m. North-first TIFF rows are reversed so both JSON axes increase. TIFF georeferencing, float type, dimensions and no-data absence were checked. The service describes the published mosaic as current through August 24, 2026; that is not a terrain acquisition date. Individual contributing raster dates and vertical-datum realizations are not returned by this export. NAVD88 follows the USGS CONUS convention and remains explicitly qualified.

Normal scene reproduction reads the tracked JSON and needs no network or raster library. To reacquire the bounded source, use Python with Pillow:

```sh
python3 scripts/research/acquire_regional_ground.py
```

The acquisition helper bounds response sizes, verifies TIFF mode/dimensions/georeferencing, records hashes, rejects invalid elevations and rewrites only this derived grid. An upstream mosaic update may change a later acquisition; the stored source hash identifies the version used here. The working cache can be checked without network with `--from-cache /absolute/path/to/work/regional-ground`.


## Verification record

The historical four-belt fixture produced 300 trees (106/55/116/23 in wood-01…04), a minimum 8.09 m center inset, minimum 12.01 m pair spacing and root-to-patch error below 0.00001 m. Original meshes and objects remained unchanged. That numerical pass did not predict a convincing image; the later integrated image exposed the sparse coverage described above.

The intermediate eight-belt platform version was generated on the fresh v07 frontage master with SHA-256 `b1d83d71b06d7e57c0d157d29ffe8b8025675aeaffb3211ebb0c42118bb9e2a1`. The isolated study replaced only 304 former tagged context objects, enlarged/lowered only the approximate surround, and changed camera clipping from 1500 to 4500 m without changing the camera transform. Generation took 7.79 seconds. A 900×600 Cycles CPU preview at 24 samples and three threads took 53.89 seconds. The master was neither regenerated nor saved and its file hash remained unchanged.

| Belt | Tree instances | Unresolved canopy groups | Terrain triangles |
| --- | ---: | ---: | ---: |
| wood-01 | 274 | 0 | 10,933 |
| wood-02 | 157 | 0 | 10,092 |
| wood-03 | 296 | 0 | 10,933 |
| wood-04 | 67 | 0 | 6,728 |
| wood-06 | 176 | 0 | 11,774 |
| wood-07 | 169 | 0 | 11,774 |
| wood-08 | 0 | 39 | 5,887 |
| wood-09 | 0 | 22 | 5,760 |
| **Total** | **1139** | **61** | **73,881** |

Of the 1139 trees, 270 share full 22,988-triangle meshes and 869 share separate 6988-triangle/2000-card meshes. Each remote canopy-group mesh has 1388 triangles. Height ranges in this deterministic run span 10.163–20.000 m; these are inferred heights. Every actual crown radius clears its traced boundary by at least 2.017 m. The maximum generated height error is 0.000000940 m and the maximum root-to-sheet contact error is 0.000000479 m. All existing object transforms, visibility and mesh links stayed unchanged. Coordinate hashes of every protected mesh, including original templates and measured terrain, matched before and after. A duplicate invocation failed without adding objects. These checks establish implementation behavior, not measurement accuracy.

That intermediate image visibly improved the formerly empty near-west background and replaced separated distant crowns with overlapping belts. Independent image review also confirmed the added near-west depth and preserved open gaps, while noting shelf-like bases and level silhouettes in several distant belts. Its view still has a conspicuously flat regional ground line and incomplete intervening residential/topographic context. Some gaps are real open marsh; others reflect the bounded coverage of this reconstruction. The remote meshes are only a low-frequency approximation, and motion stability has not been checked. This is useful visual progress, **not final photographic acceptance**.

The intermediate platform artifacts are preserved in `work/distant-refinement/plateau-history/`. Other local study artifacts include the two `*-trace-review.jpg` aerial overlays and `preview.py`. They are working verification artifacts outside the delivery repository. The recorded county export requests and committed polygon/elevation data are sufficient to regenerate this layer without relying on the cached images; no imagery download is required during scene construction.

## Continuous-terrain verification

The regional version completed the same isolated 900×600 reference-camera check on the unchanged fresh v07 master identified above. Context construction took 14.43s and the 24-sample/three-thread Cycles render took 112.78s. The surface has 64216 vertices and 126952 triangles, with no faces inside either measured-domain hole. There are 755 exterior transition vertices, with a maximum 3.121m correction relative to the coarse DEM near a measured boundary. The transition does not move measured vertices; its construction-level boundary-height match is within floating-point precision (a 1mm inward sampling fallback was available on a BVH edge).

The layer still has 270 full trees, 869 separate 2000-card trees and 61 remote canopy groups. All crowns retain at least 2.017m boundary clearance. Maximum generated height/root-contact errors remain below 0.000001m. Original object transforms, visibility, data links and protected mesh coordinate hashes all match the source master. A repeated call is rejected before duplicate geometry. The source file hash remains `b1d83d71b06d7e57c0d157d29ffe8b8025675aeaffb3211ebb0c42118bb9e2a1`; no master save or export occurred.

The regional image removes the separate platform edges and carries broad relief across the open ground between woods. It still depicts a sparse, simplified regional landscape: distant homes, roads, finer bank profiles and complete woodland coverage remain unresolved. This bounded terrain correction is ready for integration; it is **not final photographic acceptance** or a motion-quality check.

The latest working image is `work/distant-refinement/regional-context-preview.png`, with `regional-preview-report.json` and `regional-preview.log`. The source cache and acquisition receipt are in `work/regional-ground/`. The original plateau image/report remain in `work/distant-refinement/plateau-history/` so their visual failure is reviewable. The committed regional JSON SHA-256 is `c13d7099da22662f5879229656bbc4c0397523eca05bc04eff1e81d2c7a28874`.
