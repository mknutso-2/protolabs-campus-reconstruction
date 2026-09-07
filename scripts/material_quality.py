"""CC0 scanned surface response and a reference-oriented low-sun environment.

Ordinary Python: python scripts/material_quality.py --download
Blender integration, after scene/world setup and before export_materials/pack/save:
    from material_quality import apply_material_quality
    apply_material_quality(ROOT)

No geometry, object placement, camera transform, render settings or file saving is
performed. Ground/landscape in any non-pure HDRI is explicitly unregistered context.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_SUN_AZIMUTH_XY_DEG = 156.05796697531812
ENVIRONMENTS = {
    'qwantani_sunset_puresky': {'u': .6000498819563259, 'elevation': 6.083456677460177},
    'spruit_sunrise': {'u': .5993450028913411, 'elevation': 8.017500333041284},
}


def _manifest(root):
    return json.loads((Path(root) / 'research/material-assets.json').read_text())


def acquire_assets(root=ROOT, include_candidates=False):
    """Fetch only manifest URLs with size bounds and enforced SHA256; reuse good files."""
    root = Path(root)
    manifest = _manifest(root)
    directory = root / manifest['asset_directory']
    directory.mkdir(parents=True, exist_ok=True)
    receipts = []
    for asset in manifest['assets']:
        if asset.get('status') == 'rejected_candidate' and not include_candidates:
            continue
        for entry in asset['files']:
            target = directory / entry['filename']
            if target.exists():
                if hashlib.sha256(target.read_bytes()).hexdigest() != entry['sha256']:
                    raise ValueError(f'Preserved existing file with wrong SHA256: {target}')
                receipts.append({'filename': entry['filename'], 'status': 'verified existing'})
                continue
            temporary = target.with_suffix(target.suffix + '.part')
            try:
                req = urllib.request.Request(entry['url'], headers={
                    'User-Agent': 'ProtolabsCampusReconstruction/1.0 (bounded CC0 material acquisition)'})
                limit = min(manifest['max_individual_download_bytes'], entry['bytes'] + 1)
                with urllib.request.urlopen(req, timeout=90) as response:
                    data = response.read(limit + 1)
                if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
                    raise ValueError(f'Size or SHA256 mismatch: {entry["filename"]}')
                temporary.write_bytes(data)
                temporary.replace(target)
                receipts.append({'filename': entry['filename'], 'status': 'downloaded and verified'})
            finally:
                if temporary.exists():
                    temporary.unlink()
    return receipts


def _node(tree, kind, name):
    node = tree.nodes.new(kind)
    node.name = name
    node.label = name
    return node


def _image(root, asset, role):
    import bpy
    entry = next(f for f in asset['files'] if f['role'] == role)
    path = Path(root) / 'research/material-assets' / entry['filename']
    if not path.is_file():
        raise FileNotFoundError(f'{path} is missing; run python scripts/material_quality.py --download')
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
        raise ValueError(f'Material asset SHA256 mismatch: {path}')
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = 'sRGB' if role == 'Diffuse' else 'Non-Color'
    image.pack()
    return image, entry


def _surface(root, material_name, asset, albedo, tile_m, bump_m, macro_amount=.10):
    import bpy
    material = bpy.data.materials.get(material_name)
    if material is None:
        raise KeyError(f'Required reconstruction material missing: {material_name}')
    material.use_nodes = True
    tree = material.node_tree
    tree.nodes.clear()
    output = _node(tree, 'ShaderNodeOutputMaterial', 'Material Output')
    bsdf = _node(tree, 'ShaderNodeBsdfPrincipled', 'Principled BSDF')
    bsdf.inputs['Metallic'].default_value = 0
    bsdf.inputs['IOR'].default_value = 1.5
    tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    material.diffuse_color = (*albedo, 1)
    bsdf.inputs['Base Color'].default_value = (*albedo, 1)
    geometry = _node(tree, 'ShaderNodeNewGeometry', 'World metres')
    scale = _node(tree, 'ShaderNodeVectorMath', f'{tile_m:g} metre scan repeat')
    scale.operation = 'SCALE'
    scale.inputs['Scale'].default_value = 1 / tile_m
    tree.links.new(geometry.outputs['Position'], scale.inputs[0])
    images = {}
    entries = {}
    for role in ('Diffuse', 'Rough', 'Displacement'):
        image, entry = _image(root, asset, role)
        tex = _node(tree, 'ShaderNodeTexImage', f'CC0 {asset["asset_id"]} {role}')
        tex.image = image
        tex.projection = 'BOX'
        tex.projection_blend = .18
        tex.interpolation = 'Linear'
        tree.links.new(scale.outputs['Vector'], tex.inputs['Vector'])
        images[role] = tex
        entries[role] = entry
    tint = _node(tree, 'ShaderNodeMixRGB', 'Preserve scan contrast; normalize mean albedo')
    tint.blend_type = 'MULTIPLY'
    tint.inputs[0].default_value = 1
    mean = entries['Diffuse']['diffuse_mean_linear_rgb']
    tint.inputs[2].default_value = (*(albedo[i] / max(mean[i], .001) for i in range(3)), 1)
    tree.links.new(images['Diffuse'].outputs['Color'], tint.inputs[1])
    macro = _node(tree, 'ShaderNodeTexNoise', 'Restrained broad weathering')
    macro.inputs['Scale'].default_value = .12
    macro.inputs['Detail'].default_value = 2
    tree.links.new(geometry.outputs['Position'], macro.inputs['Vector'])
    ramp = _node(tree, 'ShaderNodeValToRGB', 'Broad albedo range')
    ramp.color_ramp.elements[0].color = (*(1 - macro_amount for _ in range(3)), 1)
    ramp.color_ramp.elements[1].color = (*(1 + macro_amount for _ in range(3)), 1)
    tree.links.new(macro.outputs['Fac'], ramp.inputs['Fac'])
    variation = _node(tree, 'ShaderNodeMixRGB', 'Scan times restrained broad variation')
    variation.blend_type = 'MULTIPLY'
    variation.inputs[0].default_value = 1
    tree.links.new(tint.outputs[0], variation.inputs[1])
    tree.links.new(ramp.outputs[0], variation.inputs[2])
    tree.links.new(variation.outputs[0], bsdf.inputs['Base Color'])
    roughness = _node(tree, 'ShaderNodeMapRange', 'Dry surface roughness 0.66 to 0.97')
    roughness.inputs['To Min'].default_value = .66
    roughness.inputs['To Max'].default_value = .97
    roughness.clamp = True
    tree.links.new(images['Rough'].outputs['Color'], roughness.inputs['Value'])
    tree.links.new(roughness.outputs['Result'], bsdf.inputs['Roughness'])
    bump = _node(tree, 'ShaderNodeBump', 'Small-scale relief; no silhouette displacement')
    bump.inputs['Distance'].default_value = bump_m
    bump.inputs['Strength'].default_value = .5
    tree.links.new(images['Displacement'].outputs['Color'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    material['Surface evidence'] = 'CC0 scan proxy, colour interpreted from reference; not an on-site material scan'
    material['CC0 source'] = asset['source_page']
    material['Scan repeat metres'] = tile_m
    return material


def _plain_response(name, colour_srgb, roughness, metallic=0, transmission=0, ior=1.5):
    import bpy
    material = bpy.data.materials[name]
    colour = tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in colour_srgb)
    material.use_nodes = True
    tree = material.node_tree
    tree.nodes.clear()
    output = _node(tree, 'ShaderNodeOutputMaterial', 'Material Output')
    bsdf = _node(tree, 'ShaderNodeBsdfPrincipled', 'Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*colour, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Transmission Weight'].default_value = transmission
    bsdf.inputs['IOR'].default_value = ior
    tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    material.diffuse_color = (*colour, 1)
    return material, bsdf


def _parking_paint():
    material, bsdf = _plain_response('Faded parking paint', (.68, .675, .625), .92)
    tree = material.node_tree
    geometry = _node(tree, 'ShaderNodeNewGeometry', 'Paint wear in world metres')
    noise = _node(tree, 'ShaderNodeTexNoise', 'Uneven existing-line wear')
    noise.inputs['Scale'].default_value = 8
    noise.inputs['Detail'].default_value = 2
    tree.links.new(geometry.outputs['Position'], noise.inputs['Vector'])
    coverage = _node(tree, 'ShaderNodeValToRGB', 'Mostly intact, softly worn paint')
    coverage.color_ramp.elements[0].position = .31
    coverage.color_ramp.elements[0].color = (0, 0, 0, 1)
    coverage.color_ramp.elements[1].position = .48
    coverage.color_ramp.elements[1].color = (1, 1, 1, 1)
    tree.links.new(noise.outputs['Fac'], coverage.inputs[0])
    transparent = _node(tree, 'ShaderNodeBsdfTransparent', 'Worn-through paint reveals pavement')
    mix = _node(tree, 'ShaderNodeMixShader', 'Existing stripe with patchy wear')
    tree.links.new(coverage.outputs[0], mix.inputs[0])
    tree.links.new(transparent.outputs[0], mix.inputs[1])
    tree.links.new(bsdf.outputs[0], mix.inputs[2])
    tree.links.new(mix.outputs[0], tree.nodes['Material Output'].inputs['Surface'])
    material['Wear evidence'] = 'Illustrative wear only; existing painted-line geometry unchanged'


def _environment(root, asset, strength, yaw_offset_deg=0):
    import bpy
    info = ENVIRONMENTS[asset['asset_id']]
    image, _ = _image(root, asset, 'hdri')
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new('CC0 low-sun environment')
        bpy.context.scene.world = world
    world.use_nodes = True
    tree = world.node_tree
    tree.nodes.clear()
    coord = _node(tree, 'ShaderNodeTexCoord', 'World ray direction')
    mapping = _node(tree, 'ShaderNodeMapping', 'Reference sun azimuth alignment')
    # Cycles equirectangular phi = pi - 2*pi*u. The lookup vector is rotated
    # from scene azimuth to the native HDRI direction; no horizon tilt is applied.
    native_azimuth = 180 - 360 * info['u']
    rotation_deg = native_azimuth - REFERENCE_SUN_AZIMUTH_XY_DEG + yaw_offset_deg
    mapping.inputs['Rotation'].default_value[2] = math.radians(rotation_deg)
    tree.links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
    environment = _node(tree, 'ShaderNodeTexEnvironment', 'CC0 unregistered low-sun environment')
    environment.image = image
    environment.projection = 'EQUIRECTANGULAR'
    tree.links.new(mapping.outputs['Vector'], environment.inputs['Vector'])
    background = _node(tree, 'ShaderNodeBackground', 'Single coherent illumination and background')
    background.inputs['Strength'].default_value = strength
    tree.links.new(environment.outputs['Color'], background.inputs['Color'])
    output = _node(tree, 'ShaderNodeOutputWorld', 'World Output')
    tree.links.new(background.outputs[0], output.inputs['Surface'])
    world['Environment source'] = asset['source_page']
    world['Environment registration'] = 'Lighting/background proxy only; not geographically registered to Protolabs'
    world['Reference sun azimuth XY degrees'] = REFERENCE_SUN_AZIMUTH_XY_DEG
    world['HDRI sun elevation degrees'] = info['elevation']
    return {'asset_id': asset['asset_id'], 'lookup_rotation_z_degrees': rotation_deg,
            'sun_elevation_degrees': info['elevation'], 'strength': strength}


def apply_material_quality(root=ROOT, environment='qwantani_sunset_puresky',
                           environment_strength=1.0, yaw_offset_deg=0):
    """Upgrade existing materials. environment=None retains the existing world."""
    import bpy
    root = Path(root)
    assets = {a['asset_id']: a for a in _manifest(root)['assets']}
    settings = [
        ('Weathered asphalt / metric noise', 'asphalt_01', (.040, .042, .042), 2.1, .004, .14),
        ('Mown summer grass', 'leafy_grass', (.055, .105, .030), 2.0, .017, .16),
        ('Prairie meadow', 'leafy_grass', (.077, .100, .037), 2.0, .022, .22),
        ('Warm umber precast / photo colour', 'rough_concrete', (.082, .040, .030), 1.23, .0012, .07),
        ('Muted burgundy precast', 'rough_concrete', (.091, .044, .035), 1.23, .0012, .07),
        ('Light brown panel bands', 'rough_concrete', (.107, .061, .044), 1.23, .0012, .07),
        ('Concrete curbs & walks', 'rough_concrete', (.28, .28, .25), 1.23, .0015, .10),
        ('Charcoal aggregate membrane', 'asphalt_01', (.067, .061, .061), 1.0, .006, .13),
    ]
    for name, asset_id, albedo, tile, bump, variation in settings:
        _surface(root, name, assets[asset_id], albedo, tile, bump, variation)
    # Coated metal is mostly a dielectric paint finish, with restrained sheen.
    _plain_response('Ivory coated aluminum', (.82, .845, .845), .38, .05)
    _plain_response('White structural steel', (.73, .77, .78), .34, .10)
    _plain_response('Silver standing seam roof', (.65, .69, .70), .32, .55)
    _plain_response('Anodized blue grey mullions', (.62, .70, .735), .30, .35)
    glass, glass_bsdf = _plain_response('Blue reflective insulated glazing', (.90, .95, .975), .045, 0, 1.0, 1.52)
    # Thin facade panes need full transmission: the former 30% diffuse lobe
    # appeared as opaque gray panels. A restrained dielectric coating supplies
    # additional grazing reflections without returning to blue metallic glass.
    glass_bsdf.inputs['Coat Weight'].default_value = .65
    glass_bsdf.inputs['Coat Roughness'].default_value = .035
    glass_bsdf.inputs['Coat IOR'].default_value = 1.7
    glass['Coating evidence'] = 'Interpreted low-E reflective glazing proxy; no product specification is established'
    _plain_response('Protolabs blue identity', (.015, .48, .65), .34, 0)
    _plain_response('Unspecified dark interior depth', (.018, .022, .025), .85)
    _parking_paint()
    report = {'surface_materials': [s[0] for s in settings], 'geometry_changed': False,
              'world': None, 'note': 'Shader response proposal; integrated visual acceptance is still required.'}
    if environment is not None:
        if environment not in ENVIRONMENTS:
            raise ValueError(f'Choose environment=None or one of {list(ENVIRONMENTS)}')
        report['world'] = _environment(root, assets[environment], environment_strength, yaw_offset_deg)
    bpy.context.scene['Material quality provenance'] = 'docs/material-provenance.md'
    bpy.context.scene['Material quality proposal'] = json.dumps(report)
    print('MATERIAL_QUALITY_READY', json.dumps(report))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--include-candidates', action='store_true')
    args = parser.parse_args()
    if not args.download:
        parser.error('For ordinary Python use --download; import apply_material_quality inside Blender.')
    print(json.dumps(acquire_assets(args.root, args.include_candidates), indent=2))
