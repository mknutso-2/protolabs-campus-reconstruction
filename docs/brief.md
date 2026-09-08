# Project brief

## Objective
Recognizable exterior reconstruction with architectural visualization quality, grounded in public aerial imagery, photographs and geospatial data. Editable Blender master, interactive walkthrough, fixed-view stills, cinematic flythrough, comparison gallery, reproducible private GitHub project.

## Acceptance gates

- [x] M0: environment inspected; dedicated local Git repository, private GitHub repository and draft PR created; headquarters address verified.
- [x] M1: ownership/context boundaries, measured roof/terrain constraints, dated source ledgers and acquisition records established; first frontage and fitted aerial reference camera implemented.
- [x] M2: inspect the integrated v07c frontage. The corrected entrance return, glazing, signs and apron have been checked in actual full-resolution images; remaining material/detail approximations are documented.
- [x] M3: inspect all four final v07c stills at 1600 × 1067 / 64 samples. The overview independently confirms the corrected terrain join and flat pond; this records image inspection, not photographic equivalence.
- [x] M4: current v07c master/GLB generation and bounded local viewer inspection passed, including all four saved views, walking/reset, stills/comparisons and fullscreen behavior. Final local movie integration also passed; approved deployment remains a separate delivery check.
- [x] M5: inspect the delivery-resolution sample/endpoints, then the complete film. The sample gate passed September 7 at 23:46:49 UTC, and the full film was accepted with documented limits September 8 at 01:55:53 UTC; see the [complete-film receipt](../research/v07c-cinematic-review.json).
- [x] M6: verify the complete versioned delivery workflow. Clean static generation, all four stills, the gallery, sample/full-film acceptance and final local viewer integration passed. The actual release candidate passed all 202 file hashes and an extracted viewer installation/build; [delivery verification](delivery-verification.md) records scope and final-manifest use. Private hosting awaits separate approval.

## Current review state

Earlier iterations through v06 are preserved, including rejected visual treatments and the original cube-normal failure. The winding error has been corrected and checked in later clean builds. V07 combines licensed surface scans, coherent low-sun lighting, coated glazing, revised generic assets and better constrained campus planting. Inspection continues to identify and correct visible discrepancies; source checks do not substitute for visual acceptance.

The clean source at `e29ad4b9` generated the final static artifacts. [Fresh v07c verification](fresh-checkout-v07c.md) binds the master, exports and all four inspected stills to their hashes. The [accuracy account](accuracy-summary.md) summarizes current limits; the [long review record](visual-accuracy.md) retains earlier rejected studies. The gentler path's delivery-resolution sample and endpoints are accepted for full-film rendering; [the portable receipt](../research/v07c-motion-sample-review.json) records the exact master, path, images, movie and inspection scope.

The delivery settings are 1600 × 1067 stills and a 1280 × 720, 24 fps, six-second exterior film. Frames 61–84 and endpoints 1/144 were inspected at 16 Cycles samples; mild pixel-level foliage and roof texture variation was accepted after sample playback. The complete 144-frame film passed full decoding, actual playback and independent image review and was accepted with documented limits at 01:55:53 UTC on September 8, 2026. Final local movie integration also passed. The versioned delivery workflow passed extraction and build checks; see [delivery verification](delivery-verification.md). Private-site publication awaits the user's required separate approval; no upload or deployment has occurred. The [private GitHub project](https://github.com/mknutso-2/protolabs-campus-reconstruction) includes merged [PR #7](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/7) and [PR #8](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/8); [PR #9](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/9) contains the final delivery changes.

## Rules
Dimensions from GIS/lidar are measured only to their source precision. Photo interpretation is visually confirmed where justified. Inferred details must remain flagged. No invented accurate interiors. Preserve reference attribution, dates, camera transforms and earlier iterations. Render counts and passing exports are not fidelity evidence.

## Runtime evaluation
Host: Intel i7-3610QM, 8 GB RAM, Intel integrated graphics / NVIDIA GTX 660M. Blender 4.2.9 LTS portable CPU Cycles is the working render path. The local glTF viewer is the selected exterior walkthrough, with Blender as master. UE5 evaluation is complete; a future UE5 application is optional follow-up work. See [runtime-evaluation.md](runtime-evaluation.md) for the measured environment and evidence behind that decision.
