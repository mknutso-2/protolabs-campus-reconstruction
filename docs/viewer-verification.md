# Browser verification

The current local v07c preview has passed the bounded interface review recorded below. The earlier sections preserve v06 observations; the fresh v07c figures supersede their model sizes. The complete film is now rendered and encoded, and all 12 final payload assets passed packaging. Final local movie integration passed, and the film was accepted with documented limits at 01:55:53 UTC on September 8, 2026. Private-site publication awaits the user's required separate approval; no upload or deployment has occurred.

## Historical v06 interface check — September 7, 2026

The recovered source passed a fresh cached `npm ci --offline --no-audit --no-fund` (746 packages), lint, and a complete static production build on 7 September 2026. Vinext's prerender step requires a localhost socket; the initial sandbox denied that socket, and the permitted build then completed successfully. The build retains a size warning for the dynamically loaded Three.js bundle.

The tested source includes commit `5bf2a27`, with the preserved v06 scene packaged for the browser. The generated browser model is 4.42 MB after meshopt compression. Its reduced foliage affects only the browser export; the Blender master retains complete foliage.

In the Codex browser, the model loaded, the saved headquarters camera opened through the page's WebMCP tool, and walking mode displayed its controls. Forward and lateral one-metre button steps visibly changed the camera position. No warning or error was returned in the browser log after those interactions. The reference comparison panel also opened using its keyboard action. These observations do not establish prolonged performance or exhaustive keyboard-hold/collision coverage.

The navigation helper was independently exercised for the usable exterior approach, rotated wing, vestibule, wall clearance, finite values and outer bounds. It follows simplified solid footprints from the scene generator, not a survey or an interior circulation model.

The viewer draws on changes rather than continually rendering an idle scene, with a 30 fps draw cap. Default still-view loading defers the WebGL model. Diffuse material fallbacks, omitted dynamic shadows and reduced foliage intentionally differ from the Cycles stills. This runtime check does not certify photographic appearance.

The app crash interrupted an earlier walking test. Its cause has not been established. The restored files and completed renders survived; the successful steps above were performed after recovery. At this historical checkpoint, v07 assets, the completed movie and deployment had not been checked. Later local v07c results follow below; publication remains separate.

## Updated interface check, 2026-09-07 20:24 UTC

The standalone Sites checkout was refreshed with the current app and navigation source, linted, built successfully, and reloaded in the existing browser tab. With the preserved v06 model assets, the saved headquarters view loaded, Walk and one-metre stepping worked, and selecting the same headquarters preset removed the walk pad, restored Orbit and returned the visible saved camera. No browser warning/error entries were reported in that bounded interaction. This confirms the reset-token fix; it does not validate pending v07 geometry, final video or deployment. The optimizer output at this check was 4,422,072 bytes with 69 meshes/nodes and 46 EXT_mesh_gpu_instancing nodes.

## Fresh v07c export check, 2026-09-07 23:07 UTC

The clean build from `e29ad4b9e9a4a15c3de4772288c105aca2bd8a56` includes the north terrain join correction and browser-only distant canopy proxies. A read-only Blender inspection and independent scratch packaging passed while the four current stills were rendering. No master, full GLB, still, or staged Site file was modified by these checks.

| Artifact | SHA-256 |
| --- | --- |
| Packed master | `3d861d6c2e1c54f7c144d52c5e74f21568b18d047a326631405c9da1956b8e5a` |
| Full GLB | `2916b2fe580ff1e25296fc3110c7cacbc363fc7d570fe3b5cad7f0024f474860` |
| Raw reduced browser GLB | `3dae8303843f07867e092581844c6ccc43d90616bb40819cc3d3623ef588a876` |
| Prepared mean-albedo GLB | `79966a3b423b8b198ccf9b2628b23a1a9fcd367451d16738256c05a351efb48c` |
| Optimized scratch browser GLB | `d7a84c65e0936f0f95618ca3db691dba0d3ec6c235d386f3d1007017cf394fed` |

The optimized asset is **25,747,608 bytes (24.554832 MiB)**, leaving 466,792 bytes below a 25 MiB per-asset ceiling. This figure describes the checked GLB, not a published-site result.

The saved master contains 15,737,024 visible vegetation triangles, including 12,279,332 triangles across the 1,139 original distant leaf-card objects. It contains no temporary browser foliage/proxy meshes. Comparing the raw full and browser GLBs verified identical node transforms, exact local bounds for all 1,139 distant proxies (maximum error 0 m), six shared proxy meshes with 1,388 triangles each, and byte-identical topology/vertex attributes/material identities for 2,085 other geometry nodes. The exported 178 campus/north tree nodes retain the established reduced leaf cards; the master retains their full geometry. The existing 61 solid distant groups and 347 NLCD crown groups remain intact.

Packaging used the recorded mean linear albedos before optimization, then `optimize --compress false --simplify false --palette false --texture-compress false` and the separate lossless Meshopt helper. All **161 POSITION accessors remain FLOAT32 (`5126`)**. Decoding the final compressed GLB and comparing every position array with the precompression joined GLB gave exact equality. The six distinct asphalt, roof, concrete, precast and grass albedos survived; all five leaf alpha-cutout materials remained. The prepared file preserves BIN/image/topology bytes. All input scene-file hashes were unchanged after both checks.

The existing performance comparison belongs to the preserved `7dd2ff5a…` master and the same `reference_aerial` path, not this fresh v07c package. At 1280 × 680, DPR 1, on the reported Intel HD Graphics 4000 renderer, an eight-second moving-camera diagnostic measured 6.49 fps with distant cards and 17.79 fps with the proxies; the proxy median/p95 frame intervals were 56.9/67.8 ms. Root inspected the proxy aerial and overview without browser warnings/errors. The diagnostic used `preserveDrawingBuffer`, background workload was not independently isolated, and these observations do not establish 60 fps, other-device performance, or acceptance of the current staged site. See [the performance record](viewer-performance.md).

Local detailed receipts are `work/viewer-v07c-final-check/master-validation.json` and `package-validation.json` in the outer workspace. At this 23:07 UTC checkpoint, staged-interface inspection, still review, the motion sample and encoded film were separate outstanding steps. The subsequent static/sample records and local interface checks supersede those pending statuses within their respective scopes.


## Saved eye-level cameras: orbit limit correction

The current production preview exposed a camera defect that the earlier navigation checks had missed: the entrance and arrival presets appeared above eye level. The orbit control's 87.3° polar limit raised cameras whose saved targets are above the viewer. With the actual Three r180 controls, it raised entrance local Z from 1.75 to 6.537746 m and arrival from 2.0 to 7.580561 m.

Restoring the standard `Math.PI` limit preserves all four saved positions over 240 control updates (maximum numeric drift 1.34e−13 m). The existing 36 mm horizontal-sensor field-of-view conversion also passes four aspect ratios. [The bounded numeric check](../research/viewer-camera-orbit-validation.json) measures position and field of view; it does not claim exact photographic registration or Blender/browser shading parity. Free orbit can look below its target, while walking retains its separate ground/collision rules.

After lint and production build passed, the actual current preview showed the entrance at its intended eye height. Visible forward/right walk steps and selecting the same entrance preset returned to Orbit mode and restored the view. The browser model remained the hash-verified v07c package above. At this camera-fix checkpoint, final movie and hosted-site checks were separate outstanding steps; the later local movie result is recorded below.


## Current local v07c interface, September 8, 2026 UTC

The staged production build uses the current v07c model hash above and all four current 1600 × 1067 stills. Lint and static production build passed. In the actual Codex browser, all four saved cameras opened; forward/right walking steps changed the view; selecting the same entrance preset exited Walk and restored Orbit. The three comparison choices displayed their corresponding attributed photographs and current renders. All four still images loaded at their full dimensions. No browser warning/error entries were reported after this bounded sequence. This was the local interface check before final movie integration. The later movie result follows below; publication remains a separate gate.

The fullscreen button now toggles exit as well as entry and updates its accessible label. Actual entry showed “Exit fullscreen walkthrough”; clicking it restored the page tabs and normal layout. Resize processing preserved the camera aspect and redrew the scene.

The actual Intel HD Graphics 4000 WebGL context declines requested multisample antialiasing. Unsupported contexts now navigate at the existing `min(devicePixelRatio, 1.5)` and draw one DPR 2 frame after 200 ms without camera/input changes. Contexts with native antialiasing retain their original ratio. A controlled timing check covers repeated input, the 30 fps cap and no additional idle draws; it is not a browser performance benchmark. Read-only DOM observations confirm a settled 1974 × 1148 buffer for a 987 × 574 canvas and 3840 × 2160 for a 1920 × 1080 fullscreen canvas.

The sharper resting image improves thin-feature coverage but does **not** eliminate broken subpixel parking lines and roof-band aliasing at shallow angles. Equal-camera comparisons of the prepared and final GLB, near planes of 0.15 and 10 m, active logarithmic depth, and a paint-only polygon offset did not visibly resolve that pattern. Those experimental depth/bias changes were not adopted. The browser also retains simplified diffuse shading, dark opaque glazing, no dynamic shadows, and reduced distant canopy; the Cycles stills provide the detailed lighting/material presentation.

Read-only rays through 116 corrected-row points agreed between the master and prepared GLB: 10.5–13.1 mm vertical clearance and 137–732 standard 24-bit same-ray depth steps, with no sampled point buried. This weighs against depth quantization for those rows. Large roof faces retain constant, face-aligned vertex normals; the cause of every roof band is not established. Some older curved stripes elsewhere partly intersect asphalt or sit behind nearer terrain, which remains a separate geometry limitation. The [portable runtime receipt](../research/viewer-v07c-runtime-review.json) binds this local check to the current page and model.

## Final movie packaging — September 8, 2026 UTC

All 12 generated viewer payload files passed packaging, including the model/camera/terrain/material data, four JPEG stills, three references and the full six-second movie. The movie is 2,924,950 bytes, SHA-256 `67bdc8f5448c1652f350b72f3355dc9ce06076c49f32680011f1dc2a8277e859`. It passed complete decoding, actual normal/fullscreen playback at 1280 × 720 and independent image review. [Film acceptance](../research/v07c-cinematic-review.json) was recorded at 01:55:53 UTC on September 8, 2026; the [motion record](motion-review.md) retains fine-detail variation and scenery/material limitations.

The local preview was restored from all 18 main viewer source files plus the 12 final payload assets; the production build completed with exit code 0. At localhost:3000, the actual Motion panel displayed the six-second approach from `/renders/flythrough.mp4`, with duration 6 seconds, native size 1280 × 720, ready state 4 and no video error. No browser warning/error entries were reported. The model and still bytes were unchanged, so the preceding bounded interface checks remain applicable. This completes local movie integration; it does not establish a deployed URL.

The [portable final-viewer receipt](../research/v07c-final-viewer-review.json) binds the 12 payload assets, completed build and actual movie-panel check. Workspace evidence is `work/site-final-stage.json` and `work/site-final-build.log`. The standalone local Site checkout is `4514c7ba462d9a2ed2ec98725c3f58accb4a52c0`. Its prepared Site archive was checked against all 32 build payload files plus normalized hosting metadata: 22,469,782 bytes, SHA-256 `904a6910f77c3e9529ac364f3916e80b135b55e5aaed3af68df4bc81175fb0c3`, recorded in `work/site-final-v1-archive-validation.json`. This is the prepared hosting archive, not the versioned project-delivery ZIP. The delivery ZIP and its extraction verification remain pending. Private-site publication still requires separate user approval; no push, upload or deployment has occurred.
