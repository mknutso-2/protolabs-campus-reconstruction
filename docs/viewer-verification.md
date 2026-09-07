# Browser verification

The recovered source passed a fresh cached `npm ci --offline --no-audit --no-fund` (746 packages), lint, and a complete static production build on 7 September 2026. Vinext's prerender step requires a localhost socket; the initial sandbox denied that socket, and the permitted build then completed successfully. The build retains a size warning for the dynamically loaded Three.js bundle.

The tested source includes commit `5bf2a27`, with the preserved v06 scene packaged for the browser. The generated browser model is 4.42 MB after meshopt compression. Its reduced foliage affects only the browser export; the Blender master retains complete foliage.

In the Codex browser, the model loaded, the saved headquarters camera opened through the page's WebMCP tool, and walking mode displayed its controls. Forward and lateral one-metre button steps visibly changed the camera position. No warning or error was returned in the browser log after those interactions. The reference comparison panel also opened using its keyboard action. These observations do not establish prolonged performance or exhaustive keyboard-hold/collision coverage.

The navigation helper was independently exercised for the usable exterior approach, rotated wing, vestibule, wall clearance, finite values and outer bounds. It follows simplified solid footprints from the scene generator, not a survey or an interior circulation model.

The viewer draws on changes rather than continually rendering an idle scene, with a 30 fps draw cap. Default still-view loading defers the WebGL model. Diffuse material fallbacks, omitted dynamic shadows and reduced foliage intentionally differ from the Cycles stills. This runtime check does not certify photographic appearance.

The app crash interrupted an earlier walking test. Its cause has not been established. The restored files and completed renders survived; the successful steps above were performed after recovery. Final v07 assets, the completed movie, private publishing and the deployed URL must be checked after they are staged.

## Updated interface check, 2026-09-07 20:24 UTC

The standalone Sites checkout was refreshed with the current app and navigation source, linted, built successfully, and reloaded in the existing browser tab. With the preserved v06 model assets, the saved headquarters view loaded, Walk and one-metre stepping worked, and selecting the same headquarters preset removed the walk pad, restored Orbit and returned the visible saved camera. No browser warning/error entries were reported in that bounded interaction. This confirms the reset-token fix; it does not validate pending v07 geometry, final video or deployment. The optimizer output at this check was 4,422,072 bytes with 69 meshes/nodes and 46 EXT_mesh_gpu_instancing nodes.
