# Bounded distant forest from Annual NLCD

The added layer represents dated classified forest interiors behind the existing campus and eight manually traced woodland belts. It adds347 inferred multi-crown groups as36 merged patch objects (481,636 triangles). It does not identify individual trees, measured canopy heights or precise current forest boundaries. The inspected900px preview adds an irregular thin woodland line across previously bare horizon stretches; substantial open regional ground and gaps remain. The bounded improvement was accepted for integration, not as final photographic fidelity or final still/motion acceptance.

## Source and categorical processing

The [official MRLC data-services page](https://www.mrlc.gov/data-services-page) links the USGS EROS Annual NLCD GeoServer. Its WCS offers native30m EPSG:5070 cells and explicit annual slices through2025. [USGS describes Annual NLCD Collection1.2 and1985–2025 coverage](https://www.usgs.gov/centers/eros/science/annual-national-land-cover-database). The selected2025 annual time parameter is not a flight date or individual imagery acquisition date.

One bounded GetCoverage request returned a310×311 single-band UInt8 GeoTIFF of371,634 bytes, SHA-256 `8cc746e3ef6317320543e7afe77af0540cfb608851395d87fa86be386ce2cc46`. Native bounds `[179235,2444745,188535,2454075]` enclose the campus-local±4500m square. The target is exactly300×300 30m cells in UTM26915, using nearest-neighbor categorical reprojection only. No smoothing, class interpolation or nodata filling was used; all90,000 target pixels are valid. The source response records EPSG:5070, native30m pixels and nodata250. Official WCS metadata lists fees and access constraints as NONE.

[The tracked grid](../research/nlcd_landcover_grid.json) includes all class values, source URL/parameters, product year, raster hash and metadata hash. [The tracked selection](../research/nlcd_context_selection.json) records347 cell indices/coordinates,36 patch identifiers, exclusions, protection rules and input hashes. Both files are required for scene generation; the raw TIFF and geospatial packages are optional research inputs. Grid SHA-256 is `f6d4bfc948c5813a1ce7d9ee18ad248a867d027b015f5865a60de6fb8eedba4e`; selection SHA-256 is `eed4cc179acd5c420c7fddf5a0a72ace5ace960370df4ddad9c0b4e0703e1211`.

The [official legend](https://www.mrlc.gov/data/legends/national-land-cover-database-class-legend-and-description) defines41/42/43 as forest, generally taller than5m and exceeding20% vegetation cover. This is not proof of closed canopy. Class90 permits forest **or shrubland**, so it is excluded; open water, emergent wetlands, developed areas, crops, pasture and every other class are also excluded.

## Conservative selection and geometry

Require every selected pixel and all eight neighbors to be41/42/43, producing a one-cell inward erosion. Exclude the700m radius around the scene origin, both measured terrain rectangles, all eight eligible manual belts with30m buffers, excluded wood-05 and two conservative mixed-pixel exclusion boxes identified on the cached Spring2026 county aerials. Select only the fixed reference camera's approximate101.56–171.38degree horizontal rays and4500m distance. This is a view-relevance boundary, not an occlusion test or all-direction forest reconstruction.

The raw unmodeled forest within those rays contains1671 pixels (1.504km²); the conservative subset contains347 (0.312km²), all class41 in this subset. Independent review confirmed the347 unique cells/36 patches, every selected cell's forest neighbors, and input hashes. The closest whole cell is1171.54m from the campus origin. The minimum center distance from an eligible belt is39.79m, providing at least18.57m separation even for the entire30m cell. Mixed-pixel exclusions remove possible lawn/road conflicts; they contain no final selected pixels. Beyond the cached aerial coverage, dated classification remains the evidence rather than a current crown-by-crown check.

The [scene helper](../scripts/nlcd_context.py) uses a deterministic per-cell seed derived from20250907 and the cell's row/column. It reuses the existing low-cost far-group meshes/materials, applies12–18m inferred height and26–28m inferred maximum width, rotates, and fits the **actual rotated mesh bounds** inside the cell. Every vertex remains at least1m inside its30m square, so all convexly interpolated edges/faces remain inside as well. This does not guarantee absence of clearings smaller than the raster resolution.

The lowest stem centroid raycasts the actual [regional3DEP terrain mesh](distant-context.md), preventing artificial platforms or elevation offsets. Each connected patch combines its groups into one new mesh with the existing three material slots:36 objects and up to108 material groups. Original campus/north vegetation, the eight manual belts, templates, materials and terrain remain unchanged. These merged meshes contain no leaf cards or CampusVeg material names; the browser leaf-card reducer leaves them intact. Group counts must never be described as tree counts.

## Integration and reproduction

Call after `add_distant_context` creates the regional terrain and the three existing far-group templates, inside the trees-enabled branch:

```python
from nlcd_context import add_nlcd_context
scene['NLCD context report'] = json.dumps(add_nlcd_context(ROOT, context_collection))
```

The helper performs no network request, save or export. It rejects duplicate calls before creating objects. It verifies the pinned class grid and manual-belt hashes and independently checks cell coordinates, forest neighbors and belt/radius exclusions at generation time. A normal clean scene build requires only the tracked JSONs and Blender.

Optional data reproduction requires rasterio, NumPy, SciPy and Shapely. From the repository root, an existing reviewed TIFF avoids network entirely:

```sh
python scripts/research/acquire_nlcd_context.py --raster /path/to/nlcd-2025-window.tif --output /tmp/nlcd-reproduced
```

Omit `--raster` to make one bounded public WCS request; the helper limits responses to4MB and requires the reviewed TIFF SHA-256. If the service changes its bytes, acquisition stops for review rather than silently changing evidence. The pinned raster was reprocessed twice to separate output directories; both JSONs reproduced byte-for-byte. No new research dependency or network request is required by the scene builder.

## Isolated validation and visible limits

The900×600,24sample reference preview used the existing master SHA-256 `a6632753e411a1b63d9bef90614a80a259ffd2620021107668b1f8a0ac8c0155`, CPU3threads, unchanged camera/lighting/materials. Generation took3.87s; render53.13s. Scratch preview: `work/nlcd-context/nlcd-context-preview.png`; full placement/check receipt: `work/nlcd-context/preview-report.json`. [The compact validation record](../research/nlcd-context-validation.json) preserves source/output hashes and results.

Validation found347 groups,36 patch objects and481,636 triangles; minimum stored-vertex cell inset1.004150m; maximum height error0.000000944m; root-center terrain error0m. All prior mesh coordinate/topology hashes, object transforms/data links and material values were unchanged. The duplicate-call check rejected a second layer without adding objects. The source master file hash was unchanged after rendering. No main master, main still or viewer payload was overwritten by the preview.

The resulting far groups are small in this camera and visibly improve only part of the missing horizon. The regional terrain remains coarse, the class boundary is30m, and canopy height, species, density and individual positions are inferred. Full clean-build, final still, browser and motion verification must follow integration; this isolated result does not certify those deliverables.
