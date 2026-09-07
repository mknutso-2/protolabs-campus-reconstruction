# Prioritized backlog

## P0 • evidence and visible resemblance

- [x] Verify public parcel ownership versus operational/visual context and record capture-date limitations. The confirmed headquarters parcel is 7.00 acres; neighboring context is separately identified. Public tax parcels are not a legal survey.
- [x] Acquire bounded lidar and public reference evidence; retain roof/terrain constraints, source ledgers, dates, coordinate systems, processing methods and uncertainty. Packaged raw-processing scripts have dry-run/import/hash checks; a full fresh packaged rerun remains under delivery verification.
- [x] Generate and inspect four fixed-view stills through v06. Preserve the v06 master, full/reduced GLBs, camera/material metadata, geometry check and snapshot hashes under `deliverables/iterations/v06/`.
- [x] Correct the inward-facing cube normals found in the earlier clean checkout. The v06 fresh generation/export and outward-volume checks pass; retain the original failure and subsequent correction in [fresh source verification](fresh-checkout-verification.md).
- [x] Replace the unsupported uniform northern forest band with the bounded lidar ground grid and 102 eligible canopy-envelope placements. Reproduce the constraints, verify placement heights, and retain uncertainty about trunk location, species and context beyond the aerial.
- [x] Prepare v07 CC0 texture/HDRI acquisition with checksums, the material-quality module, visual-finish module and revised original vehicle assets. Node/packing and isolated asset checks pass; integrated visual acceptance remains open.
- [ ] Inspect the v07 integrated reference-camera probe. Assess low-sun lighting, scanned surface response, restrained glazing/mullions, worn paint, entrance finish and the empty foreground court; do not treat successful execution as a resemblance pass.
- [ ] Continue matching entrance canopy, sloping roof, facade/window rhythm and glazing depth against attributed references. M2 visual acceptance remains open.
- [ ] After the v07 probe passes, render and inspect all four views. Resolve the straight far-ground horizon and landscape transitions without implying that an unregistered HDRI backdrop is measured site context. M3 campus-wide consistency remains open.

## P1 • environment and delivery

- [x] Implement pavement, curbs, islands, accessible bays, signage, vegetation and generic vehicles with evidence/provenance notes. Detailed resemblance and surface treatment remain open above.
- [ ] Refine roof equipment, facade depth, materials and small features where the reviewed views show discrepancies; preserve uncertainty for weakly evidenced rear/service areas.
- [x] Save the fixed cameras and generate the editable master and GLB.
- [x] Check the local viewer at `5bf2a27`: lint, clean npm dependency installation, production build, orbit/walk navigation, visible walk controls, rotated exterior footprints and saved-view selection. Offline installation used an existing package cache.
- [ ] Refresh and inspect the standalone reference gallery for the accepted current version, including attribution, saved transforms, preserved earlier versions and the current accuracy report.
- [ ] Refresh viewer assets after the v07 scene is accepted and check visibility, navigation, new material fallbacks, reference assets and saved-view correspondence.
- [x] Preserve the v05 preliminary opening motion sample and its bounded engineering diagnostics. It does not approve later scene revisions or full-path playback quality.
- [ ] Complete and inspect the current-revision 24-frame middle sample (frames 61–84) at 1280 × 720 / 24 fps, plus endpoint frames 1 and 144. Check leaf edges, shadows, reflections, continuity and clipping before the six-second cinematic. V06 motion was deliberately not run because its reviewed synthetic surfaces prompted v07.
- [ ] Render, inspect and encode the full cinematic only after the sample gate passes. Keep its completion status explicit.
- [x] Verify a clean v06 source archive: generate the master and both GLBs, preserve full master foliage, match camera/material baselines and all 102 canopy placements, and pass the corrected geometry checker. Retain the independent top-rounding threshold correction and original receipts.
- [ ] Complete the full v07 fresh-source delivery workflow, including mandatory CC0 material acquisition, integrated stills, accepted motion, matching viewer packaging and inspection. The v06 generation checks do not cover the new shaders or revised assets.
- [ ] Publish and verify the completed owner-only private viewer after its current model, stills, comparisons and movie are ready. Registration of the private site is not publication.
- [ ] Package source revision, derived-input identifiers, master scene, GLB, accepted stills/video, gallery and accuracy report in a versioned archive with a verified SHA-256 manifest.

## GitHub project

- [x] Create the [private repository](https://github.com/mknutso-2/protolabs-campus-reconstruction), prioritized issues and [draft PR #7](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/7). Authenticated connector mirroring is working and records equal source trees.
- [ ] Mirror the current local `feat/reference-lighting` branch and its v07 changes, with exact source-tree mappings and visual-check notes. It is not yet published at this update. Keep substantial changes synchronized with the appropriate draft PR. Normal Git CLI authentication/history reconciliation is documented; it does not prevent connector mirroring.

## P2 • later fidelity gaps

- [ ] More recent, dated ground views of every elevation.
- [ ] Accurate roof equipment, signage typography and mechanical layout.
- [ ] Surveyed curb elevations and drainage.
- [ ] Production UE5 import and performance evaluation on appropriate hardware.

Completion of evidence acquisition, v06 generation checks or viewer navigation does not close the visual-quality work in GitHub issues #2 and #3. See [brief.md](brief.md) for the acceptance gates, [fresh source verification](fresh-checkout-verification.md) for completed checks, and [visual-accuracy.md](visual-accuracy.md) for the existing discrepancy record, which must be refreshed for accepted v07 results.
