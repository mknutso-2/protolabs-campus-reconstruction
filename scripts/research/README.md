# Reproduce headquarters geospatial evidence

This folder is ready to copy to `scripts/research/` in the project. It retrieves two bounded public lidar tiles and georeferenced reference data, then reproduces `terrain_grid.json` and `lidar_roof_constraints.json`. It requires no cloud account or Blender installation.

## Setup and run

From the repository root, using Python 3.12:

```bash
python3.12 -m venv .venv-research
.venv-research/bin/python -m pip install -r scripts/research/requirements.txt
.venv-research/bin/python scripts/research/acquire.py --raw-dir data/research/raw --dry-run
.venv-research/bin/python scripts/research/acquire.py --raw-dir data/research/raw --include-reference-photos
.venv-research/bin/python scripts/research/process.py --raw-dir data/research/raw --output-dir data/research/derived
```

The optional `--include-reference-photos` flag retrieves the official Protolabs drone and 2024 exterior images. The orthophoto, parcels, OSM context and two LAZ tiles are always retrieved. The two LAZ files total 174,260,883 bytes, approximately 166.2MiB; each download is hard-limited to 149MB. No statewide raster or point-cloud product is downloaded. Processing reads at most 1 million raw lidar points per input chunk and keeps bounded campus ground/roof windows in memory. Expect several hundred megabytes of working memory and processing time that depends on hardware.

The acquisition script reuses existing files and validates immutable source hashes. `--overwrite` explicitly refetches a source; a mismatch with a recorded static SHA256 stops acquisition and preserves the previous completed file. Failed partial downloads are removed. The acquisition receipt records exact successful retrieval times, sizes and hashes.

## Output conventions

`terrain_grid.json` contains 85 x-values and 79 y-values on a 5 m grid spanning local x=-180..240 and y=-170..220m. Heights are `z[y_index][x_index]`, **NAVD88 GEOID18 minus303.6m**. Only LAS class 2 ground returns contribute to the terrain; missing bins are filled with nearest measured ground before Gaussian smoothing sigma 0.65cells. `missing_ground_return_bins` explicitly flags building-interior and uncovered bins. This interpolation is not a surveyed interior floor height.

`lidar_roof_constraints.json` contains simplified 0.25 m lidar raster roof projections and fitted plane equations for the folded ribbon and white wing. Plane equations return **absolute NAVD88 metres**; subtract 303.6 before constructing geometry in the scene. Roof projections are not wall footprint surveys.

The local horizontal origin is UTM (447671.875064,4984591.836461), derived from longitude -93.664082, latitude 45.0128453. x=east, y=north. Lidar is NAD83(2011)/UTM15N EPSG 6344; county aerial is NAD83/UTM15N EPSG 26915. Their common numeric local coordinates retain potential submeter datum reconciliation uncertainty.

`campus_parcels.geojson` records the official Protolabs-owned 7.00 acre HQ parcel and local coordinates. Neighboring parking and wetland properties must not be described as confirmed Protolabs ownership. OSM's erroneous 5840 building number does not override the official 5540 address. OSM's approximate footprint is secondary evidence because it differs from lidar roof projection by several metres.

## Evidence dates, attribution and rights

`sources.json` records exact URLs, dates, request parameters, attributions and byte limits. `SHA256SUMS.txt` fingerprints the original 2026-09-07 snapshot. Static USGS LAZ and official company image hashes are enforced. County/OSM service serialization or contents can change; their original hashes are recorded as `observed_sha256` and new acquisitions produce a separate receipt. OSM requests the historical 2026-09-07T16:48:50Z snapshot, although the JSON wrapper may differ.

- Lidar: USGS 3DEP MN_CentralMissRiver_4_B22, spring 2022, published 2023-09-14. Federal public lidar; retain USGS/Woolpert/NV5/MnGeo attribution.
- Orthophoto: Hennepin County/Nearmap Spring 2026 six-inch imagery. It is a research comparison reference; public visibility does **not** establish redistribution rights or a texture-material license.
- Parcels: Hennepin County GIS, monthly compilation, acquired 2026-09-07. Not a legal survey.
- OSM: © OpenStreetMap contributors, ODbL 1.0.
- Optional official photographs: Proto Labs, Inc., public official location page. Exterior filename specifies 2024; wider drone image is undated. Redistribution license is not established.

## Keep raw files out of Git

Commit scripts, the source manifest, dependency list and small derived JSON. Merge `.gitignore.fragment` into the repository's root ignore rules. Raw LAZ/JPEG/API responses, virtual environments, package caches, temporary `.part` files and numpy intermediates are fetched or regenerated. `acquisition_receipt.json` should accompany the locally acquired evidence, and can be retained in an archived delivery record if required.

## Validation performed

The packaged acquisition script passed a no-network `--dry-run`; all Python scripts compiled; processing dependencies imported; immutable raw sources and optional reference images matched their recorded SHA256s. The processing functions were adapted directly from the scripts that produced the delivered constraints; the 174 MB input pipeline was not rerun just to validate packaging. `expected_outputs.json` records the existing delivered geometric summaries for a fresh-run comparison. File hashes of generated JSON may differ because the repo-ready script adds clearer descriptions and formatting; compare numeric coordinates, elevations and dimensions.
