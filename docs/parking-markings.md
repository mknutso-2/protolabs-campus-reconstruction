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
off the apron. It follows the existing bilinear terrain at ground + 0.04 m,
instead of retaining a fixed elevation. No new accessible-parking layout is
invented: the remaining hatch is explicitly inferred from the old construction,
and its real-world position still needs a dedicated source review.

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
It replaces those 48 curves with one terrain-following paint mesh; all other
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

That check passed: exactly 38 row stripes and ten separate access-aisle curves
were replaced by a 1,660-triangle paint mesh. Maximum terrain-offset error was
below 0.000001 m, all paint faces point upward, and no retained access-paint
vertex lies inside the apron. Other objects and the saved master remained
unchanged; the repeated helper call added nothing. The projected overlay has
the correct paired-row and capped-end organization, with visible residual
pixel offsets from the reference. The dated plan trace, terrain and camera
were not adjusted to force its paint to coincide with photographic pixels.

Local diagnostics are retained in the enclosing workspace's `work/parking-review`:
`before-aerial-overlay.png`, `after-aerial-overlay.png`, `projection.json`, and
`validation.json`, with `after-projection-overlay.png` for the camera check.
These overlays and geometry checks do not substitute for
inspection of the integrated final stills or motion.
