# Generic vehicle asset provenance

`vehicles.py` is an original procedural Blender Python asset generator authored for this reconstruction on 2026-09-07. Code and generated vehicle geometry are licensed under the MIT license in `VEHICLES-LICENSE.txt`.

Geometry is constructed from mathematical cross-section meshes and primitive rods/boxes. No downloaded geometry, photo textures, logos, manufacturer badges, real registration plates, or branded vehicle designs are included. Colors and materials are procedural. The vehicles are generic background scene objects rather than reconstructions of particular cars seen at the site.

The entry point `create_vehicle_asset(name, color=(.22,.28,.33), variant='sedan')` creates one joined mesh at the origin, in meters, with +Y forward and minimum Z=0. `variant='suv'` or `'compact_suv'` creates the taller version. Linked instances can share the returned object's mesh. Existing scene objects are preserved.

A single 900×700 preview render and numerical checks validate both variants. Exact triangle counts and bounds are recorded in `vehicles-validation.json`. Bounds include side mirrors and protruding plates. Vehicle body widths are approximately 1.85–1.90 meters.
