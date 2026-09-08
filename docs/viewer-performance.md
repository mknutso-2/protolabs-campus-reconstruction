# Distant browser canopy approximation

The first moving-camera benchmark showed that the corrected-color browser
model remained too expensive to navigate comfortably. On the tested visible
1280 × 680 canvas at pixel ratio 1, the early a663 master produced 53 frames in
8,093.87 ms: 6.55 fps, with median/p95 requestAnimationFrame intervals of
161.3/183.7 ms. The view issued 155 draw calls and 11,714,303 triangles.
A 64-sample Blender render ran concurrently, and the scratch canvas used
preserveDrawingBuffer=true. This is a measured result under that workload,
not an isolated GPU throughput test.

The browser exporter now substitutes existing original closed canopy meshes
only for leaf-card objects named Distant woodland. Each replacement fits its
source mesh's exact local XYZ bounds while retaining the object's transform.
This preserves the assigned oriented footprint and height envelope, inferred
belt layout and ground anchor. The detailed leafy silhouette is approximated
by an opaque crown. No photographs or third-party tree models are introduced.

The editable master, full GLB and rendered stills retain all their original
geometry. Campus and north-side trees keep the existing 30% leaf-card export.
The 61 already-solid distant groups and 347 NLCD groups are unchanged.
Only temporary mesh copies are substituted, and every original mesh link is
restored after the browser export, including when an export raises an error.

## Isolated export and packaging checks

The comparison uses master 7dd2ff5a1253f1153e70c4ba09a1bb7806c3d326b950d91c629635bb5cc43cc0.
It predates the subsequent north-boundary terrain correction and is not a
claim about the final delivered master.

Exactly 1,139 distant leaf-card objects use six shared copies of the existing
1,388-triangle crown meshes. The fit has zero local-bound error in the fixture.
All original object transforms are unchanged; each proxy mesh is closed and
has positive signed volume. The master/full-GLB hashes and original data links
remain unchanged after export, and temporary meshes are removed.

Visible vegetation in the reduced export falls from 9,840,564 to 2,930,804
triangles. These counts describe rendering work, not visual fidelity or a
surveyed tree count. The 182 campus/north/template objects follow the existing
leaf-reduction path, retaining their original branches and leaf alpha masks.

Both baseline and proxy packages use the same corrected mean colors and
lossless FLOAT32 Meshopt pipeline. All five leaf MASK materials remain present,
and the distinct architectural/ground albedos pass their post-optimization
checks. Proxy positions decode exactly; no geometry quantization is introduced.

The optimized baseline is 26,522,252 bytes (25.294 MiB). The proxy package is
25,747,644 bytes (24.555 MiB), 466,756 bytes below a 25 MiB per-asset ceiling.
This is a narrow size margin for this specific package, not a general guarantee
for later geometry changes. Each final package needs its own size/hash check.

The isolated comparison and user-triggered eight-second camera benchmark are
kept in the enclosing workspace's work/viewer-material-review harness.
Export and package receipts are under work/viewer-proxy-review.

The owning agent's same-7dd2 baseline run at 22:38:43.614 UTC produced 52 frames
in 8,010.3 ms (6.49 fps), median/p95 intervals of 162.1/178.0 ms, 158 draw calls
and 12,210,107 triangles at the same 1280 × 680 resolution and pixel ratio 1.
The proxy aerial was inspected: nearby trees and the assigned woodland layout
remain recognizable, while distant opaque crown silhouettes are simpler but
coherent.

The matching reference-aerial proxy run finished at 22:41:11.529 UTC: 143 frames
and intervals over 8,038.97 ms, or 17.79 fps. Minimum/median/p95 intervals were
16.47/56.9/67.8 ms, with 152 draw calls and 5,300,347 triangles. Both runs used
the same 1280 × 680 canvas at pixel ratio 1; the reported renderer was ANGLE on
Mesa Intel HD Graphics 4000 (IVB GT2), OpenGL 4.2. No browser warnings or errors
were reported. Background workload was not independently isolated.

This is an observed improvement of about 2.7 times in mean frame rate on the
tested device, not a 60 fps or cross-device guarantee. The owning agent accepted
the proxy provisionally for integration after the aerial and timing checks;
overview inspection and the final v07c package/runtime check remain separate.
[The structured receipt](../research/viewer-proxy-review.json) retains both
timing results, package hashes, size checks and export-preservation assertions.
