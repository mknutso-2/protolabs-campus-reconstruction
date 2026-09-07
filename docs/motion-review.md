# Motion and exposure review

## v05 preliminary sample, 7 September 2026

The v05 sample is an engineering and appearance check, not an accepted final cinematic. Its forest placement is being replaced with lidar-derived vegetation constraints in v06. A revised-geometry sample and native-speed playback review are required before final acceptance.

The encoded sample is `deliverables/iterations/v05/motion-sample.mp4`: 24 contiguous, distinct frames at 1280 × 720 and 24 fps, lasting exactly 1.00 second. The source is frames 1–24 of a six-second, 144-frame camera path. Rendering used Cycles CPU, 16 samples, denoising, a fixed sampling seed, and a 0.35-frame shutter. Encoding used H.264/libx264, CRF 18, yuv420p, and fast-start MP4. Encoding preserved every frame and the original resolution; it applied no interpolation, scaling, looping, or missing-frame substitution. FFmpeg decoded all 24 encoded frames without an error.

Source master SHA-256: `3600cd9b9b0af9cc86a9b5186c69bbfe52a9bf5b59597e7f2f770f1a3c6e0176`. The sample's `path.json` records source revision `3fbe7285c692e133fa5affd96240126d890b6172` and camera keyframes. That metadata identifies the scene used by this preliminary sample; it does not describe later geometry revisions.

Native-resolution inspection of frames 1, 12, and 24 found no gross geometry pop, clipped building, empty render, or camera obstruction. The moving framing retains the building, monument sign, forecourt, and distinctive roof structure. The foreground leaves and forest contain high-frequency detail that may shimmer at 720p. White roof panels retain seam detail, but the overall result still has a synthetic appearance: repetitive tree forms, simple material variation, simplified cars, and clean paving remain visible.

This sample covers the slow initial portion of the easing curve. It cannot establish the smoothness or framing of the faster middle or lower final part of the six-second path. Review a short segment near the middle of the revised path, plus the endpoint, before rendering the complete film. Native-speed playback must specifically check roof seams and truss edges for crawling, foliage for shimmer, and denoised shadows for pulsing. Static frame inspection alone does not pass those checks.

### Bounded temporal diagnostics

`deliverables/iterations/v05/motion-sample-diagnostics.json` records dimensions, continuity, uniqueness, brightness changes, and local difference measurements. No frames are missing or byte-identical. Mean image luma rises gradually from 160.97 to 162.46 on an 8-bit scale as the camera moves; the largest adjacent-frame mean change is 0.18. This does not show a gross whole-image brightness flash.

A small diagnostic fitted integer translations within ±4 pixels to selected image regions, then measured the remaining high-frequency difference. The median residual is 8.17/255 in foliage, 1.33/255 in a roof-panel region, and 0.04/255 in a sky region. These are **not flicker scores or acceptance thresholds**: camera motion, perspective, occlusion, subpixel coverage, and imperfect registration all contribute. A facade region also has a relatively large residual, illustrating why the numbers cannot independently attribute variation to stochastic noise. They identify detailed moving edges as priorities for playback inspection rather than proving a defect or a clean result.

## Controlled exposure probe

A separate test loaded the v05 master without saving it and changed exposure from −0.25 to −0.85 stops. It retained the AgX Medium High Contrast look, world strength 0.30, and 32° sun elevation. The test rendered the fitted reference camera at 1000 × 667 and 24 samples; the baseline image is 1600 × 1067, so their sampling and pixel resolution differ. The expected exposure multiplier in linear light is approximately 0.660.

Visual comparison of the baseline and probe favors −0.85 for the next scene test. It modestly improves the distinction between white roof and fascia surfaces and reduces the bright, washed appearance of paving and vegetation. It also darkens glazing and sheltered entrance areas, which still need inspection in the close entrance view. The change alone does not make the scene photographic and does not correct geometry, forest placement, repetitive assets, or material accuracy. No master, generator, or material was modified by this review.

Probe inputs and metadata remain in the intermediate `work/assets/exposure_probe_*` files. Final exposure must be recorded in the generator and delivery manifest after the revised scene is visually checked.
