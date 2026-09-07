# Project brief

## Objective
Recognizable exterior reconstruction with architectural visualization quality, grounded in public aerial imagery, photographs and geospatial data. Editable Blender master, interactive walkthrough, fixed-view stills, cinematic flythrough, comparison gallery, reproducible private GitHub project.

## Acceptance gates

- [x] M0: environment inspected; dedicated local Git repository, private GitHub repository and draft PR created; headquarters address verified.
- [x] M1: ownership/context boundaries, measured roof/terrain constraints, dated source ledgers and acquisition records established; first frontage and fitted aerial reference camera implemented.
- [ ] M2: inspect the final integrated v07 frontage. Materials, glazing, lettering, tree heights and fascia revisions have been inspected; close-view review prompted a canopy-return correction, now verified in a cropped render.
- [ ] M3: inspect all four final v07 stills. Continuous regional terrain, flat basin-clipped water and corrected entrance parking have passed bounded geometry and visual checks; their combined production images are rendering.
- [x] M4: baseline master/GLB generation, local interactive orbit/walk navigation and saved camera views work. Refresh and recheck the viewer with the final v07 scene as part of delivery verification.
- [ ] M5: complete and inspect the delivery-resolution motion sample; correct temporal or camera defects before rendering and accepting the cinematic.
- [ ] M6: finish the reference gallery, repeat the full fresh-source workflow after corrections, and verify the complete versioned delivery. Instructions and provenance exist; complete fresh-checkout and artifact acceptance remain pending.

## Current review state

Earlier iterations through v06 are preserved, including rejected visual treatments and the original cube-normal failure. The winding error has been corrected and checked in later clean builds. V07 combines licensed surface scans, coherent low-sun lighting, coated glazing, revised generic assets and better constrained campus planting. Inspection continues to identify and correct visible discrepancies; source checks do not substitute for visual acceptance.

The clean source at `e9ed871` is generating an editable master, full/reduced GLBs and four production stills after the latest canopy-return, parking, regional-ground and pond corrections. The [accuracy record](visual-accuracy.md) retains individual studies and remaining approximations. Final integrated images and motion are not yet accepted.

The current delivery targets are 1600 × 1067 stills and a 1280 × 720, 24 fps, six-second exterior film. A 24-frame middle sample, endpoint checks and the full film remain pending inspection/completion. The project is managed in the [private GitHub repository](https://github.com/mknutso-2/protolabs-campus-reconstruction) and [draft PR #7](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/7); repository access is no longer a blocker.

## Rules
Dimensions from GIS/lidar are measured only to their source precision. Photo interpretation is visually confirmed where justified. Inferred details must remain flagged. No invented accurate interiors. Preserve reference attribution, dates, camera transforms and earlier iterations. Render counts and passing exports are not fidelity evidence.

## Runtime evaluation
Host: Intel i7-3610QM, 8 GB RAM, Intel integrated graphics / NVIDIA GTX 660M. Blender 4.2.9 LTS portable CPU Cycles is the working render path. The local glTF viewer provides exterior inspection, with Blender as master. UE5 remains evaluated but undelivered on this host; see [runtime-evaluation.md](runtime-evaluation.md) for the measured environment and evidence behind that decision.
