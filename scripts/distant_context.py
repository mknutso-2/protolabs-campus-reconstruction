"""Add inferred distant woodland from the attributed 2026 aerial/EPQS record.

Call add_distant_context(root, collection, tree_assets) after creating the three
original vegetation assets and the distant ground surround. Existing meshes and
measured tree objects are never edited. No network or external Python dependency.
"""
from pathlib import Path
import hashlib
import json
import math
import random

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon

MAX_TREES = 300
MIN_CONTEXT_Y = 405.0
EDGE_INSET = 8.0
MARGIN_WIDTH = 8.0
SEED = 554017
TAG = 'protolabs_distant_context'


def _inside(point, polygon):
    x, y = point
    result = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        if (a[1] > y) != (b[1] > y):
            crossing = (b[0]-a[0])*(y-a[1])/(b[1]-a[1]) + a[0]
            if x < crossing:
                result = not result
    return result


def _edge_distance(point, polygon):
    x, y = point
    closest = float('inf')
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        length2 = dx*dx + dy*dy
        t = max(0., min(1., ((x-a[0])*dx + (y-a[1])*dy)/length2))
        closest = min(closest, math.hypot(x-a[0]-t*dx, y-a[1]-t*dy))
    return closest


def _area(polygon):
    return abs(sum(a[0]*b[1]-b[0]*a[1]
                   for a, b in zip(polygon, polygon[1:]+polygon[:1])))/2


def _candidates(row, index):
    """Bounded dart sampling with crown-dependent 12–16m pair spacing."""
    polygon = row['polygon_xy_m']
    rng = random.Random(SEED + index*101)
    xs, ys = zip(*polygon)
    low, high = row['canopy_height_range_m']
    candidates = []
    bins = {}
    cell = 16.
    attempts = min(20000, max(2500, int(_area(polygon)/4)))
    for _ in range(attempts):
        x, y = rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))
        if y < MIN_CONTEXT_Y or not _inside((x, y), polygon):
            continue
        if _edge_distance((x, y), polygon) < EDGE_INSET:
            continue
        height = rng.uniform(low, high)
        crown = max(6., min(12., height*rng.uniform(.49, .65)))
        spacing = max(12., min(16., crown+3.5))
        key = (math.floor(x/cell), math.floor(y/cell))
        neighbors = (p for ix in range(key[0]-1, key[0]+2)
                     for iy in range(key[1]-1, key[1]+2)
                     for p in bins.get((ix, iy), []))
        if any(math.hypot(x-p['x'], y-p['y']) < (spacing+p['spacing'])/2
               for p in neighbors):
            continue
        point = {'x': x, 'y': y, 'height': height, 'crown': crown,
                 'spacing': spacing, 'rotation': rng.random()*math.tau,
                 'asset_index': rng.randrange(3)}
        candidates.append(point)
        bins.setdefault(key, []).append(point)
    return candidates


def _cap_across_belts(groups):
    """Proportional cap, retaining a deterministic spread in every eligible belt."""
    total = sum(len(points) for points in groups)
    if total <= MAX_TREES:
        return groups
    exact = [len(points)*MAX_TREES/total for points in groups]
    budgets = [math.floor(value) for value in exact]
    order = sorted(range(len(groups)), key=lambda i: exact[i]-budgets[i], reverse=True)
    for index in order[:MAX_TREES-sum(budgets)]:
        budgets[index] += 1
    chosen = []
    for index, (points, budget) in enumerate(zip(groups, budgets)):
        selection = random.Random(SEED+9000+index).sample(points, budget)
        chosen.append(sorted(selection, key=lambda p: (p['y'], p['x'])))
    return chosen


def _terrain_patch(row, collection, material, surround_z):
    """Triangulated plateau with an internal margin; no expansion into marsh."""
    polygon = row['polygon_xy_m']
    ground_z = float(row['ground_elevation']['scene_ground_z_m'])
    vectors = [Vector((x, y, ground_z)) for x, y in polygon]
    by_xy = {(point.x, point.y): index for index, point in enumerate(vectors)}
    faces = [tuple(point if isinstance(point, int) else by_xy[(point.x, point.y)]
                   for point in triangle)
             for triangle in tessellate_polygon([vectors])]
    data = bpy.data.meshes.new('Distant terrain '+row['id'])
    data.from_pydata(vectors, [], faces)
    bm = bmesh.new()
    try:
        bm.from_mesh(data)
        longest = max(edge.calc_length() for edge in bm.edges)
        cuts = min(28, max(3, math.ceil(longest/5.)-1))
        bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=cuts, use_grid_fill=True)
        for vertex in bm.verts:
            distance = _edge_distance((vertex.co.x, vertex.co.y), polygon)
            t = max(0., min(1., distance/MARGIN_WIDTH))
            smooth = t*t*(3.-2.*t)
            vertex.co.z = surround_z + .004 + smooth*(ground_z-surround_z-.004)
        bmesh.ops.triangulate(bm, faces=list(bm.faces))
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        # These are terrain sheets; their intended visible side is upward.
        bmesh.ops.reverse_faces(bm, faces=[face for face in bm.faces if face.normal.z < 0])
        bm.to_mesh(data)
    finally:
        bm.free()
    data.materials.append(material)
    data.update()
    patch = bpy.data.objects.new('Distant inferred ground '+row['id'], data)
    collection.objects.link(patch)
    patch[TAG] = True
    patch['evidence_source'] = 'research/distant-woodland.json'
    patch['belt_id'] = row['id']
    patch['ground_basis'] = ('One EPQS point extended across the belt interior. '
                            '8m margin slopes to existing far plane inside the trace. '
                            'This surface is inferred, not measured terrain.')
    patch['epqs_scene_ground_z_m'] = ground_z
    patch['surround_z_m'] = surround_z
    patch['minimum_context_y_m'] = MIN_CONTEXT_Y
    surface = BVHTree.FromPolygons([v.co for v in data.vertices],
                                   [tuple(f.vertices) for f in data.polygons],
                                   all_triangles=True)
    return patch, surface


def add_distant_context(root, collection, tree_assets):
    """Return a serializable placement report; never save or modify the master.

    Parameters are the repository root, a bpy Collection for the added objects,
    and exactly three mesh template objects from the existing vegetation module.
    Their actual mesh bounds define instance scale. Existing objects/materials
    and all template geometry remain unchanged. Calling twice raises before edits.
    """
    root = Path(root)
    if any(obj.get(TAG) for obj in bpy.data.objects):
        raise RuntimeError('Distant context already exists; rebuild the scene to replace it')
    if len(tree_assets) != 3 or any(obj.type != 'MESH' for obj in tree_assets):
        raise ValueError('Pass exactly three existing mesh vegetation template objects')
    source = root/'research/distant-woodland.json'
    evidence = json.loads(source.read_text())
    rows = [row for row in evidence['polygons'] if row.get('scene_eligible')]
    if {row['id'] for row in rows} != {'wood-01', 'wood-02', 'wood-03', 'wood-04'}:
        raise ValueError('Expected the four reviewed eligible woodland belts')
    for row in rows:
        if min(point[1] for point in row['polygon_xy_m']) <= MIN_CONTEXT_Y:
            raise ValueError('Distant terrain must stay entirely north of y405m')
        if 'scene_ground_z_m' not in row.get('ground_elevation', {}):
            raise ValueError('Missing recorded EPQS point elevation for '+row['id'])
    surround = bpy.data.objects.get('Distant ground surround')
    if surround is None or surround.type != 'MESH' or not surround.data.materials:
        raise ValueError('Create the existing material-bearing distant ground surround first')
    surround_z = min((surround.matrix_world@v.co).z for v in surround.data.vertices)
    if any(surround_z >= row['ground_elevation']['scene_ground_z_m'] for row in rows):
        raise ValueError('Far surround must lie below the recorded distant ground elevations')
    material = surround.data.materials[0]
    bounds = []
    for asset in tree_assets:
        low = [min(vertex.co[i] for vertex in asset.data.vertices) for i in range(3)]
        high = [max(vertex.co[i] for vertex in asset.data.vertices) for i in range(3)]
        if any(high[i] <= low[i] for i in range(3)):
            raise ValueError('Vegetation asset has degenerate mesh bounds')
        bounds.append((low, high))
    groups = _cap_across_belts([_candidates(row, index) for index, row in enumerate(rows)])
    report = {'source': 'research/distant-woodland.json',
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'seed': SEED, 'tree_cap': MAX_TREES, 'minimum_context_y_m': MIN_CONTEXT_Y,
              'edge_inset_m': EDGE_INSET, 'surround_z_m': surround_z,
              'scope': 'Inferred distant context only; no existing tree or measured terrain edits.',
              'height_basis': 'Ranges inferred from woodland type; ground from sparse EPQS points.',
              'terrain_basis': 'Per-belt plateau with an8m internal taper; not surveyed topography.',
              'belts': []}
    for row, points in zip(rows, groups):
        patch, surface = _terrain_patch(row, collection, material, surround_z)
        placements = []
        for index, point in enumerate(points):
            ground_z = float(row['ground_elevation']['scene_ground_z_m'])
            hit, _, _, _ = surface.ray_cast(Vector((point['x'], point['y'], ground_z+50.)),
                                            Vector((0., 0., -1.)))
            if hit is None:
                raise RuntimeError('Tree placement missed its inferred ground patch')
            asset_index = point['asset_index']
            low, high = bounds[asset_index]
            vertical = point['height']/(high[2]-low[2])
            horizontal = point['crown']/max(high[0]-low[0], high[1]-low[1])
            obj = bpy.data.objects.new(f"Distant woodland {row['id']} {index+1:03d}",
                                       tree_assets[asset_index].data)
            collection.objects.link(obj)
            obj.location = (point['x'], point['y'], hit.z-low[2]*vertical)
            obj.scale = (horizontal, horizontal, vertical)
            obj.rotation_euler.z = point['rotation']
            obj[TAG] = True
            obj['belt_id'] = row['id']
            obj['evidence_source'] = 'research/distant-woodland.json'
            obj['evidence'] = 'Aerial-traced belt; individual tree position, species, crown and height inferred.'
            obj['inferred_canopy_height_m'] = point['height']
            obj['inferred_ground_z_m'] = hit.z
            placements.append({'object': obj.name, 'x': point['x'], 'y': point['y'],
                'ground_z': hit.z, 'height_m': point['height'], 'crown_m': point['crown'],
                'spacing_m': point['spacing'], 'asset_index': asset_index,
                'edge_distance_m': _edge_distance((point['x'], point['y']), row['polygon_xy_m'])})
        report['belts'].append({'id': row['id'], 'tree_count': len(placements),
            'terrain_object': patch.name, 'terrain_triangles': len(patch.data.polygons),
            'epqs_ground_z_m': row['ground_elevation']['scene_ground_z_m'],
            'placements': placements})
    report['tree_count'] = sum(belt['tree_count'] for belt in report['belts'])
    return report
