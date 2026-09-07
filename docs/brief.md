# Project brief

## Objective
Recognizable exterior reconstruction with architectural visualization quality, grounded in public aerial imagery, photographs and geospatial data. Editable Blender master, interactive walkthrough, fixed-view stills, cinematic flythrough, comparison gallery, reproducible private GitHub project.

## Acceptance gates
- [x] M0: inspect environment; dedicated Git repository; verify headquarters address.
- [ ] M1: site extent/footprints and source ledger; one reference-matched frontage.
- [ ] M2: daylight geometry and material comparison; fix major visible errors.
- [ ] M3: extend consistent detail across evidenced campus and landscape.
- [ ] M4: interactive exterior inspection and saved camera views.
- [ ] M5: delivery-resolution motion sample inspected; cinematic generated if sample passes.
- [ ] M6: fresh-checkout instructions, provenance, candid accuracy report and versioned delivery.

## Rules
Dimensions from GIS/lidar are measured only to their source precision. Photo interpretation is visually confirmed where justified. Inferred details must remain flagged. No invented accurate interiors. Preserve reference attribution, dates, camera transforms and earlier iterations. Render counts and passing exports are not fidelity evidence.

## Runtime evaluation
Host: Intel i7-3610QM, 8 GB RAM, Intel integrated graphics / NVIDIA GTX 660M. Blender 4.2 LTS portable CPU render chosen. UE5 is evaluated separately: current Linux recommendation is 32 GB RAM and a modern dedicated GPU with 8 GB VRAM. Local UE5 high-quality walkthrough is not a reasonable production target on this host; a portable glTF viewer will provide exterior inspection, with Blender as master.
