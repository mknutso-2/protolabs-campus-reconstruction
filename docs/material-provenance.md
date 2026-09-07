# Material and low-sun lighting proposal

This upgrade replaces generic surface noise with small CC0 photographic scans, reduces synthetic blue and metallic responses, and provides a low-sun HDRI environment. It changes shader response only. The scans are material proxies from other locations; they are not samples measured at Protolabs. Integrated still-image inspection remains the acceptance step.

## Sources, rights and download bounds

All acquired files come from Poly Haven's official `api.polyhaven.com` manifests and `dl.polyhaven.org` asset downloads. Poly Haven releases its asset files under [CC0](https://polyhaven.com/license). The source scans and HDRIs may be packed into the editable Blender master and redistributed with it. The separate official Protolabs/company photographs used for comparison do not acquire a CC0 license through this upgrade.

[research/material-assets.json](../research/material-assets.json) records every exact file URL, source page, author, resolution, byte size, SHA256, official MD5 and selection status. Downloads were verified against the API's byte counts and MD5, and the reproduction command enforces the recorded SHA256. No file exceeded 7 MB; the acquisition code imposes a 15 MB per-file maximum. All seven researched assets, including rejected lighting candidates, total 24,851,119 bytes. The default acquisition excludes the two rejected candidates and fetches 16,298,653 bytes, including the optional alternate HDRI.

| Asset | Author(s) | Acquired files | Use |
|---|---|---|---|
| [Asphalt 01](https://polyhaven.com/a/asphalt_01) | Charlotte Baglioni; Dario Barresi | 1K diffuse, roughness and displacement JPG | Dry pavement, with an approximately 2.1 m scan repeat; reduced-scale surface proxy on aggregate roof |
| [Leafy Grass](https://polyhaven.com/a/leafy_grass) | Charlotte Baglioni | 1K diffuse, roughness and displacement JPG | Ground-level grass/leaf detail, approximately 2 m repeat, recolored toward the reference; not a measured lawn species or maintenance state |
| [Rough Concrete](https://polyhaven.com/a/rough_concrete) | Dimitrios Savva | 1K diffuse, roughness and displacement JPG | Fine pitting on tinted precast and concrete walks, approximately 1.23 m repeat; no brick courses or invented panel joints |
| [Qwantani Sunset (Pure Sky)](https://polyhaven.com/a/qwantani_sunset_puresky) | Greg Zaal; Jarod Guest | 2K HDR | Default illumination, reflections and sky; no land backdrop |
| [Spruit Sunrise](https://polyhaven.com/a/spruit_sunrise) | Greg Zaal | 2K HDR | Optional unregistered field/tree-horizon environment |
| [Lilienstein](https://polyhaven.com/a/lilienstein) | Andreas Mischok | 2K HDR | Rejected as default: sun too high and distinctive rock mountain inappropriate for this reconstruction |
| [Evening Field](https://polyhaven.com/a/evening_field) | Sergej Majboroda | 1K HDR | Rejected as default: leaf-off landscape and diffuse glow differ from the leaf-on direct-sun reference |

The raw file directory `research/material-assets/` is excluded by the repository's root `.gitignore`. Commit the manifest, this document and the material script; restore raw files by acquisition. Rejected candidates remain available locally for the research audit and can be restored with `--include-candidates`.

## What the module changes

[scripts/material_quality.py](../scripts/material_quality.py) upgrades eight existing surface materials with world-coordinate scan projection, so they do not require new UVs or alter mesh topology. Diffuse images are loaded as sRGB, while roughness and height images are non-color data. The source diffuse scan's mean is normalized in linear light to a recorded target albedo while retaining its local photographic variation. A restrained broad variation breaks up uniform large patches. Fine surface relief uses bump only; no displacement changes silhouettes, curbs or terrain.

The three warm facade materials use tinted fine concrete relief. They remain precast, without a brick pattern. The roof aggregate borrows the asphalt scan's grain as a surface-detail proxy, which is an approximation rather than a claim about the installed roofing product. The grass scan contains flattened blades, leaves and twigs; recoloring and tiling do not turn it into an exact representation of the site's lawn.

Coated pale aluminum and painted structural steel receive restrained dielectric finishes. Mullions become pale silver/blue-gray, with much less saturation. The first v07 probe used glazing transmission 0.70 and read as opaque gray panels. The revised thin-pane response uses neutral cool sRGB `(0.90, 0.95, 0.975)`, IOR 1.52, roughness 0.045 and transmission 1.0. A restrained dielectric coat (weight 0.65, IOR 1.7, roughness 0.035) increases reflections without metallic blue. The unmeasured interior depth remains neutral and dark; neither the glass coating nor interior is an accurate product specification. Pale fascia and mullion values were lifted after the same probe. Their sRGB targets are `(0.82, 0.845, 0.845)` and `(0.62, 0.70, 0.735)`, with metallic weights 0.05 and 0.35 respectively. The photo-interpreted cyan identity color uses sRGB `(0.015, 0.48, 0.65)`, metallic weight 0 and no emission. All these display-referred color inputs are converted to linear light in the shader helper.

Existing parking-paint geometry receives warm off-white color, high roughness, and soft patchy transparency so local wear reveals the pavement beneath it. This introduces no parking spaces, markings, layout changes or claims about specific cracks. It also does not establish the exact wear of any individual painted line.

The module does not alter foliage, camera placement, ground extent, geometry, object visibility, exposure, render settings, or save files. It packs each image it actually uses. The parent generator must run its usual material-fallback export, packing and save steps afterward. World-projected scan nodes and procedural paint wear are intended for the Blender master and Cycles output; the lightweight browser may use mean-color fallbacks rather than reproducing these shader graphs. The world HDRI is not embedded into the GLB by the existing exporter.

## Reference sun and environment choice

The wider official reference shows a sun near image pixel (288,245) in its 1200 by 800 image. A ray through that manually observed point using the fitted reference camera implies an elevation of approximately **5.46°** and local XY azimuth **156.06°**, where x is east and y is north. This is a photographic inference, not an ephemeris calculation, verified capture date or precise light survey. The previous 32° Nishita sun gives a substantially different direction and shadow length.

The downloaded Qwantani pure-sky HDRI's high-luminance solar region is centered at UV approximately (0.600050,0.533797), corresponding to an elevation of **6.08°**. It supplies a close low-sun approximation without importing landscape. Its world lookup rotates around z by **−192.075924°** to align its native sun azimuth with the reference. No horizon tilt and no second artificial sun are added. One environment supplies the background, reflections and illumination, so their directions stay coherent. Its default strength remains 1.0. The first integrated probe retained AgX Medium High Contrast, exposure −0.85 and gamma 1.0; the current generator now uses the tested Medium Low Contrast / −0.35 / 1.15 settings described below. Neither adjustment rotates or tilts the HDRI.

The spherical mapping follows [Cycles' equirectangular coordinate implementation](https://github.com/blender/blender/blob/main/intern/cycles/kernel/camera/projection.h): native azimuth is `180° − 360° × u`. The lookup vector rotation is native azimuth minus the target scene azimuth. Bright-region positions were calculated from the downloaded floating-point HDR data, not its tonemapped thumbnail.

Spruit Sunrise is an optional **unregistered** photographic tree horizon. Its sun elevation is **8.02°**, so it is less closely aligned vertically than the default pure sky. It includes distant power pylons elsewhere in the panorama. They appear beyond the right side of the matched reference camera's estimated field of view when the sun is aligned, but may enter other views; that angular estimate is not an integrated-render acceptance. Using this HDRI does not make its trees, field or utilities part of measured Protolabs context. Keep that limitation visible wherever such a backdrop is used.

The default pure sky deliberately provides no replacement trees. The preserved first v07 probe has a large far-ground plane forming a straight visible horizon. Distant-context integration belongs to the scene generator and requires inspection across all cameras; its latest appearance is not established by the material studies. This shader module does not silently remove it.

## Reproduction and integration

From a fresh source checkout, ordinary Python's standard library is sufficient for acquisition:

```bash
python3 scripts/material_quality.py --download
```

Existing correct files are reused. A mismatched existing file is preserved and causes an error. Downloaded content is accepted only at its recorded size and SHA256; failed partial files are removed. No asset service account or token is used.

In `build_scene.py`, after the current world, camera and exposure setup and **before** executing `export_materials.py`, `bpy.ops.file.pack_all()`, and `save_as_mainfile`, invoke:

```python
from material_quality import apply_material_quality
apply_material_quality(ROOT)
```

To evaluate the optional field backdrop, use `apply_material_quality(ROOT, environment='spruit_sunrise')`. For a surface-only comparison that retains the existing world, use `environment=None`. `environment_strength` and `yaw_offset_deg` are explicit optional controls; a nonzero yaw offset moves the source sun away from the reference alignment and should be recorded with the resulting image.

The source passes Python compilation and the acquisition command verifies all active cached source hashes. The initial proposal's Blender 4.2.9 smoke check upgraded 15 named materials, packed 10 source images for the default configuration, created valid world nodes, and preserved the object inventory. A separate 320 by 213, one-sample world-only projection took 2.87 seconds and was visually inspected: the aligned sun appears at approximately (77,64), close to the reference's scaled (77,65), confirming the rotation sign and camera relationship. That sky-only check contains no campus geometry. Those initial checks established implementation behavior only; the subsequent integrated v07 probe exposed the glazing and frontage problems described above.

## Bounded v07 glass and tone study

Two isolated 900 × 600, 20-sample Cycles renders with three CPU threads used the preserved first v07 master (SHA256 `d9df348a833ca58acf88706daffe429203f9ee8fa8cc1c66187476d220f03c0c`). The first radiance render compared three AgX display settings with full-transmission glass. The second tested the current glass coat, pale trim and nonmetallic identity shader values. Each run verified that the loaded master file remained unchanged. No geometry, world direction, camera transform, scene save or GLB export occurred. Scripts, images and receipts are retained under the build workspace's `work/v07-glass-tone/`; they are study outputs, not delivery renders.

The coated case with `view_transform='AgX'`, `look='AgX - Medium Low Contrast'`, `exposure=-0.35`, and `gamma=1.15` improves dark-pane separation and frontage readability. This is a global display-transform shadow lift, without hue retouching or image compositing. It also lifts asphalt and does not reproduce the official photograph's richer sky color or all reflected detail. The material module now uses the tested shader values and leaves view settings to the generator. The current `build_scene.py` explicitly applies the same tested display transform:

```python
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium Low Contrast'
scene.view_settings.exposure = -0.35
scene.view_settings.gamma = 1.15
```

This records source integration, not acceptance of a newly generated master or production image set. Distant-context integration, four-camera inspection and motion review remain separate steps.


## Monument geometry is a separate fit

Frontage/sign readability involved both shader response and an incorrectly oriented sign. [monument-sign-fit.json](../research/monument-sign-fit.json) documents the separately inferred panel corners, fixed-camera fit, terrain anchor and uncertainty. Its nominal +83.82° yaw and 3.52 × 2.26 m panel reverse the incorrect top-edge screen slope; they are image-derived dimensions, not a physical measurement. The alternate left-edge interpretation and conditional perturbation ranges are retained rather than suppressed by the nominal 2.12-pixel corner RMS.

`monument_finish.apply_monument_finish(ROOT)` applies the same transform to the panel, all lettering/logo parts and base after geometry and the fixed cameras exist, before saving/exporting; the current generator now invokes it. It does not change their materials, the world, camera or view transform. The material helper does not move the sign. The isolated transform/projection check preserved the source master; combined rendered acceptance remains pending. See [visual accuracy](visual-accuracy.md#monument-sign-bounded-image-corner-fit) for the full distinction between fit residuals, implementation checks and visual fidelity.
