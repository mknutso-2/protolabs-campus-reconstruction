"""Apply the explicitly inferred monument-sign fit to its complete assembly.

Call ``apply_monument_finish(ROOT)`` after geometry and fixed cameras exist,
before material export, scene packing/saving and GLB export. Importing this module
does not mutate the scene. The function never saves, renders, or edits cameras.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'Monument fit SHA256'
MAIN_NAMES = ('Monument sign base', 'Dark monument sign', 'Monument brand',
              'Monument tagline', 'Monument address', 'Blue monument rule')
LOGO_PREFIXES = ('Hexagonal Protolabs outline', 'Mark inner bars')


def _ground(grid, x, y):
    tx, ty, tz = grid['x'], grid['y'], grid['z']
    fx = max(0, min(len(tx)-1.001, (x-tx[0])/(tx[1]-tx[0])))
    fy = max(0, min(len(ty)-1.001, (y-ty[0])/(ty[1]-ty[0])))
    ix, iy = int(fx), int(fy)
    u, v = fx-ix, fy-iy
    return (tz[iy][ix]*(1-u)+tz[iy][ix+1]*u)*(1-v)+(tz[iy+1][ix]*(1-u)+tz[iy+1][ix+1]*u)*v


def apply_monument_finish(root=ROOT):
    """Apply one shared affine assembly transform; repeated calls are a no-op."""
    import bpy
    from mathutils import Euler, Matrix, Vector

    root = Path(root)
    fit_path = root/'research/monument-sign-fit.json'
    raw = fit_path.read_bytes()
    fingerprint = hashlib.sha256(raw).hexdigest()
    data = json.loads(raw)
    panel = bpy.data.objects.get('Dark monument sign')
    if panel is None:
        raise RuntimeError('Build the original monument assembly before applying its fit')
    if panel.get(MARKER):
        if panel[MARKER] != fingerprint:
            raise RuntimeError('A different monument fit is already applied; rebuild the original assembly')
        report = json.loads(panel['Monument fit report'])
        if any(bpy.data.objects.get(name) is None or bpy.data.objects[name].get(MARKER) != fingerprint
               for name in report['assembly_objects']):
            raise RuntimeError('The previously fitted monument assembly is incomplete')
        return {**report, 'already_applied': True}

    # Reject stale terrain/camera inputs rather than applying a hidden old fit.
    for key in ('terrain', 'camera'):
        record = data[key]
        if hashlib.sha256((root/record['path']).read_bytes()).hexdigest() != record['sha256']:
            raise RuntimeError(f'Monument fit {key} input changed; refit before applying')
    terrain = json.loads((root/data['terrain']['path']).read_text())
    bpy.context.view_layer.update()
    camera = bpy.data.objects.get('reference_aerial')
    expected = data['camera']
    if (camera is None or camera.type != 'CAMERA'
        or (camera.matrix_world.translation-Vector(expected['position'])).length > .001
        or camera.rotation_euler.to_quaternion().rotation_difference(
            Euler(expected['rotation_euler_xyz_radians'], 'XYZ').to_quaternion()).angle > .0001
        or abs(camera.data.lens-expected['lens_mm']) > .0001):
        raise RuntimeError('Monument fit requires the documented fixed reference camera')

    bpy.context.view_layer.update()
    source = data['method']['source_panel']
    sx, sy = source['center_xy_m']
    source_pivot = Vector((sx, sy, _ground(terrain, sx, sy)+source['center_z_above_ground_m']))
    if (panel.matrix_world.translation-source_pivot).length > .005:
        raise RuntimeError('Original monument center differs from the fit source assembly')
    # Source dimensions are local mesh dimensions, independent of its bevel.
    dimensions = [max(v.co[i] for v in panel.data.vertices)-min(v.co[i] for v in panel.data.vertices)
                  for i in range(3)]
    if any(abs(a-b) > .001 for a, b in zip(dimensions, (5.8, .27, 2.75))):
        raise RuntimeError('Original monument panel dimensions changed; inspect/refit the assembly')
    if panel.matrix_world.to_quaternion().angle > .0001 or any(abs(s-1) > .0001 for s in panel.scale):
        raise RuntimeError('Original monument panel has an unexpected rotation or scale')

    assembly = []
    for name in MAIN_NAMES:
        ob = bpy.data.objects.get(name)
        if ob is None:
            raise RuntimeError(f'Missing monument assembly part: {name}')
        assembly.append(ob)
    # Logo helpers share names with facade logos. Select only the three whose
    # world-space bounds lie at the monument; never move the facade branding.
    for ob in bpy.data.objects:
        if ob.type not in {'MESH', 'CURVE', 'FONT'} or not ob.name.startswith(LOGO_PREFIXES):
            continue
        center = sum((ob.matrix_world@Vector(c) for c in ob.bound_box), Vector())/8
        if (center-source_pivot).length < 4.0:
            assembly.append(ob)
    if len(assembly) != 9:
        raise RuntimeError(f'Expected six named monument parts and three logo parts; found {len(assembly)}')
    if any(ob.parent is not None for ob in assembly):
        raise RuntimeError('Monument parenting changed; avoid double-transforming a hierarchy')
    if any(ob.get(MARKER) for ob in assembly):
        raise RuntimeError('Partially transformed monument assembly; rebuild before applying')

    fit = data['fit']
    x, y = fit['center_xy_m']
    target_ground = _ground(terrain, x, y)
    target = Vector((x, y, target_ground+fit['panel_bottom_above_ground_m']+fit['panel_height_m']/2))
    scale = (fit['panel_width_m']/source['width_m'], 1.0, fit['panel_height_m']/source['height_m'])
    transform = (Matrix.Translation(target) @ Matrix.Rotation(fit['yaw_radians'], 4, 'Z')
                 @ Matrix.Diagonal((*scale, 1.0)) @ Matrix.Translation(-source_pivot))
    report = {'fit_sha256': fingerprint, 'assembly_objects': [ob.name for ob in assembly],
              'source_pivot_xyz_m': list(source_pivot), 'target_pivot_xyz_m': list(target),
              'shared_scale_xyz': list(scale), 'yaw_degrees': fit['yaw_degrees'],
              'world_transform_rows': [list(row) for row in transform],
              'corner_rms_px': fit['corner_rms_px'], 'already_applied': False,
              'scope': 'Photo-inferred entire sign assembly correction; camera, terrain and other objects unchanged'}
    # Positive scales preserve winding and readable lettering. All components,
    # including fonts, bevelled base and logo curves, receive exactly this matrix.
    for ob in assembly:
        ob.matrix_world = transform @ ob.matrix_world
        ob[MARKER] = fingerprint
        ob['evidence'] = 'Photo-fitted monument assembly; research/monument-sign-fit.json; dimensions/yaw inferred'
    panel['Monument fit report'] = json.dumps(report)
    bpy.context.view_layer.update()
    print('MONUMENT_FINISH_READY', json.dumps(report))
    return report
