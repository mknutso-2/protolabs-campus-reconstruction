# Distant woodland context

`scripts/distant_context.py` adds distant background context from [the reviewed aerial and elevation record](../research/distant-woodland.json). It uses only `wood-01` through `wood-04`, the four eligible belts. `wood-05` remains excluded because its coarse outline mixed residential structures and lawns. The source image shows broad open marsh and a lake between wooded areas; the module does not fill those gaps with trees or use the aerial as a texture.

## Integration

Call the module after the distant ground surround and the three existing vegetation template meshes have been created, and before saving/exporting the master:

```python
from distant_context import add_distant_context

distant_report = add_distant_context(ROOT, collection, tree_assets)
```

`ROOT` is the repository root, `collection` is a Blender collection for the new context objects, and `tree_assets` contains exactly the three original mesh templates. The function uses their actual mesh bounds to scale linked instances. It does not change their mesh data, materials, visibility, or transforms. Existing measured terrain and tree objects remain untouched. It neither saves the master nor writes files; its return value is a serializable placement/provenance report that the caller may retain with a delivery.

The existing `Distant ground surround` object must be a mesh with a material and must lie below each recorded woodland elevation. The added patches reuse that material. A second call is rejected before mutation to prevent duplicate context; regenerate the containing scene when changing this layer.

## Placement and ground support

Tree centers are at least 8 m inside the traced polygons and strictly north of local y = 405 m. Deterministic sampling gives each candidate a crown-dependent spacing between 12 and 16 m. A proportional cap limits the entire layer to at most 300 trees while keeping all four belts represented. Thinning can leave larger gaps. The capacity limit is an implementation choice, not evidence of actual tree density or visual fidelity.

Tree height comes from each belt's inferred range, approximately 10–20 m. Crown width, species, rotation, individual position, and age remain interpretations. The three original full-detail assets are reused through linked mesh data without additional textures or downloaded geometry.

Each belt receives a small triangulated terrain sheet confined to its own polygon. Its interior approaches the belt's one recorded EPQS point elevation. An 8 m margin slopes down to the existing far-ground plane **inside** the trace, so no patch expands into the surrounding marsh or crosses into the existing measured grid south of y = 405 m. This is deliberately limited ground support, not a reconstruction of detailed remote topography. One elevation cannot establish every slope across an entire woodland; the patch shape and its edge transition remain inferred.

Each tree is projected onto the actual generated patch surface before its origin is positioned. The lowest point of the scaled asset touches that surface, avoiding floating roots where triangulation crosses the sloped margin. Canopy height is preserved using actual template bounds.

## Evidence and limitations

The county export is the Spring 2026 Nearmap layer, covering local x = −1000…700 m and y = 250…1200 m. The traced belts have approximately 12–20 m boundary uncertainty. Five bounded USGS EPQS queries supplied representative ground elevations; the four eligible belts return about 293.17–296.51 m. The service reported 1 m source resolution and an acquisition-date attribute of `4/3/2023`. That string is preserved as metadata and is not assumed to be a lidar flight date.

NAVD88 is interpreted from the USGS convention for 3DEP data in the conterminous United States; the individual EPQS responses do not explicitly identify the datum or geoid realization. Their values are interpolated DEM elevations, not surveyed control points. The source record preserves query URLs, raw responses, date/rights notes, and the image hash. Ground and canopy in this layer do not have the same evidential status as the bounded lidar constraints around the headquarters.

The module contains no claim that distant silhouettes are correct in a rendered camera view. The integrated scene still needs inspection for visible ground transitions, woodland gaps, atmospheric depth, and motion stability. No full campus render is part of this module's isolated verification.

## Isolated verification

Blender 4.2.9 created the context using the three original vegetation assets in an isolated scene. The placement overlay was inspected against the county aerial. All instances stayed inside the four reviewed woody interiors; the central marsh and rejected residential candidate remain empty in this layer.

| Belt | Linked tree instances | Terrain triangles |
| --- | ---: | ---: |
| wood-01 | 106 | 10,933 |
| wood-02 | 55 | 10,092 |
| wood-03 | 116 | 10,933 |
| wood-04 | 23 | 6,728 |

Numerical checks confirmed a minimum center-to-edge inset of 8.09 m, minimum pair spacing of 12.01 m, and a maximum root-to-patch contact error below 0.00001 m. The lowest placed tree center is at local y = 466.11 m. These are checks of generated geometry, not real-world measurement accuracy. Terrain faces point upward. Existing objects and template mesh coordinates remained unchanged, every tree shares one of the three original meshes, resampling produced identical positions, and a duplicate invocation failed before adding objects.
