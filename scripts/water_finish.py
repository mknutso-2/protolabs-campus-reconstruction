"""Replace terrain-draped water with a flat evidence-based, basin-clipped surface.

Call apply_water_finish(root) after site polygons and measured terrain exist,
before saving/exporting. Only the two named water objects receive new mesh data.
"""
from pathlib import Path
import hashlib
import json
import math

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

TAG='protolabs_flat_water'


def _clip(poly,signed):
    if not poly:return []
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        sa,sb=signed(a),signed(b)
        ina,inb=sa>=-1e-10,sb>=-1e-10
        if ina:result.append(a)
        if ina!=inb:
            t=sa/(sa-sb)
            result.append(tuple(a[i]+t*(b[i]-a[i]) for i in range(3)))
    return result


def _cross(a,b,p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])


def _within_triangle(poly,triangle):
    orientation=1. if _cross(triangle[0],triangle[1],triangle[2])>=0 else -1.
    for a,b in zip(triangle,triangle[1:]+triangle[:1]):
        poly=_clip(poly,lambda p:orientation*_cross(a,b,p))
        if not poly:break
    return poly


def apply_water_finish(root):
    """Return a geometry/evidence receipt; never save or modify measured ground."""
    root=Path(root);source=root/'research/water-surface-constraints.json'
    evidence=json.loads(source.read_text());level=evidence['scene_water_z_m']
    clearance=evidence['minimum_basin_clearance_m']
    objects=[bpy.data.objects.get(row['id']) for row in evidence['water_polygons']]
    if any(o is None or o.type!='MESH' for o in objects):
        raise ValueError('Create both traced water meshes before applying flat water')
    if any(o.get(TAG) for o in objects):
        if all(o.get(TAG) for o in objects):return {'status':'already_applied'}
        raise ValueError('Water correction is only partially applied')
    ground=bpy.data.objects.get('Measured rolling ground')
    if ground is None or ground.type!='MESH':
        raise ValueError('Create the original measured main terrain first')
    ground.data.calc_loop_triangles()
    world=[tuple(ground.matrix_world@v.co) for v in ground.data.vertices]
    terrain_triangles=[tuple(world[i] for i in t.vertices) for t in ground.data.loop_triangles]
    report={'source':'research/water-surface-constraints.json','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'water_elevation_navd88_m':evidence['water_elevation_navd88_m'],'scene_water_z_m':level,
        'minimum_basin_clearance_m':clearance,'terrain_object':ground.name,
        'scope':'Only water mesh data replaced; measured terrain/materials and existing object transforms unchanged.',
        'water_polygons':[]}
    prepared=[]
    for row,obj in zip(evidence['water_polygons'],objects):
        polygon=row['polygon_xy_m'];vectors=[Vector((x,y,0.)) for x,y in polygon]
        # Clip exact rendered terrain triangles first by water level, then by
        # the source footprint's convex ear triangles. No draped water remains.
        footprints=[]
        for tri in tessellate_polygon([vectors]):
            footprints.append([tuple(vectors[p]) if isinstance(p,int) else tuple(p) for p in tri])
        xs,ys=zip(*polygon);bbox=(min(xs),min(ys),max(xs),max(ys))
        candidates=[]
        for tri in terrain_triangles:
            tx,ty=zip(*[(p[0],p[1]) for p in tri])
            if max(tx)<bbox[0] or min(tx)>bbox[2] or max(ty)<bbox[1] or min(ty)>bbox[3]:continue
            clipped=_clip(list(tri),lambda p:level-clearance-p[2])
            if len(clipped)>=3:candidates.append(clipped)
        vertices=[];faces=[];lookup={};area=0.
        def vertex_id(p):
            key=(round(p[0],7),round(p[1],7))
            if key not in lookup:
                lookup[key]=len(vertices);vertices.append((p[0],p[1],level))
            return lookup[key]
        for terrain in candidates:
            tx,ty=zip(*[(p[0],p[1]) for p in terrain])
            for tri in footprints:
                sx,sy=zip(*[(p[0],p[1]) for p in tri])
                if max(tx)<min(sx) or min(tx)>max(sx) or max(ty)<min(sy) or min(ty)>max(sy):continue
                clipped=_within_triangle(terrain,tri)
                for i in range(1,len(clipped)-1):
                    a,b,c=clipped[0],clipped[i],clipped[i+1]
                    signed_area=_cross(a,b,c)/2
                    if abs(signed_area)<1e-8:continue
                    indices=(vertex_id(a),vertex_id(b),vertex_id(c))
                    if len(set(indices))<3:continue
                    faces.append(indices if signed_area>0 else tuple(reversed(indices)))
                    area+=abs(signed_area)
        if not faces:raise ValueError('Recorded level produced no water inside '+row['id'])
        inverse=obj.matrix_world.inverted()
        data=bpy.data.meshes.new(obj.name+' flat basin-clipped water')
        data.from_pydata([inverse@Vector(v) for v in vertices],[],faces)
        for material in obj.data.materials:data.materials.append(material)
        data.update()
        prepared.append((obj,data))
        outline_area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1])))/2
        report['water_polygons'].append({'id':row['id'],'original_trace_area_m2':outline_area,
            'retained_flat_area_m2':area,'retained_area_fraction':area/outline_area,
            'vertices':len(vertices),'triangles':len(faces),'water_z_range_m':[level,level],
            'waterline_basis':'Traced footprint intersected with actual rendered terrain below the fixed water elevation; no bank inflation.'})
    for obj,data in prepared:
        obj.data=data;obj[TAG]=True;obj['water_elevation_navd88_m']=evidence['water_elevation_navd88_m']
        obj['water_level_evidence']='Dominant interior class2 low-return mode in cached2022 lidar; no class9 and no current survey.'
        obj['evidence_source']='research/water-surface-constraints.json'
    return report
