# Vehicle asset revision v07

`scripts/vehicles.py` remains an original procedural generator, licensed under the existing [MIT license](VEHICLES-LICENSE.txt). No downloaded vehicle geometry, photograph texture, manufacturer badge, identifiable registration plate, or specific vehicle design is included. These are generic sedan and compact SUV scene objects; they do not reconstruct vehicles known to occupy the headquarters.

## Visible changes

The body now uses a densely sampled smooth loft with a crowned hood and tapered bumpers. Boolean cuts make actual wheel apertures through the body instead of placing wheels against an uninterrupted slab. Rounded cabin edges, gently curved windshield/side-window surfaces, thin closed glazing, and a shallow roof crown soften the previous straight-edged silhouette.

Tires use 48-sided rounded profiles with recessed alloy lips, split spokes, brake-disc layers, hubs, and individual fasteners. Paint has a clearcoat layer; paint swatches are interpreted as sRGB and converted to linear shader values. Glass and rubber are substantially darker than the earlier unconverted values. All geometry is unbranded. Significantly denser mesh geometry improves medium-distance silhouettes; it does not establish close-up automotive realism.

The entry point is unchanged: `create_vehicle_asset(name, color=(.22,.28,.33), variant='sedan')`. It returns one joined mesh in metres, +Y forward, with minimum Z=0. `suv` and `compact_suv` select the taller variant. Modifiers are applied, unrelated scene objects are preserved, and linked instances may reuse the returned mesh.

## Isolated validation

Blender 4.2.9 LTS created and exported both variants to GLB in an isolated scene. The checks verified finite coordinates, applied modifiers, a single returned mesh, preservation of an unrelated sentinel object, ground at Z=0, no boundary/nonmanifold edges, and positive signed volume for every connected component. Counts and the generator hash are retained in [vehicle asset validation](../research/vehicle-asset-validation.json).

| Variant | Triangles | Dimensions including mirrors and plates |
| --- | ---: | --- |
| Sedan | 20,428 | 2.238 × 4.6585 × 1.552 m |
| Compact SUV | 21,698 | 2.238 × 4.6585 × 1.848 m |

Both variants stay below the 30,000-triangle limit. A 1000 × 650 isolated Cycles preview at 24 samples was inspected: the body, glazing and wheel clearance are improved, while close-up vehicle design remains simplified. These checks verify asset construction/export and one asset preview, not the full scene, browser performance, or a cinematic. The main campus still requires a regenerated scene and fresh visual inspection after integration.

## Placement and source limitations

The [official headquarters aerial](https://www.protolabs.com/media/s4dignhf/hq-drone.jpg) shows an empty foreground lot. Repeated rows of white and orange vehicles in the earlier reconstruction therefore reduced resemblance. For the reference-matched image, keep the visible foreground empty. Any cars included elsewhere are an inferred occupancy state; vary their spacing, orientation, body type, and restrained neutral paint colors without implying current or historical ownership. Vehicle placement is controlled by the scene generator, not this module.

A limited CC0 asset search considered the original publisher listings for [GGBotNet's PSX cars](https://opengameart.org/content/psx-style-cars), [Kenney's Car Kit](https://opengameart.org/content/car-kit), and [Creomoto's generic car](https://opengameart.org/content/car-0). The first two explicitly target low-poly game aesthetics. The Creomoto listing offers a generic model, but its suitability was not established by an asset inspection. None of these assets was downloaded or incorporated, so their licenses do not apply to this original generated geometry. This record does not claim that a comprehensive search found no suitable licensed alternative.
