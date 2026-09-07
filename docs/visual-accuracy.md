# Visual accuracy record

Updated 7 September 2026. The original detailed review below inspected the preserved v04 aerial and its three saved stills. A later review rejected the oversized continuous forest band in v05. The current v06 replaces that band using lidar-derived ground and canopy-envelope constraints, but its newly rendered images remain **pending full-image inspection** at this update. None of these version labels implies a photographic quality pass.

The comparison gallery reads the original v01–v05 snapshots without replacing them and presents v06 separately. Its manifest records image hashes, dimensions, the selected latest version, and explicit inspection status. By default the latest version is pending; `--reviewed-latest` may be used only after the aerial and all three latest stills have actually been inspected. That flag records inspection, not motion acceptance, engineering validity, or photographic equivalence.

The headquarters is recognizable in the reviewed v04 reconstruction. The low-rise composition, darker left block, white glazed right wing, silver sloping entrance roof, white fan braces, flagpole and monument sign carry its identity. The work remains a schematic architectural visualization. It is not photographically equivalent to the official aerial and has not been validated as a surveyed as-built model.

## Reference evidence and dates

- **Official wide aerial:** Proto Labs, Inc., [hq-drone.jpg](https://www.protolabs.com/media/s4dignhf/hq-drone.jpg). The photo is undated. Its photographic setup matches the official exterior file whose name includes “2024”; exact capture date is not independently established. The source is 1200 × 800 pixels.
- **Official exterior:** Proto Labs, Inc., [current headquarters image](https://www.protolabs.com/media/sj0nwkxv/hq_mp_exterior_2024.jpg), linked by the [locations page](https://www.protolabs.com/about-us/locations/). Filename year is not a verified capture timestamp.
- **Entrance close-up:** [Minneapolis / St. Paul Business Journal, 6 December 2018](https://www.bizjournals.com/twincities/news/2018/12/06/2018-business-of-manufacturing-proto-labs-inc.html). Exact photograph date and photographer were not independently verified. Historic green/blue lettering differs from the current branded interpretation.
- **Arrival photograph:** [Machine Design, 26 January 2024](https://www.machinedesign.com/automation-iiot/article/21281562/protolabs-qa-protolabs-rebranded-manufacturing-partner-network-expands-capabilities), image credited to Protolabs. Exact capture date is unknown; snow and dormant planting show a different season from the model.

All photographic references were retrieved on 7 September 2026. They remain attributed to their original owners. Public access does not establish a redistribution license. The architecture and geospatial ledgers retain the source URLs, acquisition notes and limitations. Images of Protolabs' separately listed Brooklyn Park building at 8500 Wyoming Avenue N were excluded as headquarters evidence.

## Camera alignment is separate from visual fidelity

The **reference_aerial** camera uses a nonlinear fit to eleven manually annotated 2D landmarks and corresponding 3D points. The saved fit reports weighted RMS **3.1687 pixels** and unweighted RMSE **7.8705 pixels** on the 1200 × 800 source. A partly obscured roof correspondence has about **19.95 pixels** residual and a reduced weight. These are selected-point reprojection statistics; they are not a whole-image similarity score, measured building tolerances, or proof that hidden geometry is correct.

The source photo may be cropped or lens-corrected. Its capture date differs from the public lidar dataset used for constraints. Manual point identification, weighting and occlusion add uncertainty. The current 1600 × 1067 render is close to the source aspect ratio. See `research/reference_drone_camera_fit.json` for the complete fit, residuals and assumptions, and `scene/cameras.json` for saved views.

**entrance_detail**, **arrival** and **campus_overview** are approximate presentation cameras. Their associated source filenames identify useful visual context, not successful photographic registration. The campus overview is oblique and should not be compared pixel-for-pixel with the county's top-down aerial. No claim of matched-camera accuracy is made for these three views.

## Visible resemblance in v04

The central roof now reads as the characteristic projecting sloping silver plane. White trusses and diagonal fan braces remain open in front of a triangular glazed enclosure, with dark supports and a projecting glass entrance below. This is a substantial improvement over the early oversized roof and later intersecting-panel treatment.

The major left/right massing division and window rhythms are apparent. Blue mullions and glazing divisions are more legible than in v02–v03. The parking, flagpole island, sign and facade planting place the building in a recognizable arrival setting. Dense procedural crowns improve the earlier sparse trees.

These observations support recognizable architecture and general site composition. They do not establish exact member sizes, all window counts, exact planting positions, or the condition of unseen elevations.

## Five largest remaining discrepancies

1. **Materials, exposure and lighting.** The official aerial is a sunset photograph with darker asphalt, richer brick color, soft atmospheric background and changing reflections. The current render is brighter daylight. Brick, painted panels, metal roof and pavement remain too uniform and clean, with limited weathering and fine surface variation. Lighting differences prevent meaningful direct color-error interpretation.
2. **Glazing and entrance finish.** The source has varied dark/blue reflections and relatively fine mullions. The model uses repeated saturated blue panes, simplified interior appearance and inferred framing. The entrance still clearly shows the structural motif, but exact vestibule width, glass-bay proportions, column sections, truss web layout and connection hardware have not been independently measured. Faceted columns, large uninterrupted panes and simplified door hardware remain visible at close range.
3. **Vegetation and distant environment.** v04's crowns are fuller, but their repeated procedural shapes, individual leaf cards and bright lighting still differ from photographed mature trees. The photograph's understory, mixed vegetation, continuous wooded horizon and nuanced grass edges are only approximated. Tree species, pruning, age, precise crown shape and seasonal state are inferred. The v04 model intentionally combines leaf-on planting with geospatial evidence of different dates.
4. **Pavement, parking and occupancy.** Curbs and islands are simplified polygonal traces. Stripe spacing, worn markings, accessible access aisles, gravel/rock beds and asphalt aging do not fully match the photograph. Generic repeated vehicles are scene dressing and do not reconstruct specific vehicles or operational occupancy. The official aerial shows an empty foreground lot. Approximate parking-row counts must not be presented as official capacity.
5. **Small features and hidden detail.** Sign lettering/scale, flag pattern and drape, hydrant, exterior lights, roof screens and exposed mechanical equipment remain simplified. No current dated ground-photo set covers every elevation. Rear/service geometry and hidden equipment remain less well evidenced than the main frontage. The campus overview exposes these simplifications more clearly than the fitted aerial.

## Preserved iteration record

| Iteration | Visible state retained | Limits |
| --- | --- | --- |
| v01 | Early building massing, roof, site surfaces and initial daylight render | Oversized roof impression, bright materials, ground discontinuities and no mature landscape |
| v02 | Revised surfaces, first procedural vegetation and site details | Sparse crowns, exaggerated facade relief and unresolved entrance roof treatment |
| v03 | Revised framing, generic parked vehicles and further building changes | Dark glazing, sparse foliage and visible material simplification |
| v04 | Preserved aerial and three stills with fitted camera, denser crowns, revised glazing and roof treatment | Historical reviewed state; recognizable structure with the limitations listed above |
| v05 | Preserved master, glTF export, aerial, three stills, cameras and one-second motion sample | Oversized continuous forest band rejected: it crosses pond/open ground and creates unsupported canopy massing |
| v06 | Current working revision with north-context lidar ground and 102 eligible canopy-envelope placements | Pending inspection of the new aerial and three stills; crown form/species, current tree state and northern candidates without aerial coverage remain uncertain |

Every preserved iteration retains its original aerial image and camera file; later versions also retain additional scene, still and motion artifacts where available. The gallery generator never creates, refreshes or overwrites an iteration snapshot. It discovers existing numbered snapshots, assigns the working image an explicit `--latest-version` (default `v06`), and rejects a latest label that collides with a preserved version. The former `--refresh-v04` replacement behavior has been removed. Generated HTML and its manifest are outputs; source code and measured input records are retained in Git without duplicating render binaries.

## v05 landscape rejected; v06 evidence revision pending

The v05 background used an oversized, continuous band of procedural trees. The 2026 orthophoto instead shows pond, open grass, reeds and scattered trees immediately north of headquarters. Filling that area with a uniform wooded wall creates a false silhouette and conceals the actual open setting. The v05 images and its one-second motion sample are preserved as the rejected state; encoding continuity or attractive framing does not accept its landscape.

V06 replaces the unsupported band with a north-context ground grid and **102 eligible canopy-envelope candidates** derived from one previously cached, checksum-verified 2022 USGS lidar tile. Ground comes from class 2 returns. Candidate heights and approximate widths come from filtered class 1 elevated returns; class 1 means unclassified and is not certified vegetation. Their centers locate envelope peaks rather than measured trunks. Sixty-five of 105 raw candidates fall within the cached 2026 aerial. Three small isolated candidates outside that coverage were excluded, leaving 102 eligible placements. The rest of the northern candidates have no aerial visual cross-check.

This is better-supported placement evidence, not proof of a faithful rendered landscape. Generic crown forms, foliage density, exact trunks, species, pruning and 2026 growth/removal remain inferred. The ground below this context is substantially lower than the entrance platform, so the generator uses each candidate's recorded base elevation and height rather than adding a uniform height above entrance grade. The approximately four-year date gap also prevents treating these as current measured tree heights.

See [north canopy evidence](canopy-evidence.md), [placement constraints](../research/north_context_canopy_constraints.json), [north ground grid](../research/north_context_ground_grid.json), and [procedural asset provenance](vegetation-provenance.md). New v06 views must be checked for silhouette, open-water/grass visibility, canopy scale, exposure, close entrance readability and any ground discontinuity before this pending state changes. The preliminary v05 motion check in [motion-review.md](motion-review.md) cannot accept the revised geometry.

## Quality milestones still needed before stronger claims

- Independently check a second photograph with a fitted camera and explicit residuals. One selected-landmark aerial fit is insufficient to validate the full facade and canopy geometry.
- Resolve close-up entrance proportions and member/connection details against measured elevations or a more complete, dated photo set.
- Improve material, glazing, pavement and landscape response under lighting matched to a reference; inspect the resulting full-resolution frame again.
- Verify rear/service elevations and roof equipment where source coverage is currently weak.
- Inspect a completed delivery-resolution motion sample, including foliage aliasing, shadows, camera motion and frame continuity. This static review does not certify motion quality or approve a cinematic render.
- Validate the exported interactive scene separately for navigation, visibility, asset completeness and performance. This gallery does not exercise the 3D runtime.

Creating or exporting files is not evidence that these visual milestones passed. The present assessment should remain “recognizable exterior reconstruction with documented approximations,” not “photoreal,” “survey accurate,” or an exact digital twin.

## Reproducing this comparison

Run `python3 scripts/build_comparison.py --latest-version v06` from a checkout containing the reference cache, existing iteration snapshots and current rendered images. This builds a gallery with v06 pending inspection. Only after inspecting the latest aerial and all three current stills, rebuild with `python3 scripts/build_comparison.py --latest-version v06 --reviewed-latest` to record that inspection. Use a new explicit version label for subsequent revisions. Open `deliverables/comparison/index.html` directly in a browser. The page requires no server, external fonts, network fetches or third-party JavaScript. Source links work when online. `deliverables/comparison/manifest.json` records image hashes, sizes and camera-fit statistics. The gallery does not alter, recolor or retouch the source photographs or renders.
