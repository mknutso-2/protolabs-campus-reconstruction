# Project brief

## Objective
Recognizable exterior reconstruction with architectural visualization quality, grounded in public aerial imagery, photographs and geospatial data. Editable Blender master, interactive walkthrough, fixed-view stills, cinematic flythrough, comparison gallery, reproducible private GitHub project.

## Acceptance gates

- [x] M0: environment inspected; dedicated local Git repository, private GitHub repository and draft PR created; headquarters address verified.
- [x] M1: ownership/context boundaries, measured roof/terrain constraints, dated source ledgers and acquisition records established; first frontage and fitted aerial reference camera implemented.
- [ ] M2: visual standard not fully accepted. Four v04 fixed-view stills have been inspected; the subsequent fresh-checkout check exposed inward-facing cube normals. The v05 correction and rerenders must be inspected before advancing this gate.
- [ ] M3: architectural and landscape treatment is implemented across the modeled exterior, but consistent visual quality is not yet accepted. Expanded wooded background and corrected geometry need review from every saved view.
- [x] M4: baseline master/GLB generation, local interactive orbit/walk navigation and saved camera views work. Refresh and recheck the viewer after v05 changes as part of delivery verification.
- [ ] M5: complete and inspect the delivery-resolution motion sample; correct temporal or camera defects before rendering and accepting the cinematic.
- [ ] M6: finish the reference gallery, repeat the full fresh-source workflow after corrections, and verify the complete versioned delivery. Instructions and provenance exist; complete fresh-checkout and artifact acceptance remain pending.

## Current review state

The four v04 still views have been inspected, and earlier iterations are preserved. The local Blender master, GLB export and interactive exterior viewer work. The reference comparison gallery is being finalized, with a candid review in [visual-accuracy.md](visual-accuracy.md).

A fresh-checkout check found a real geometry defect: the cube helper generated inward-facing normals. The v05 work corrects that winding and expands the wooded background. Those changes require fresh stills and viewer checks; v04 inspection does not certify the corrected revision. M2 and M3 remain open because recognizable architecture and functioning exports do not yet meet the complete visual standard.

The current delivery targets are 1600 × 1067 stills and a 1280 × 720, 24 fps, six-second exterior film. The opening 24-frame sample and full film remain pending inspection/completion. The project is managed in the [private GitHub repository](https://github.com/mknutso-2/protolabs-campus-reconstruction) and [draft PR #7](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/7); repository access is no longer a blocker.

## Rules
Dimensions from GIS/lidar are measured only to their source precision. Photo interpretation is visually confirmed where justified. Inferred details must remain flagged. No invented accurate interiors. Preserve reference attribution, dates, camera transforms and earlier iterations. Render counts and passing exports are not fidelity evidence.

## Runtime evaluation
Host: Intel i7-3610QM, 8 GB RAM, Intel integrated graphics / NVIDIA GTX 660M. Blender 4.2.9 LTS portable CPU Cycles is the working render path. The local glTF viewer provides exterior inspection, with Blender as master. UE5 remains evaluated but undelivered on this host; see [runtime-evaluation.md](runtime-evaluation.md) for the measured environment and evidence behind that decision.
