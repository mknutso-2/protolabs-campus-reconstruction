# Motion and exposure review

## v05 preliminary sample, 7 September 2026

The v05 sample is an engineering and appearance check, not an accepted final cinematic. Its oversized forest band was rejected and replaced by lidar-derived vegetation constraints in v06. A revised-geometry sample and native-speed playback review are required before final acceptance.

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

Probe inputs and metadata remain in the intermediate `work/assets/exposure_probe_*` files. That historical test informed the −0.85 exposure used in v06. V07 changes the illumination environment and material response, so the earlier exposure result cannot accept the new lighting. Final exposure must be recorded in the generator and delivery manifest after the revised scene is visually checked.

## v06 still review and early v07 probe

The preserved v06 aerial, entrance, arrival and campus-overview stills were all inspected and rejected as a final visual finish. The lidar-based north-context revision retains open ground/pond context, but its materials, glazing, repeated scenery and bare far horizon remained visibly schematic. **No v06 motion was rendered.** The earlier v05 sample cannot establish v06 or v07 motion quality.

The early v07 reference aerial was rendered at 1200 × 800 and 32 Cycles samples and visually compared with v06 and the official photo. Low-sun lighting, surface scans, an empty foreground lot and small entrance/flag corrections improve the result. Its straight bare far-ground horizon, dark entrance/sign and relatively uniform gray glazing still need attention. Distant woodland research is ongoing and is not represented by the inspected probe. All four full production v07 views remain pending. See [visual-accuracy.md](visual-accuracy.md) for the probe hash and detailed assessment.

No full film or delivery-resolution sample has been accepted. The final motion resolution and path duration must be selected explicitly after the visual corrections. A new sample must cover the faster middle section and endpoint as well as the slow start, and it must be inspected at native size and speed for foliage shimmer, roof/truss edge crawling, denoiser pulsing, camera smoothness and clipping. The full film remains deferred until those checks pass.

## Resume and file-integrity verification

The rendering pipeline now checks a SHA-256 fingerprint of **every generated frame's camera location, Euler rotation, scale and lens**, alongside the source master hash and render/PNG settings, before reusing any existing frame. This covers parts of the path outside the selected render range. The camera equations, 24 fps, fixed Cycles seed 5540 and disabled animated seed remain unchanged. Seed continuity helps reproducibility; it is not itself a temporal-quality pass.

[frame_integrity.py](../scripts/frame_integrity.py) validates chunk CRCs throughout each PNG, complete chunk framing, matching dimensions, the terminal IEND, the zlib image stream, decoded scanline lengths and scanline filter bytes. Standard and Adam7 layouts are supported. A damaged PNG with a compatible manifest is rendered again. An unreadable/incompatible manifest, including a legacy one without the full-path fingerprint, is rejected before its frames are reused. Manifest and progress JSON are replaced atomically. [render_motion.py](../scripts/render_motion.py) accepts `--output-dir` for isolated frame/manifest output, and both single-frame and range resume use the same checks. Default output directories and camera path are unchanged.

Actual Blender 4.2.9 tests used a separate one-cube master at **96 × 54, one Cycles sample**, without touching the production master or rendering into production frame directories. They demonstrated:

- A valid completed frame was skipped with unchanged file hash and modification time.
- A byte flipped inside IDAT, with the original PNG header/dimensions/IEND intact, caused CRC rejection and rerendering.
- A changed lens at generated frame 13 prevented reuse of requested frame 1, confirming full-path coverage.
- Corrupt JSON, incompatible render settings and a legacy manifest lacking the fingerprint were rejected before overwriting the existing frame or manifest.
- A bad zlib stream with a recomputed chunk CRC, truncated data, trailing bytes and mismatched dimensions were rejected.
- A preserved 1280 × 720 campus frame passed validation without alteration; small Adam7 and 16-bit RGBA fixtures also passed.

The fixed-seed rerender had identical decoded image scanlines. Its full PNG hash differed because Blender embeds Date and RenderTime text metadata; that difference was verified rather than treated as a pixel change. The fixture master was unchanged. Workspace receipts are retained under `work/motion-review/` in `motion-resume-receipt.md`, `motion-resume-validation.json`, `png-integrity-additional-checks.json`, and the per-case Blender logs. These are successful resume/integrity checks, not acceptance of visual finish or motion. Start the revised production sequence with a fresh compatible manifest; do not mix historical v05/v06 images with v07 frames.


## v07 framing correction before the complete sample

Only two middle frames (61 and 62) were rendered from master `7dd2ff5a` before the job was stopped to correct a visible main/north terrain join. They remain preserved in the workspace as an incomplete, unaccepted study. Native inspection of frame 61 also showed the northeastern wing crossing the right edge and the monument base crossing the bottom edge.

The revised six-second path keeps the existing smoothstep timing and target `(55,16,3.5)`, but uses a shorter **−52° to −30°** arc, **145 to 119 m** radius, **29 to 16 m** camera height and **28 to 30 mm** lens. The saved fixed-view cameras are unchanged. A read-only analysis of 1,154 evaluated architectural, entrance, flag and monument objects (140,147 vertices) checked all 144 frames, with projection calibrated against Blender. Every selected feature retains at least 5% image margin; the limiting endpoint northeastern fascia has **64.95 pixels / 5.074%** right margin at 1280 × 720. Vegetation, paving and adjacent context were excluded from this conservative architectural framing check.

[The framing receipt](../research/motion-framing-review.json) identifies the source master, selected geometry, alternatives and projected bounds. The subsequent northern terrain correction does not move the selected objects. This is a framing check, not playback or temporal-quality acceptance. Render a complete new frames 61–84 sample and endpoint views from the revised master/path; the paused two frames cannot be reused. The full camera-path hash in each render manifest prevents accidental mixing with the earlier path.


## v07c sample accepted for full-film rendering — 7 September 2026

At **23:46:49 UTC**, root accepted the complete **frames 61–84** sample and native endpoints **1/144** for a six-second **1280 × 720, 24 fps, 16-sample Cycles** film. The sample uses master `3d861d6c2e1c54f7c144d52c5e74f21568b18d047a326631405c9da1956b8e5a` and the gentler path `2328277591e0c3c1f04ff040c49497cd2e8e77246d4926ee693b2187215bfbac`. Its MP4 SHA-256 is `1f906d4419f9c4dde677f518dab713f15ef3ad89f7a2598d1e00031b8f422f62`. The [portable acceptance receipt](../research/v07c-motion-sample-review.json) records all 26 inspected PNG hashes, sample and endpoint manifests, settings, source revisions and review scope. The original authorization SHA-256 is `2697b2835b58f210231209c7d2c0f32d3328079febf2f6ef1d84ca1199c2ee98`.

Root inspected native frame 61, both endpoints, all 24 roof/truss and foreground-foliage crops, and actual encoded browser playback at normal speed: **Playing 0.262/1.000 s → Paused 1.000/1.000 s**, without an error, followed by repeated fullscreen playback. Independent review inspected native frames 61, 72 and 84 and endpoints 1 and 144, all 24 tiles in five native crop sequences, and selected adjacent pairs. All24 PNGs were complete and unique; the MP4 fully decoded at the documented resolution/cadence. Roof/truss, glazing, crowns and shadows remained coherent. **Mild pixel-level foliage and roof texture variation was accepted after playback.** Simplified scenery and synthetic material appearance remain; numeric luma/registration measurements were descriptive, not pass thresholds.

The full-film driver subsequently started with all **26 reviewed seeds** copied unchanged. A bounded **23:50:22 UTC** check confirmed their hashes and original manifests, frame 1 actually skipped, and new frames 2 and 3 rendered; the initial missing count was 118. **The full film was still rendering and was neither complete nor visually accepted at this record.** Its eventual 144-frame encoding needs its own complete playback review. Repeating the one-second sample was a review control only, not a film substitute; the earlier paused v07b frames remain unaccepted.


## v07c complete film accepted — 8 September 2026 UTC

At **2026-09-08T01:55:53.567198+00:00**, root accepted the complete six-second film for versioned delivery with the documented limitations. The [portable final receipt](../research/v07c-cinematic-review.json) binds all 144 frames, the encoded movie, motion scene, camera path, prior sample gate and independent inspection. The film is **1280 × 720, 24 fps, 16 Cycles samples**, 2,924,950 bytes, SHA-256 `67bdc8f5448c1652f350b72f3355dc9ce06076c49f32680011f1dc2a8277e859`.

The driver completed at 01:41:05 UTC, reusing the 26 accepted sample/endpoint images unchanged and rendering the remaining 118. Independent checks verified complete PNG integrity, 144 unique image frames, unchanged previously inspected frames and a complete MP4 decode with continuous timestamps over exactly six seconds. Native roof/truss, crown, glazing/shadow and right-wing-edge strips covered the remaining sequence; prior frames 1–85 retained their earlier inspection. Explicit joins 1/2, 60/61, 84/85, 85/86 and 143/144 showed no new camera, lighting or geometry discontinuity.

Root played the actual movie at normal speed, observing 0.011/6.000 s, 0.262/6.000 s and the paused 6.000/6.000 s endpoint without a playback error, then inspected repeated fullscreen playback and native source frame 115. Roof/truss, glazing, crowns and shadows remain coherent, with the building, flag and monument within the frame. Fine leaf and roof pixels still vary; broad ground tones, sparse context and synthetic material response remain visible. These limitations are accepted for this release, without a photorealism claim.

The editable motion scene reopened successfully in background Blender 4.2.9: animated active camera, frames 1–144, 24 fps, 1280 × 720 and Cycles. No graphical-editor test was performed. The final local walkthrough loads this same movie with duration 6.000 s, native dimensions 1280 × 720, readiness 4 and no reported video/browser error. Site publication remains separate and unperformed.
