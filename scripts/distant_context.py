"""Add source-traced woodland context without changing measured campus objects.

Call add_distant_context(root, collection, tree_assets) after the original three
vegetation assets and distant ground surround exist. No network, save or export.
"""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import math
import random

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

MAX_TREES = 1200  # Instance budget; remote groups do not denote individual trees.
MARGIN_WIDTH = 8.0
SEED = 554017
TAG = 'protolabs_distant_context'
REFERENCE_XY = (122.2179957382899, -41.42428315068638)
LOD_DISTANCE = 700.0
CLUSTER_DISTANCE = 2000.0
LOD_CARDS = 2000
PROTECTED_GRIDS = ((-180., -170., 240., 220.), (-170., 60., 230., 405.))


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
        if not length2:
            continue
        t = max(0., min(1., ((x-a[0])*dx + (y-a[1])*dy)/length2))
        closest = min(closest, math.hypot(x-a[0]-t*dx, y-a[1]-t*dy))
    return closest


def _area(polygon):
    return abs(sum(a[0]*b[1]-b[0]*a[1]
                   for a, b in zip(polygon, polygon[1:]+polygon[:1])))/2


def _candidates(row, index):
    """Deterministic overlapping crowns; whole nominal crowns stay in the trace."""
    polygon = row['polygon_xy_m']
    rng = random.Random(SEED + index*101)
    xs, ys = zip(*polygon)
    low, high = row['canopy_height_range_m']
    remote = row.get('representation') == 'inferred_multi_crown_cluster'
    candidates, bins = [], {}
    cell = 24. if remote else 12.
    attempts = min(35000, max(5000, int(_area(polygon)*1.2)))
    for _ in range(attempts):
        x, y = rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))
        if not _inside((x, y), polygon):
            continue
        distance = math.hypot(x-REFERENCE_XY[0], y-REFERENCE_XY[1])
        if remote and distance < CLUSTER_DISTANCE:
            raise ValueError('Canopy groups may only represent woodland beyond 2km')
        height = rng.uniform(low, high)
        crown = rng.uniform(22., 32.) if remote else max(7., min(12., height*rng.uniform(.55, .72)))
        # Bound circular crown overhang by the actual polygon, including creek banks.
        inset = max(float(row.get('recommended_edge_inset_m', 8.)), crown/2.+2.)
        if _edge_distance((x, y), polygon) < inset:
            continue
        spacing = crown*(.63 if remote else .66)
        key = (math.floor(x/cell), math.floor(y/cell))
        neighbors = (p for ix in range(key[0]-1, key[0]+2)
                     for iy in range(key[1]-1, key[1]+2)
                     for p in bins.get((ix, iy), []))
        if any(math.hypot(x-p['x'], y-p['y']) < (spacing+p['spacing'])/2
               for p in neighbors):
            continue
        representation = ('inferred_crown_cluster' if remote else
                          'linked_card_lod' if distance > LOD_DISTANCE else 'linked_full_tree')
        point = {'x': x, 'y': y, 'height': height, 'crown': crown,
                 'spacing': spacing, 'rotation': rng.random()*math.tau,
                 'asset_index': rng.randrange(3), 'representation': representation,
                 'reference_distance_m': distance}
        candidates.append(point)
        bins.setdefault(key, []).append(point)
    return candidates


def _cap_across_belts(groups):
    """Retain the first evenly spaced dart samples, rather than random hole cutting."""
    total = sum(len(points) for points in groups)
    if total <= MAX_TREES:
        return groups
    exact = [len(points)*MAX_TREES/total for points in groups]
    budgets = [math.floor(value) for value in exact]
    order = sorted(range(len(groups)), key=lambda i: exact[i]-budgets[i], reverse=True)
    for index in order[:MAX_TREES-sum(budgets)]:
        budgets[index] += 1
    return [points[:budget] for points, budget in zip(groups, budgets)]


def _ground_at(row, x, y):
    samples = row.get('ground_elevation_samples')
    if not samples or len(samples) == 1:
        return float(row['ground_elevation']['scene_ground_z_m'])
    weights = [1./max(.01, (x-s['query_xy_local_m'][0])**2+(y-s['query_xy_local_m'][1])**2)
               for s in samples]
    return sum(w*s['scene_ground_z_m'] for w, s in zip(weights, samples))/sum(weights)


def _bounds(data):
    low = [min(vertex.co[i] for vertex in data.vertices) for i in range(3)]
    high = [max(vertex.co[i] for vertex in data.vertices) for i in range(3)]
    if any(high[i] <= low[i] for i in range(3)):
        raise ValueError('Vegetation asset has degenerate mesh bounds')
    return low, high


def _card_lod(data, index):
    """Separate 2000-card copy, stratified in 3D, retaining UVs and exact extrema.

    CampusVeg materials keep compatibility with export_viewer's additional 30%
    browser reduction. Original master templates are never changed or reassigned.
    """
    low, high = _bounds(data)
    groups = defaultdict(list)
    for face in data.polygons:
        if face.material_index:
            groups[min(face.vertices)].append(face)
    if len(groups) <= LOD_CARDS:
        return data
    cells = defaultdict(list)
    for key, faces in groups.items():
        center = faces[0].center
        cell = tuple(min(4, int((center[i]-low[i])/(high[i]-low[i])*5)) for i in range(3))
        cells[cell].append(key)
    rng = random.Random(SEED+18000+index)
    for keys in cells.values():
        rng.shuffle(keys)
    # Include cards containing an extreme vertex so dimensions cannot shrink.
    extreme = {min(data.vertices, key=lambda v: v.co[i]).index for i in range(3)}
    extreme |= {max(data.vertices, key=lambda v: v.co[i]).index for i in range(3)}
    selected = {key for key, faces in groups.items()
                if any(extreme.intersection(face.vertices) for face in faces)}
    order = sorted(cells)
    while len(selected) < LOD_CARDS:
        progress = False
        for cell in order:
            if cells[cell]:
                selected.add(cells[cell].pop())
                progress = True
                if len(selected) == LOD_CARDS:
                    break
        if not progress:
            break
    kept = [face for face in data.polygons if face.material_index == 0 or min(face.vertices) in selected]
    used = sorted({v for face in kept for v in face.vertices})
    remap = {old: new for new, old in enumerate(used)}
    lod = bpy.data.meshes.new(data.name+' distant2000')
    lod.from_pydata([data.vertices[v].co for v in used], [],
                    [[remap[v] for v in face.vertices] for face in kept])
    for material in data.materials:
        lod.materials.append(material)
    for dst, src in zip(lod.polygons, kept):
        dst.material_index, dst.use_smooth = src.material_index, src.use_smooth
    for uv in data.uv_layers:
        target = lod.uv_layers.new(name=uv.name)
        for dst, src in zip(lod.polygons, kept):
            for dl, sl in zip(dst.loop_indices, src.loop_indices):
                target.data[dl].uv = uv.data[sl].uv
    lod.update()
    if max(abs(a-b) for aa, bb in zip(_bounds(lod), (low, high)) for a, b in zip(aa, bb)) > 1e-5:
        raise AssertionError('Context card LOD lost an original mesh extremum')
    lod['context_leaf_cards'] = len(selected)
    return lod


def _cluster_mesh(index):
    """Low-frequency irregular crown group for >2km only; no leaf-card aliasing."""
    rng = random.Random(SEED+20000+index)
    data = bpy.data.meshes.new(f'Distant inferred canopy group {index}')
    materials = []
    for number, color in enumerate(((.027,.061,.020),(.032,.071,.024),(.039,.080,.027))):
        name = f'DistantCanopy_Group_{number}'
        material = bpy.data.materials.get(name)
        if material is None:
            material = bpy.data.materials.new(name)
            material.use_nodes = True
            bsdf = material.node_tree.nodes.get('Principled BSDF')
            bsdf.inputs['Base Color'].default_value = (*color, 1.)
            bsdf.inputs['Roughness'].default_value = .9
            material.diffuse_color = (*color, 1.)
        materials.append(material)
    bm = bmesh.new()
    try:
        # Overlapping ellipsoidal crown lobes: several unresolved crowns, not giant trees.
        for number in range(17):
            angle = number*2.399963229728653+rng.uniform(-.2,.2)
            radius = math.sqrt(number/17)*.31
            cx, cy = math.cos(angle)*radius, math.sin(angle)*radius
            cz = rng.uniform(.49,.69)
            sx, sy, sz = rng.uniform(.19,.29), rng.uniform(.17,.27), rng.uniform(.20,.32)
            result = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.)
            vertices = result['verts']
            for v in vertices:
                v.co = (cx+v.co.x*sx, cy+v.co.y*sy, cz+v.co.z*sz)
            for face in {face for v in vertices for face in v.link_faces}:
                face.material_index = number%3
                face.smooth = True
        # Minimal central woody stem supplies ground-to-top height semantics.
        stem = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=7,
                                     radius1=.018, radius2=.012, depth=.46)
        for v in stem['verts']:
            v.co.z += .23
        bmesh.ops.triangulate(bm, faces=list(bm.faces))
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(data)
    finally:
        bm.free()
    low, high = _bounds(data)
    diameter = max(high[0]-low[0], high[1]-low[1])
    for vertex in data.vertices:
        vertex.co.x = (vertex.co.x-(low[0]+high[0])/2)/diameter
        vertex.co.y = (vertex.co.y-(low[1]+high[1])/2)/diameter
        vertex.co.z = (vertex.co.z-low[2])/(high[2]-low[2])
    for material in materials:
        data.materials.append(material)
    data.update()
    data['representation'] = 'Inferred unresolved multi-crown group, used beyond 2km only'
    return data


def add_distant_context(root, collection, tree_assets):
    """Return a placement receipt. Existing objects/templates/materials stay intact."""
    root = Path(root)
    if any(obj.get(TAG) for obj in bpy.data.objects):
        raise RuntimeError('Distant context already exists; rebuild the scene to replace it')
    if len(tree_assets) != 3 or any(obj.type != 'MESH' for obj in tree_assets):
        raise ValueError('Pass exactly three existing mesh vegetation template objects')
    source = root/'research/distant-woodland.json'
    evidence = json.loads(source.read_text())
    rows = [row for row in evidence['polygons'] if row.get('scene_eligible')]
    if {row['id'] for row in rows} != {'wood-01','wood-02','wood-03','wood-04','wood-06','wood-07','wood-08','wood-09'}:
        raise ValueError('Expected the eight reviewed eligible woodland interiors')
    for row in rows:
        xs, ys = zip(*row['polygon_xy_m'])
        # Conservative bbox rejection is sufficient for the reviewed disjoint traces.
        if any(not(max(xs)<a or min(xs)>c or max(ys)<b or min(ys)>d)
               for a,b,c,d in PROTECTED_GRIDS):
            raise ValueError('Woodland overlaps a protected measured grid: '+row['id'])
        if 'scene_ground_z_m' not in row.get('ground_elevation', {}):
            raise ValueError('Missing EPQS point evidence for '+row['id'])
    surround = bpy.data.objects.get('Distant ground surround')
    if surround is None or surround.type != 'MESH' or not surround.data.materials:
        raise ValueError('Create the material-bearing distant ground surround first')
    surround_z = min((surround.matrix_world@v.co).z for v in surround.data.vertices)
    if any(surround_z >= _ground_at(row,*p) for row in rows for p in row['polygon_xy_m']):
        raise ValueError('Far surround must lie below all inferred woodland ground')
    from regional_ground import add_regional_context_ground
    regional_grid=json.loads((root/'research/regional_context_ground_grid.json').read_text())
    if surround_z >= min(min(row) for row in regional_grid['z']):
        raise ValueError('Far surround must lie below the regional DEM minimum')
    regional_object,regional_surface,regional_receipt=add_regional_context_ground(
        root,collection,surround.data.materials[0])
    original = [asset.data for asset in tree_assets]
    lods = [_card_lod(data,index) for index,data in enumerate(original)]
    clusters = [_cluster_mesh(index) for index in range(3)]
    meshes = {'linked_full_tree': original, 'linked_card_lod': lods, 'inferred_crown_cluster': clusters}
    bounds = {key: [_bounds(data) for data in datas] for key,datas in meshes.items()}
    candidates = [_candidates(row,index) for index,row in enumerate(rows)]
    # Verify true vertex radius as well as nominal crown diameter. This handles
    # asymmetric original crowns and rotation without overhanging the trace.
    radii = {key:[max(math.hypot(v.co.x,v.co.y) for v in data.vertices)/
                       max(high[0]-low[0],high[1]-low[1])
                  for data,(low,high) in zip(datas,bounds[key])]
             for key,datas in meshes.items()}
    candidates = [[p for p in points if _edge_distance((p['x'],p['y']),row['polygon_xy_m']) >=
                    p['crown']*radii[p['representation']][p['asset_index']]+2.]
                  for row,points in zip(rows,candidates)]
    groups = _cap_across_belts(candidates)
    report = {'source':'research/distant-woodland.json',
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(), 'seed':SEED,
        'instance_cap':MAX_TREES, 'protected_grid_rectangles_xy_m':PROTECTED_GRIDS,
        'surround_z_m':surround_z, 'lod_distance_m':LOD_DISTANCE,
        'cluster_distance_m':CLUSTER_DISTANCE, 'context_lod_cards':LOD_CARDS,
        'scope':'Inferred context only. Original templates, campus/north trees and measured terrain unchanged.',
        'height_basis':'Inferred woodland ranges, not individual measurements.',
        'terrain_basis':'Continuous50m USGS3DEP grid, outside-only75m transition to original measured boundaries.',
        'regional_ground':regional_receipt,
        'mesh_triangles':{key:[sum(len(f.vertices)-2 for f in data.polygons) for data in datas]
                          for key,datas in meshes.items()}, 'belts':[]}
    for row,points in zip(rows,groups):
        patch,surface = regional_object,regional_surface
        placements=[]
        for index,point in enumerate(points):
            hit,_,_,_ = surface.ray_cast(Vector((point['x'],point['y'],100.)), Vector((0.,0.,-1.)))
            if hit is None:
                raise RuntimeError('Context placement missed regional DEM surface')
            asset_index,representation = point['asset_index'],point['representation']
            low,high = bounds[representation][asset_index]
            vertical=point['height']/(high[2]-low[2])
            horizontal=point['crown']/max(high[0]-low[0],high[1]-low[1])
            obj=bpy.data.objects.new(f"Distant woodland {row['id']} {index+1:03d}",meshes[representation][asset_index])
            collection.objects.link(obj)
            obj.location=(point['x'],point['y'],hit.z-low[2]*vertical)
            obj.scale=(horizontal,horizontal,vertical)
            obj.rotation_euler.z=point['rotation']
            obj[TAG]=True
            obj['belt_id']=row['id']
            obj['representation']=representation
            obj['evidence_source']='research/distant-woodland.json'
            obj['evidence']='Traced woody interior; position, height, crown and species inferred. Remote groups are not individual trees.'
            obj['inferred_canopy_height_m']=point['height']
            obj['inferred_ground_z_m']=hit.z
            placements.append({'object':obj.name, 'x':point['x'], 'y':point['y'],
                'ground_z':hit.z, 'height_m':point['height'], 'crown_m':point['crown'],
                'spacing_m':point['spacing'], 'asset_index':asset_index,
                'representation':representation, 'reference_distance_m':point['reference_distance_m'],
                'edge_distance_m':_edge_distance((point['x'],point['y']),row['polygon_xy_m'])})
        report['belts'].append({'id':row['id'],'instance_count':len(placements),
            'tree_count':sum(p['representation']!='inferred_crown_cluster' for p in placements),
            'cluster_count':sum(p['representation']=='inferred_crown_cluster' for p in placements),
            'terrain_object':patch.name,'terrain_triangles':0,
            'epqs_ground_z_m':row['ground_elevation']['scene_ground_z_m'],'placements':placements})
    report['instance_count']=sum(b['instance_count'] for b in report['belts'])
    report['tree_count']=sum(b['tree_count'] for b in report['belts'])
    report['cluster_count']=sum(b['cluster_count'] for b in report['belts'])
    report['representation_counts']={key:sum(p['representation']==key for b in report['belts'] for p in b['placements']) for key in meshes}
    return report
