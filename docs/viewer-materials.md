# Browser material and position preservation

The lightweight walkthrough uses opaque mean-color Lambert surfaces for the
procedural architectural and ground materials. The Blender master and rendered
stills retain their scan textures, glass response and physical lighting. Leaf
textures and their alpha masks remain in the browser model.

## Material diagnosis

The Blender exporter retained the original scan image but omitted the node graph
that normalizes its mean and tints it to the selected albedo. The old viewer then
multiplied that raw image by the recorded mean color and a 1.7 boost. This made
the roof much darker than intended while boosting pale untextured fascia.
For example, the asphalt scan's measured mean linear RGB is approximately
(0.100, 0.080, 0.062); multiplying it directly by the roof target
(0.067, 0.061, 0.061) repeats an unintended darkening. This is a missing
normalization operation, not an already tinted texture being tinted twice.

The old optimizer also deduplicated materials whose exported shader parameters
were identical, even though their unsupported Blender color nodes differed.
The optimized model consequently used the roof material for pavement and a
precast material for some concrete curbs.

[The preprocessing helper](../scripts/prepare_viewer_materials.py) places each
known opaque material's recorded linear albedo into its glTF base-color factor
and removes only its unsupported scan base-color binding before optimization.
All non-material JSON, binary chunks, images and topology remain exact.
Unknown materials and alpha materials are unchanged. Distinct asphalt, roof,
concrete, precast and grass colors are checked after optimization.

The viewer consumes each resulting glTF color once. It retains the earlier
explicit dark-glazing and bark approximations because Lambert cannot reproduce
the master shaders. Ambient/hemisphere/sun intensities are now 0.8/1.0/2.2;
exposure, camera, tone mapping and disabled dynamic shadows are unchanged.
These are restrained preview settings, not a calibrated reproduction of the
reference illumination.

Three.js documents [Lambert materials](https://threejs.org/docs/pages/MeshLambertMaterial.html);
the installed 0.180 shader multiplies diffuse color by the color-map sample.
Blender documents its [recognized glTF material arrangements](https://docs.blender.org/manual/en/4.0/addons/import_export/scene_gltf2.html).
The diagnosis above was checked against the actual exported GLB and installed
loader/shader source rather than inferred only from a screenshot.

## Position precision

The previous optimize command also used default 14-bit position quantization.
The joined regional context spans 9 km, giving about 0.55 m quantization steps,
far larger than pavement, paint and apron clearances. Its POSITION accessors
became SHORT integers with a 4,500 m node scale. The overview displayed jagged
grass/asphalt overlaps that were absent in Blender.

Packaging now runs the same optimization with compression and simplification
disabled, then [compresses the attribute bytes losslessly](../scripts/compress_viewer_lossless.mjs)
using EXT_meshopt_compression without a quantize transform. The installed CLI
implementation was inspected to verify that compression=false adds no implicit
quantization. All 164 POSITION accessors in the diagnostic package remain
FLOAT32 and exactly match their decoded pre-compression arrays.

An independent world-coordinate comparison also covers asphalt, concrete,
roof, both grass materials and paint, including GPU instance transforms.
Every source/optimized surface vertex has a matching coordinate within
0.000007 m in both directions; the maximum is a roof transform rounding
difference. Asphalt, concrete, grass and paint coordinates match exactly.
The package is larger, about 20 MB, to preserve this required precision.

## Bounded verification

[The diagnostic receipt](../research/viewer-material-review.json) identifies the
early v07 master, source/prepared/optimized hashes and exact checks. It does not
identify the subsequent final geometry build. Each package run writes a new
scene/viewer-package.json with its current master and asset hashes.

On 7 September 2026 at 22:06–22:07 UTC, the owning agent inspected the isolated
localhost:3107 comparison in a separate browser tab: After aerial, then Before
and After overview. Large jagged ground patches disappeared, roofs were gray
and distinct from asphalt, concrete was lighter, and foliage retained its alpha
cutouts. The browser reported no warnings or errors. The observations remain in
the task's browser tool output; no saved screenshot file is claimed.

The plain-color walkthrough retains a dark pond, simplified glass without
physical reflections and some distant thin-edge aliasing. It is intended for
geometry navigation alongside the textured still views. This bounded check
does not accept the final stills, movie, refreshed Site assets or deployment.
Python compilation, viewer lint and TypeScript checking passed for this change.
