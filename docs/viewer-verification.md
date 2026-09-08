# Browser verification

The earlier interface checks below used preserved v06 assets. The fresh v07c export and packaging checks at the end of this document supersede their model-size figures; current staged-site runtime review remains pending.

The recovered source passed a fresh cached `npm ci --offline --no-audit --no-fund` (746 packages), lint, and a complete static production build on 7 September 2026. Vinext's prerender step requires a localhost socket; the initial sandbox denied that socket, and the permitted build then completed successfully. The build retains a size warning for the dynamically loaded Three.js bundle.

The tested source includes commit `5bf2a27`, with the preserved v06 scene packaged for the browser. The generated browser model is 4.42 MB after meshopt compression. Its reduced foliage affects only the browser export; the Blender master retains complete foliage.

In the Codex browser, the model loaded, the saved headquarters camera opened through the page's WebMCP tool, and walking mode displayed its controls. Forward and lateral one-metre button steps visibly changed the camera position. No warning or error was returned in the browser log after those interactions. The reference comparison panel also opened using its keyboard action. These observations do not establish prolonged performance or exhaustive keyboard-hold/collision coverage.

The navigation helper was independently exercised for the usable exterior approach, rotated wing, vestibule, wall clearance, finite values and outer bounds. It follows simplified solid footprints from the scene generator, not a survey or an interior circulation model.

The viewer draws on changes rather than continually rendering an idle scene, with a 30 fps draw cap. Default still-view loading defers the WebGL model. Diffuse material fallbacks, omitted dynamic shadows and reduced foliage intentionally differ from the Cycles stills. This runtime check does not certify photographic appearance.

The app crash interrupted an earlier walking test. Its cause has not been established. The restored files and completed renders survived; the successful steps above were performed after recovery. Final v07 assets, the completed movie, private publishing and the deployed URL must be checked after they are staged.

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

Local detailed receipts are `work/viewer-v07c-final-check/master-validation.json` and `package-validation.json` in the outer workspace. Current staged-site inspection, completed still review, motion sample and encoded film remain separate acceptance steps.


## Saved eye-level cameras: orbit limit correction

The current production preview exposed a camera defect that the earlier navigation checks had missed: the entrance and arrival presets appeared above eye level. The orbit control's 87.3° polar limit raised cameras whose saved targets are above the viewer. With the actual Three r180 controls, it raised entrance local Z from 1.75 to 6.537746 m and arrival from 2.0 to 7.580561 m.

Restoring the standard `Math.PI` limit preserves all four saved positions over 240 control updates (maximum numeric drift 1.34e−13 m). The existing 36 mm horizontal-sensor field-of-view conversion also passes four aspect ratios. [The bounded numeric check](../research/viewer-camera-orbit-validation.json) measures position and field of view; it does not claim exact photographic registration or Blender/browser shading parity. Free orbit can look below its target, while walking retains its separate ground/collision rules.

After lint and production build passed, the actual current preview showed the entrance at its intended eye height. Visible forward/right walk steps and selecting the same entrance preset returned to Orbit mode and restored the view. The current browser model remains the hash-verified v07c package above. Final movie and hosted-site checks remain separate.
