# Project brief

## Objective
Recognizable exterior reconstruction with architectural visualization quality, grounded in public aerial imagery, photographs and geospatial data. Editable Blender master, interactive walkthrough, fixed-view stills, cinematic flythrough, comparison gallery, reproducible private GitHub project.

## Acceptance gates

- [x] M0: environment inspected; dedicated local Git repository, private GitHub repository and draft PR created; headquarters address verified.
- [x] M1: ownership/context boundaries, measured roof/terrain constraints, dated source ledgers and acquisition records established; first frontage and fitted aerial reference camera implemented.
- [x] M2: inspect the integrated v07c frontage. The corrected entrance return, glazing, signs and apron have been checked in actual full-resolution images; remaining material/detail approximations are documented.
- [x] M3: inspect all four final v07c stills at 1600 × 1067 / 64 samples. The overview independently confirms the corrected terrain join and flat pond; this records image inspection, not photographic equivalence.
- [x] M4: baseline master/GLB generation, local interactive orbit/walk navigation and saved camera views work. Refresh and recheck the viewer with the final v07 scene as part of delivery verification.
- [x] M5: inspect the delivery-resolution middle sample and endpoints. Accepted for full-film rendering on September 7, 2026 at 23:46:49 UTC; the complete cinematic requires separate playback inspection and acceptance.
- [ ] M6: finish the reference gallery, repeat the full fresh-source workflow after corrections, and verify the complete versioned delivery. Instructions and provenance exist; complete fresh-checkout and artifact acceptance remain pending.

## Current review state

Earlier iterations through v06 are preserved, including rejected visual treatments and the original cube-normal failure. The winding error has been corrected and checked in later clean builds. V07 combines licensed surface scans, coherent low-sun lighting, coated glazing, revised generic assets and better constrained campus planting. Inspection continues to identify and correct visible discrepancies; source checks do not substitute for visual acceptance.

The clean source at `e29ad4b9` generated the final static artifacts. [Fresh v07c verification](fresh-checkout-v07c.md) binds the master, exports and all four inspected stills to their hashes. The [accuracy account](accuracy-summary.md) summarizes current limits; the [long review record](visual-accuracy.md) retains earlier rejected studies. The gentler path's delivery-resolution sample and endpoints are accepted for full-film rendering; [the portable receipt](../research/v07c-motion-sample-review.json) records the exact master, path, images, movie and inspection scope.

The current delivery targets are 1600 × 1067 stills and a 1280 × 720, 24 fps, six-second exterior film. Frames 61–84 and endpoints 1/144 were inspected at 16 Cycles samples; mild pixel-level foliage and roof texture variation was accepted after sample playback. The full film is rendering and remains unaccepted; the hosted walkthrough and versioned release are also pending. The project is managed in the [private GitHub repository](https://github.com/mknutso-2/protolabs-campus-reconstruction) and [draft PR #7](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/7); repository access is no longer a blocker.

## Rules
Dimensions from GIS/lidar are measured only to their source precision. Photo interpretation is visually confirmed where justified. Inferred details must remain flagged. No invented accurate interiors. Preserve reference attribution, dates, camera transforms and earlier iterations. Render counts and passing exports are not fidelity evidence.

## Runtime evaluation
Host: Intel i7-3610QM, 8 GB RAM, Intel integrated graphics / NVIDIA GTX 660M. Blender 4.2.9 LTS portable CPU Cycles is the working render path. The local glTF viewer provides exterior inspection, with Blender as master. UE5 remains evaluated but undelivered on this host; see [runtime-evaluation.md](runtime-evaluation.md) for the measured environment and evidence behind that decision.
