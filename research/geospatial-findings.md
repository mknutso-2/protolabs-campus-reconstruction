# Geospatial findings, acquired September 7, 2026

The headquarters address is **5540 Pioneer Creek Drive, Maple Plain, MN 55359**, confirmed by the company and a 2026 SEC filing. The county tax parcel is **2411824320013**, owned by PROTO LABS INC, 7.00 acres. OSM incorrectly calls the building 5840; the geocoder street point is south of the actual building. The headquarters building is near 45.01315 N, -93.66367 W.

`campus_aerial_measured.jpg` shows the current county Spring 2026 orthophoto with the confirmed ownership parcel in yellow and OSM geometry in cyan. The large parking field on the far east extends into neighboring North Shore Gymnastics parcels. West and north neighbors are also separately owned. These surroundings establish the scene but must not be claimed as Protolabs-owned campus.

## Coordinate convention

Every local geometry uses x=east, y=north, units metres, origin NAD83 UTM15N (447671.875064, 4984591.836461), corresponding to longitude -93.664082, latitude45.0128453. This is the OSM southwest brick corner, not an authoritative surveyed corner. For a renderer whose z=0 is near the public entrance, subtract **303.0m** from measured NAVD88 heights.

Lidar CRS is NAD83(2011) UTM15N (EPSG6344), versus the aerial's EPSG26915 NAD83. We retained common numeric UTM coordinates for scene construction; do not claim submeter alignment without resolving datum differences.

## Critical geometry findings

- Main brick block roof: approximately x3.5..61.0, y1.25..49.75, or **57.5×48.5m**. OSM has several-metre offsets and should be superseded by lidar for roof geometry.
- Main gravel roof slopes gently from NAVD88 310.17m at front/back edges to310.65m around mid-depth. It is not perfectly flat.
- Rooftop mechanical room: x10..25, y18..33, top314.25m. Smaller upper tower x55..61, y40..49.5, top314.9m.
- Northeast white wing is rotated about+27.7° in plan, with corners near (69,51),(92.5,62.5),(105.25,37.5),(78.25,24.25). Its roof is ~308.1..308.4m.
- The signature white feature is a **broad, transversely sloped and bent roof ribbon**, not a freestanding thin wall. High western edge runs (60.75,53.75) to(60.75,27.5) then to(78.25,-7.5). Low eastern edge runs approximately x69 in the north branch, bending southeast to the same south tip. This is visible in aerial and lidar; the exact facade underside/edge profile must come from street photographs.
- Ribbon northern plane: z=-0.585359224*x+0.0031214945*y+348.591201.
- Ribbon southern plane: z=-0.521280975*x-0.257179186*y+351.963817.
- **Terrain is strongly sloped.** Public entrance and southeast paving~303.6m; main block southwest ground302.3m, west side298.8m, northwest297.95m, northeast rear298.64m. A flat ground plane misrepresents building height and west/rear lower stories. These are 2022 measured ground returns, not estimated contours.

## Useful files

- `source_ledger.json`: source URLs, acquisition/source dates, confidence, rights, observations and conflicts.
- `lidar_roof_constraints.json`: extracted roof projection polygons and robust fitted roof planes.
- `terrain_scene_grid.json`: 5m terrain mesh (70×56) with local x/y/z and interpolated flags.
- `terrain_1m_navd88.npy`: underlying 1m grid in absolute NAVD88 metres.
- `lidar_hq_height_map.png`: easy visual roof-height comparison, annotated local axes.
- `hq_surface_grid_2m.json`: roof and surface elevations in 2m bins.
- `site_layout_traces.json`: approximate road, pond and parking row traces from 2026 aerial.
- `hq_footprint_local.json`: original OSM-derived footprint, retained as provenance, **not the best roof geometry**.
- `campus_parcels.geojson`: confirmed owned HQ parcel, with local metric coordinate appendix.
- `campus_lidar_clip.npz`: 4.8 million local x/y/absolutez/classification records, ~350×280m, 2022.
- `USGS_LPC_MN_CentralMissRiver_B22_4475_49845.laz`: full original500×500m tile, 74MB, 13.3million points,30ppsm nominal project density.
- `aerial_2026.jpg` and `aerial_2026_export.json`: original reference and exact georeferencing.

## Reproduction and licensing

`acquire_site.py` uses the Python standard library to download bounded public sources; the latest raw GIS layers may change since this snapshot. `SHA256SUMS.txt` identifies the acquisition used here. Processing uses numpy, scipy, shapely, rasterio, pyproj, laspy[lazrs] and Pillow. `analyze_site.py`, `derive_roofs.py`, and `package_findings.py` generate derivative constraints and diagrams from the local clip.

The lidar is public USGS data. OSM geometry requires OpenStreetMap attribution under ODbL. County aerial images identify Nearmap as supplier: public availability does not establish redistribution rights. Keep imagery as attributed research comparison reference and do not claim it as a CC material or general texture asset. The original LAZ, numpy caches, and deps directory should be excluded from Git or fetched via acquisition script. Small geometric JSON and provenance scripts are suitable for version control.

## Limits

2026 aerial matches the broad 2022 roof arrangement. Lidar does not validate current window divisions, signage, brick detail, roof fascia thickness, entrances, or interiors. The source sampling and polygon simplification were designed to constrain an architectural model, not to produce a survey or a direct photogrammetric mesh. Dense data alone does not establish visual quality.

## Extended requested terrain and flagpole refinement

`terrain_grid.json` covers x=-180..240,y=-170..220, 5m spacing, arrays x/y and z[y][x]. Its datum is **NAVD88-303.6**, per renderer request; this overrides the older303.0 relative datum in terrain_scene_grid.json. A second100MB USGS tile4475_49840 supplies southern coverage. Only a narrow8m western edge falls outside the two tiles and uses nearest-ground extension. Missing-ground bins under buildings are explicitly flagged.

The American flagpole is strongly constrained at local(84.20,-5.80), ground303.33m, top316.18m, hence height12.85m. A0.12m cylinder includes returns at ground, middle310.84, and tip316.18; adjacent flag-like returns extend southwest. The frontage monument location is(94.39,-27.81), visibly just east of main entrance drive. Details are in site_layout_traces.json.

Processing order after acquire_site.py: prepare_geometry.py, analyze_site.py, derive_roofs.py, build_requested_terrain.py. package_findings.py generates initial manual traces/ledger; the delivered source_ledger.json and site_layout_traces.json include subsequent flagpole and south tile refinements, so preserve those delivered files rather than overwriting them with the initial packaging script.
