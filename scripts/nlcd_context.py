"""Add bounded NLCD forest interiors after add_distant_context has built terrain.

Call add_nlcd_context(root, collection); no network, master save, export or edits
of existing objects/meshes/materials. Each new mesh combines one connected patch.
"""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import math
import random

import bpy
from mathutils import Vector

TAG = 'protolabs_nlcd_context'
SEED = 20250907


def add_nlcd_context(root, collection):
    from regional_ground import _surface
    from distant_context import _inside, _edge_distance
    root = Path(root)
    if any(obj.get(TAG) for obj in bpy.data.objects):
        raise RuntimeError('NLCD context already exists; rebuild to replace it')
    selection_path = root/'research/nlcd_context_selection.json'
    grid_path = root/'research/nlcd_landcover_grid.json'
    selection = json.loads(selection_path.read_text())
    if hashlib.sha256(grid_path.read_bytes()).hexdigest() != selection['grid_sha256']:
        raise ValueError('NLCD grid no longer matches reviewed selection')
    belt_path = root/'research/distant-woodland.json'
    if hashlib.sha256(belt_path.read_bytes()).hexdigest() != selection['manual_belts_sha256']:
        raise ValueError('Manual belts changed; recheck NLCD protection')
    grid = json.loads(grid_path.read_text())
    belts = json.loads(belt_path.read_text())['polygons']
    if selection['cell_count'] != 347 or selection['patch_count'] != 36:
        raise ValueError('Expected reviewed347cell/36patch selection')
    ground = bpy.data.objects.get('Regional context ground | USGS3DEP50m')
    if ground is None or ground.type != 'MESH':
        raise ValueError('Call after distant context creates regional ground')
    surface = _surface(ground)
    sources = [bpy.data.meshes.get(f'Distant inferred canopy group {i}') for i in range(3)]
    if any(mesh is None for mesh in sources):
        raise ValueError('Existing three low-cost distant canopy group meshes are required')
    original_materials = list(sources[0].materials)
    if any(list(mesh.materials) != original_materials for mesh in sources):
        raise ValueError('Canopy group material slots must agree')
    if any(any(material.name.startswith('CampusVeg') for material in mesh.materials) for mesh in sources):
        raise ValueError('NLCD groups must not be leaf-card meshes')
    patch_cells = defaultdict(list)
    seen = set()
    for cell in selection['cells']:
        row,col = cell['row'],cell['column']
        if (row,col) in seen or not(0<row<299 and 0<col<299):
            raise ValueError('Duplicate or boundary NLCD cell')
        seen.add((row,col))
        if cell['x'] != -4485+col*30 or cell['y'] != 4485-row*30:
            raise ValueError('Cell coordinates do not match class grid')
        if any(grid['classes'][r][c] not in (41,42,43)
               for r in range(row-1,row+2) for c in range(col-1,col+2)):
            raise ValueError('Selected cell lacks the required forest-neighbor inset')
        if math.hypot(cell['x'],cell['y'])<=700:
            raise ValueError('NLCD cell overlaps protected campus radius')
        for belt in belts:
            polygon = belt['polygon_xy_m']
            if _inside((cell['x'],cell['y']),polygon) or (
                    belt['scene_eligible'] and _edge_distance((cell['x'],cell['y']),polygon)<30):
                raise ValueError('NLCD cell overlaps a protected manual belt')
        patch_cells[cell['patch']].append(cell)
    if len(seen)!=347 or len(patch_cells)!=36:
        raise ValueError('Selection counts do not match reviewed inputs')
    report = {'source':'research/nlcd_context_selection.json',
        'source_sha256':hashlib.sha256(selection_path.read_bytes()).hexdigest(),
        'grid_sha256':selection['grid_sha256'], 'seed':SEED,
        'representation':'Inferred unresolved multi-crown groups on conservative dated30m forest interiors; not tree count or measured height.',
        'height_range_m':[12,18], 'width_range_m':[26,28],
        'ground_object':ground.name, 'ground_source':'research/regional_context_ground_grid.json',
        'ground_source_sha256':hashlib.sha256((root/'research/regional_context_ground_grid.json').read_bytes()).hexdigest(),
        'scope':'Only new merged patches; existing campus/north vegetation, eight manual belts, materials and terrain remain unchanged.',
        'patches':[]}
    for patch_id in sorted(patch_cells):
        vertices,faces,indices,smooth,placements = [],[],[],[],[]
        for cell in patch_cells[patch_id]:
            # Per-cell seed means patch ordering cannot perturb other crowns.
            rng = random.Random(SEED+cell['row']*300+cell['column'])
            asset_index = rng.randrange(3)
            source = sources[asset_index]
            angle = rng.random()*math.tau
            width,height = rng.uniform(26.,28.),rng.uniform(12.,18.)
            ca,sa = math.cos(angle),math.sin(angle)
            rotated = [(v.co.x*ca-v.co.y*sa,v.co.x*sa+v.co.y*ca,v.co.z) for v in source.vertices]
            low = [min(p[k] for p in rotated) for k in range(3)]
            high = [max(p[k] for p in rotated) for k in range(3)]
            scale_xy = width/max(high[0]-low[0],high[1]-low[1])
            scale_z = height/(high[2]-low[2])
            local = [((p[0]-(low[0]+high[0])/2)*scale_xy,
                      (p[1]-(low[1]+high[1])/2)*scale_xy,(p[2]-low[2])*scale_z)
                     for p in rotated]
            # Use the lowest stem's actual XY centroid, which can differ slightly
            # from the rotated crown bbox center. No ground lift or plateau.
            bottom = [p for p in local if p[2]<1e-6]
            root_x = cell['x']+sum(p[0] for p in bottom)/len(bottom)
            root_y = cell['y']+sum(p[1] for p in bottom)/len(bottom)
            hit,_,_,_ = surface.ray_cast(Vector((root_x,root_y,100.)),Vector((0.,0.,-1.)))
            if hit is None:
                raise RuntimeError('NLCD root missed actual regional terrain')
            start = len(vertices)
            world = [(cell['x']+p[0],cell['y']+p[1],hit.z+p[2]) for p in local]
            # Every transformed vertex stays inside its own eligible30m pixel;
            # the additional neighboring forest pixels provide a broad cover inset.
            clearance = min(15-abs(p[k]-cell[('x','y')[k]]) for p in world for k in (0,1))
            if clearance < .5:
                raise AssertionError('Canopy footprint escapes eligible cell inset')
            vertices.extend(world)
            faces.extend(tuple(start+i for i in face.vertices) for face in source.polygons)
            indices.extend(face.material_index for face in source.polygons)
            smooth.extend(face.use_smooth for face in source.polygons)
            placements.append({**cell,'vertex_start':start,'vertex_count':len(world),
                'asset_index':asset_index,'rotation_radians':angle,'ground_z_m':hit.z,
                'root_xy_m':[root_x,root_y],'inferred_height_m':height,'inferred_width_m':width,
                'minimum_cell_footprint_clearance_m':clearance})
        mesh = bpy.data.meshes.new(f'NLCD2025 merged forest patch {patch_id:02d}')
        mesh.from_pydata(vertices,[],faces)
        for material in original_materials:mesh.materials.append(material)
        for face,index,sm in zip(mesh.polygons,indices,smooth):
            face.material_index,face.use_smooth = index,sm
        mesh.update()
        mesh[TAG] = True
        mesh['representation'] = 'Merged low-cost NLCD multiple-crown groups; no leaf cards or leaf reduction'
        obj = bpy.data.objects.new(mesh.name,mesh)
        collection.objects.link(obj)
        obj[TAG] = True
        obj['evidence_source'] = 'research/nlcd_context_selection.json'
        obj['evidence'] = report['representation']
        obj['inferred_crown_group_count'] = len(placements)
        report['patches'].append({'object':obj.name,'groups':len(placements),
            'vertices':len(mesh.vertices),'triangles':sum(len(f.vertices)-2 for f in mesh.polygons),
            'placements':placements})
    report['group_count'] = sum(p['groups'] for p in report['patches'])
    report['patch_object_count'] = len(report['patches'])
    report['triangles'] = sum(p['triangles'] for p in report['patches'])
    report['minimum_cell_footprint_clearance_m'] = min(p['minimum_cell_footprint_clearance_m'] for patch in report['patches'] for p in patch['placements'])
    return report
