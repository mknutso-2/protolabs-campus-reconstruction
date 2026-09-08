# Prioritized backlog

## P0 • evidence and visible resemblance

- [x] Verify public parcel ownership versus operational/visual context and record capture-date limitations. The confirmed headquarters parcel is 7.00 acres; neighboring context is separately identified. Public tax parcels are not a legal survey.
- [x] Acquire bounded lidar and public reference evidence; retain roof/terrain constraints, source ledgers, dates, coordinate systems, processing methods and uncertainty. Packaged raw-processing scripts have dry-run/import/hash checks; a complete raw-data rerun remains optional research follow-up. Normal scene reproduction uses the pinned derived inputs.
- [x] Generate and inspect four fixed-view stills through v06. Preserve the v06 master, full/reduced GLBs, camera/material metadata, geometry check and snapshot hashes under `deliverables/iterations/v06/`.
- [x] Correct the inward-facing cube normals found in the earlier clean checkout. The v06 fresh generation/export and outward-volume checks pass; retain the original failure and subsequent correction in [fresh source verification](fresh-checkout-verification.md).
- [x] Replace the unsupported uniform northern forest band with the bounded lidar ground grid and 102 eligible canopy-envelope placements. Reproduce the constraints, verify placement heights, and retain uncertainty about trunk location, species and context beyond the aerial.
- [x] Prepare v07 CC0 texture/HDRI acquisition with checksums, the material-quality module, visual-finish module and revised original vehicle assets. Node/packing, isolated asset checks and integrated v07c static inspection passed; material/detail fidelity limitations remain.
- [x] Inspect repeated v07 probes and the clean frontage build. Correct the largest visible discrepancies in glazing, tree scale, fascia, lettering and material tone; preserve rejected studies and bounded findings.
- [x] Correct the low entrance return after full-resolution close-view inspection. The hidden lower-right aerial pick is superseded by a continuous photographed header; all four integrated v07c views were subsequently inspected.
- [x] Replace distant per-belt terrain shelves with a continuous regional DEM; flatten pond water to a documented lidar-derived level; correct overlapping entrance bays and access paint crossing the apron. Individual previews and bounded geometry checks pass.
- [x] Render and inspect all four final integrated v07c views from clean source `e29ad4b9`, including independent overview inspection. M2/M3 static inspection is complete; [the current record](fresh-checkout-v07c.md) preserves exact artifact hashes and limitations.

## P1 • environment and delivery

- [x] Implement pavement, curbs, islands, accessible bays, signage, vegetation and generic vehicles with evidence/provenance notes. Detailed resemblance and surface treatment remain open above.
- [ ] Refine roof equipment, facade depth, materials and small features where the reviewed views show discrepancies; preserve uncertainty for weakly evidenced rear/service areas.
- [x] Save the fixed cameras and generate the editable master and GLB.
- [x] Check the local viewer at `5bf2a27`: lint, clean npm dependency installation, production build, orbit/walk navigation, visible walk controls, rotated exterior footprints and saved-view selection. Offline installation used an existing package cache.
- [x] Inspect the refreshed v07 comparison gallery: current/reference pair, wipe movement, version selection, attribution and six preserved iterations. All 58 local links/assets resolve and current/history image hashes match; three reference caches pass their pinned hashes.
- [x] Refresh the v07c local viewer and inspect all four saved views, walking/reset, material fallbacks, stills/comparisons and fullscreen behavior. All 12 final payload files passed packaging; the bounded interface record is preserved alongside the subsequent final-movie check.
- [x] Inspect the final movie in the rebuilt local viewer. The six-second 1280 × 720 movie loaded with ready state 4 and no video or browser-log error; the production build passed. Private deployment remains separate below.
- [x] Preserve the v05 preliminary opening motion sample and its bounded engineering diagnostics. It does not approve later scene revisions or full-path playback quality.
- [x] Inspect the v07c 24-frame middle sample (61–84) at 1280 × 720 / 24 fps / 16 Cycles samples, plus endpoints 1/144. Accepted for full-film rendering at 23:46:49 UTC on September 7, 2026 after encoded playback and native image/crop inspection; mild foliage and roof texture variation remains. [The acceptance receipt](../research/v07c-motion-sample-review.json) binds the exact evidence. V06 motion was deliberately not run because its reviewed synthetic surfaces prompted v07.
- [x] Inspect and accept the full film with documented limits. All 144 frames finished at 01:41:05 UTC on September 8, 2026; encoding, complete decode, actual normal/fullscreen playback and independent image review passed. [Acceptance](../research/v07c-cinematic-review.json) was recorded at 01:55:53 UTC; fine-detail variation and scenery/material limitations remain.
- [x] Verify a clean v06 source archive: generate the master and both GLBs, preserve full master foliage, match camera/material baselines and all 102 canopy placements, and pass the corrected geometry checker. Retain the independent top-rounding threshold correction and original receipts.
- [x] Verify the actual release candidate after extraction: all 202 manifest files, complete runtime payload and original source/asset/review bindings passed. Fresh cached npm installation and the extracted production build succeeded; original payload bytes remained unchanged. See [delivery verification](delivery-verification.md).
- [ ] Publish and verify the owner-only private viewer after final integration and the user's required separate approval. No upload or deployment has occurred; registration of the private site is not publication.
- [x] Package source, derived inputs, native scenes, exports, accepted stills/video, complete viewer payload, gallery and accuracy records with a verified SHA-256 manifest. The final archive sidecars identify its exact clean source and bytes.

## GitHub project

- [x] Create the [private repository](https://github.com/mknutso-2/protolabs-campus-reconstruction) and prioritized issues; [PR #7](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/7) and [PR #8](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/8) are merged. Authenticated connector mirroring records equal source trees.
- Final v07 source and delivery integration are tracked in [PR #9](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/9), with exact source-tree comparison to main. Normal Git CLI authentication/history reconciliation is documented; connector mirroring preserves the source contents.

## P2 • later fidelity gaps

- [ ] More recent, dated ground views of every elevation.
- [ ] Accurate roof equipment, signage typography and mechanical layout.
- [ ] Surveyed curb elevations and drainage.
- [ ] Optional future UE5 import and performance evaluation on appropriate hardware; the evaluated and selected current walkthrough uses the browser.
- [ ] Optional complete reacquisition/reprocessing of the 174 MB raw-research pipeline, separate from the verified scene build using committed derived evidence.

Static inspection and delivery checks do not close the remaining visual-quality work in GitHub issues #2 and #3. See [brief.md](brief.md) for the acceptance gates, [current static verification](fresh-checkout-v07c.md) for completed checks, and the [accuracy summary](accuracy-summary.md) and [long visual record](visual-accuracy.md) for retained fidelity limits and historical corrections.
