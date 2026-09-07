# Visual accuracy record

Reviewed 7 September 2026 against the preserved v04 aerial and the current entrance-detail, arrival and campus-overview stills. This record describes the images actually inspected, not a projected final quality level. The gallery manifest records the reviewed aerial's hash and dimensions. v04 is a historical review state, not a final-quality designation. The latest working v05 is shown separately when available and remains pending fresh full-image inspection; no v05 quality pass is implied. The v04 entrance, arrival and campus-overview stills were copied into `deliverables/iterations/v04/stills/` before later renders could replace the working files.

The headquarters is recognizable in the current reconstruction. The low-rise composition, darker left block, white glazed right wing, silver sloping entrance roof, white fan braces, flagpole and monument sign carry its identity. The work remains a schematic architectural visualization. It is not photographically equivalent to the official aerial and has not been validated as a surveyed as-built model.

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
| v04 | Current aerial snapshot with fitted camera, denser crowns, revised glazing and roof treatment | Recognizable structure; photographic and detailed geometry limitations remain as listed above |

Every iteration retains its own original image and saved camera file. The comparison generator preserves v04 on first execution and leaves existing snapshots unchanged on later builds. When the working aerial hash differs from v04, the gallery adds a v05 latest entry marked pending review; the reviewed v04 stills remain visible below it. `--refresh-v04` is an explicit replacement operation for a deliberate new current snapshot; v01–v03 are not changed. The gallery also links the latest working aerial separately, so later renders are not silently represented as the preserved review state.

## Quality milestones still needed before stronger claims

- Independently check a second photograph with a fitted camera and explicit residuals. One selected-landmark aerial fit is insufficient to validate the full facade and canopy geometry.
- Resolve close-up entrance proportions and member/connection details against measured elevations or a more complete, dated photo set.
- Improve material, glazing, pavement and landscape response under lighting matched to a reference; inspect the resulting full-resolution frame again.
- Verify rear/service elevations and roof equipment where source coverage is currently weak.
- Inspect a completed delivery-resolution motion sample, including foliage aliasing, shadows, camera motion and frame continuity. This static review does not certify motion quality or approve a cinematic render.
- Validate the exported interactive scene separately for navigation, visibility, asset completeness and performance. This gallery does not exercise the 3D runtime.

Creating or exporting files is not evidence that these visual milestones passed. The present assessment should remain “recognizable exterior reconstruction with documented approximations,” not “photoreal,” “survey accurate,” or an exact digital twin.

## Reproducing this comparison

Run `python3 scripts/build_comparison.py` from a checkout containing the reference cache and rendered images. Open `deliverables/comparison/index.html` directly in a browser. The page requires no server, external fonts, network fetches or third-party JavaScript. Source links work when online. `deliverables/comparison/manifest.json` records image hashes, sizes and camera-fit statistics. The gallery does not alter, recolor or retouch the source photographs or renders.
