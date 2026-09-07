# Prioritized backlog

## P0 • evidence and visible resemblance

- [x] Verify public parcel ownership versus operational/visual context and record capture-date limitations. The confirmed headquarters parcel is 7.00 acres; neighboring context is separately identified. Public tax parcels are not a legal survey.
- [x] Acquire bounded lidar and public reference evidence; retain roof/terrain constraints, source ledgers, dates, coordinate systems, processing methods and uncertainty. Packaged raw-processing scripts have dry-run/import/hash checks; a full fresh packaged rerun remains under delivery verification.
- [x] Generate and inspect the four v04 fixed-view stills, preserving earlier iterations and recording visible discrepancies.
- [ ] Verify the v05 fix for inward-facing cube normals discovered by a fresh-checkout check. Rebuild the master and GLB, inspect corrected faces/reflections/shadows in stills and the viewer, and retain the before/after evidence.
- [ ] Continue matching entrance canopy, sloping roof, facade/window rhythm and glazing depth against attributed references. M2 visual acceptance remains open.
- [ ] Inspect the expanded wooded background and landscape transitions from all saved views. Correct the largest visible discrepancies before accepting M3 campus-wide consistency.

## P1 • environment and delivery

- [x] Implement pavement, curbs, islands, accessible bays, signage, vegetation and generic vehicles with evidence/provenance notes. Detailed resemblance and surface treatment remain open above.
- [ ] Refine roof equipment, facade depth, materials and small features where the reviewed views show discrepancies; preserve uncertainty for weakly evidenced rear/service areas.
- [x] Save the fixed cameras and generate the editable master and GLB.
- [x] Check baseline local interactive orbit/walk navigation and saved-view selection.
- [ ] Finish and inspect the standalone reference gallery, including attribution, saved transforms, preserved versions and the current accuracy report.
- [ ] Refresh viewer assets after the v05 correction and check visibility, navigation, material fallback, reference assets and saved-view correspondence.
- [ ] Complete and inspect the opening 24-frame motion sample at the current 1280 × 720 / 24 fps delivery target. Check representative later positions, leaf edges, shadows, reflections, continuity and camera clipping; correct failures before the six-second cinematic.
- [ ] Render, inspect and encode the full cinematic only after the sample gate passes. Keep its completion status explicit.
- [ ] Repeat the complete fresh-source workflow after the normals correction. The earlier check found a real defect; full reproduction and delivery acceptance have not passed.
- [ ] Package source revision, derived-input identifiers, master scene, GLB, accepted stills/video, gallery and accuracy report in a versioned archive with a verified SHA-256 manifest.

## GitHub project

- [x] Create the [private repository](https://github.com/mknutso-2/protolabs-campus-reconstruction), prioritized issues and [draft PR #7](https://github.com/mknutso-2/protolabs-campus-reconstruction/pull/7). Authenticated connector mirroring is working and records equal source trees.
- [ ] Keep substantial source updates and their visual-check notes synchronized with the draft PR. Normal Git CLI authentication/history reconciliation is documented; it does not prevent the current connector workflow.

## P2 • later fidelity gaps

- [ ] More recent, dated ground views of every elevation.
- [ ] Accurate roof equipment, signage typography and mechanical layout.
- [ ] Surveyed curb elevations and drainage.
- [ ] Production UE5 import and performance evaluation on appropriate hardware.

Completion of evidence acquisition or baseline navigation does not close the visual-quality work in GitHub issues #2 and #3. See [brief.md](brief.md) for the current acceptance gates and [visual-accuracy.md](visual-accuracy.md) for the reviewed v04 limitations.
