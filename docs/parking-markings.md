# Entrance parking paint correction

The original entrance-row data gave each single bay a 53.8-pixel depth. At the
recorded aerial scale of 0.148056 m/pixel this becomes 7.965 m. The first opposing
row pair is only 41.7 pixels apart, so its lines overlap by approximately 1.79 m.
Its two interpolated rows consequently read as long closely packed strips in
the reference aerial render. The coordinate conversion itself is consistent;
the coarse single-bay depth/count interpretation is not consistent with the
visible paint boundaries.

[The derived record](../research/entrance-parking-correction.json) preserves the
original layout hash and a separate manual trace of four entrance rows. The
2026 county aerial shows individual depths of approximately 37–41 pixels,
5.48–6.07 m, with shared center lines and hatched, rounded ends. The corrected
rendered bay counts are 5, 6, 9, and 10; original estimates were 6, 7, 10, and 11.
These counts describe the traced geometry, not official parking capacity.
The older official drone photograph independently shows the same paired-row
and hatched-end organization, but source-date differences remain possible.

Manual boundary reading is approximately ±3 pixels, or 0.44 m from annotation
alone. Source georegistration, existing terrain sampling, wear, parked-car
occlusion, and capture dates add uncertainty. Divider interpolation, corner
rounding, 0.10 m paint width, and hatch spacing remain restrained approximations.
Neither accessibility compliance nor an exact parking design is claimed.

The county aerial remains a research image. It is not painted onto the model
or bundled as a material. The existing faded parking-paint material is reused.
Original `site-layout.json` rows and builder inputs are retained for comparison.
Other parking rows, cars, curbs, accessible symbols, and buildings are unchanged.

## Separate access-aisle construction correction

The builder also creates ten `Accessible access aisle hatch` curves at constant
z = 0.05 m, running between roughly y = −10 and −5.3 m. They intersect the existing
`Entry concrete apron`, whose footprint begins at y = −7 m in that part of the
entrance. These are separate from the four aerial-traced rows.

The helper reads the actual current apron mesh footprint, splits those existing
segments at its edges, and retains only their outside portions. The retained
paint stops 0.08 m along each segment before the boundary to keep its full width
off the apron. Its final height follows the actual rendered asphalt, using the
small rendering clearance described below. No new accessible-parking layout is
invented: the remaining hatch is explicitly inferred from the old construction,
and its real-world position still needs a dedicated source review.

## Actual pavement conformance

The first integrated final aerial exposed an additional construction error:
matching paint to the bilinear terrain grid did not match the independently
triangulated asphalt mesh. Some paint lay as much as 47 mm beneath the pavement,
so the shared row divisions disappeared while raised end caps remained visible.

`asphalt_surface_sampler` builds a temporary raycast index from evaluated mesh
faces using the existing `Weathered asphalt / metric noise` material. It samples
the highest downward intersection at each paint coordinate. Final paint vertices
sit 12 mm above that rendered surface. This is a modest rendering separation,
not a claim about physical paint thickness. The old ground + 0.04 m value remains
only as an initial construction scaffold and historical record.

`conform_parking_paint` subdivides the existing triangles in XY to edges no longer
than 0.20 m. It checks edge midpoints, face centers and additional interior points,
subdividing further if sampled clearance drops below 3 mm. The current site has
at least 9 mm clearance in a denser independent audit. This preserves XY coverage,
paint width, shared center lines and the existing apron exclusion. The asphalt,
curb, apron and measured terrain are never edited by this helper.

## Integration

After the original parking and access-hatch curves, the entry apron, and any
entry-apron correction have been created, call this before saving/exporting:

```python
from parking_finish import apply_parking_finish
parking_report = apply_parking_finish(ROOT)
```

The helper matches all 38 legacy curves for the four selected rows by their
world-space endpoints, rather than by unstable numeric name suffixes. It also
requires the ten existing access-aisle curves and actual apron footprint.
Missing or changed prerequisites raise an error before removing old geometry.
It replaces those 48 curves with one asphalt-following paint mesh; all other
scene objects are preserved. A repeated call with the same evidence hash does
nothing. A changed evidence hash requires rebuilding the scene.

The module writes no files and never saves the master. Its returned report can
be retained with integration receipts. Call before the material-quality pass
when practical so that the shared material receives the usual finish.

## Verification

The before/after plan overlays were inspected against the 2026 aerial: shorter
bay divisions, shared center lines, and bounded hatched caps follow visible
paint far more closely. An isolated Blender check opens the clean v07 frontage
master, applies only this helper, validates the exact legacy-curve replacement,
terrain offset, upward paint faces, apron exclusion, repeated-call behavior,
and preservation of unrelated objects and the saved master. It also projects
the old/new paths through the unchanged fitted aerial camera for inspection.

The original grid-based check passed its limited assertions: exactly 38 row
stripes and ten separate access-aisle curves became a 1,660-triangle mesh, with
terrain-offset error below 0.000001 m. The integrated image subsequently showed
that this was insufficient: 834 of 3,320 paint vertices and 1,597 edge/face samples
were below the actual asphalt. The deepest measured penetration was 46.96 mm.

The repaired helper was then checked both on that final master in memory and
through the full replacement API on the clean frontage master. Both produce a
13,228-triangle paint mesh. All 10,072 vertices and 251,332 independently sampled
edge/interior points clear the asphalt; their minimum gaps are 12.00 mm and
8.99 mm respectively. Paint XY area differs by less than 0.000003 m² from float
storage, all faces point upward, and no retained access-paint vertex lies inside
the apron. All unrelated object data/transforms, asphalt mesh coordinates and
saved master files remain unchanged. Repeating the complete helper is a no-op.
A native-scale crop of the 1600-pixel aerial, rendered at 24 samples, was compared
with the integrated still: the previously missing dividers and shared center
lines are continuous, while the original faded paint material remains intact.

The projected overlay has the correct paired-row and capped-end organization,
with visible residual pixel offsets from the reference. The dated plan trace,
terrain and camera were not adjusted to force paint onto photographic pixels.

Local diagnostics are retained in the enclosing workspace's `work/parking-review`
for the original plan/projection review, and `work/parking-surface-review` for the
actual-asphalt correction: `validation.json`, `apply-validation.json` and the
bounded `after-parking-crop.png` render. These checks concern this paint correction;
they do not establish final acceptance of the overall stills or motion.
