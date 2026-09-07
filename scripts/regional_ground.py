"""Continuous source-derived regional ground outside the two existing lidar meshes.

No network, original mesh edits or master save. The50m DEM is authoritative only
at regional scale. Extra near-boundary vertices interpolate it without claiming
additional measurement resolution.
"""
from pathlib import Path
import bisect
import hashlib
import json
import math

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

TAG='protolabs_regional_ground'
SEAM_WIDTH=75.0
MEASURED=(('Measured rolling ground',(-180.,-170.,240.,220.)),
          ('North context ground | lidar',(-170.,220.,230.,405.)))


def sample_grid(grid,x,y):
    xs,ys=grid['x'],grid['y']
    if not(xs[0]<=x<=xs[-1] and ys[0]<=y<=ys[-1]):
        raise ValueError('Regional sample outside recorded grid')
    i=max(0,min(len(xs)-2,bisect.bisect_right(xs,x)-1))
    j=max(0,min(len(ys)-2,bisect.bisect_right(ys,y)-1))
    tx=(x-xs[i])/(xs[i+1]-xs[i]);ty=(y-ys[j])/(ys[j+1]-ys[j])
    z=grid['z']
    return ((z[j][i]*(1-tx)+z[j][i+1]*tx)*(1-ty)+
            (z[j+1][i]*(1-tx)+z[j+1][i+1]*tx)*ty)


def _surface(obj):
    obj.data.calc_loop_triangles()
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],
        [tuple(t.vertices) for t in obj.data.loop_triangles],all_triangles=True)


def add_regional_context_ground(root,collection,material):
    """Return object, actual triangle BVH and serializable source/transition receipt."""
    if any(o.get(TAG) for o in bpy.data.objects):
        raise RuntimeError('Regional ground already exists')
    source=Path(root)/'research/regional_context_ground_grid.json'
    grid=json.loads(source.read_text())
    if grid['spacing']!=50 or grid['extent']!=[-4500,-4500,4500,4500]:
        raise ValueError('Unexpected bounded regional grid')
    surfaces=[]
    xs=set(grid['x']);ys=set(grid['y'])
    for name,rect in MEASURED:
        obj=bpy.data.objects.get(name)
        if obj is None or obj.type!='MESH':
            raise ValueError('Create original measured terrain before regional context: '+name)
        surfaces.append((_surface(obj),rect))
        # Actual boundary vertex spacing lets the external sheet meet the
        # existing surface without modifying its elevation or topology.
        for v in obj.data.vertices:
            p=obj.matrix_world@v.co
            if abs(p.x-rect[0])<1e-4 or abs(p.x-rect[2])<1e-4:ys.add(round(p.y,5))
            if abs(p.y-rect[1])<1e-4 or abs(p.y-rect[3])<1e-4:xs.add(round(p.x,5))
        xs.update((rect[0],rect[2]));ys.update((rect[1],rect[3]))
    xs,ys=sorted(xs),sorted(ys)
    def in_measured(x,y):
        return any(a<=x<=c and b<=y<=d for _,(a,b,c,d) in MEASURED)
    transition_count=0;max_correction=0.;max_boundary_error=0.
    vertices=[]
    for y in ys:
        for x in xs:
            z=sample_grid(grid,x,y)
            closest=None
            for surface,(a,b,c,d) in surfaces:
                px,py=max(a,min(c,x)),max(b,min(d,y))
                distance=math.hypot(x-px,y-py)
                if distance<=SEAM_WIDTH and (closest is None or distance<closest[0]):
                    closest=(distance,surface,px,py,(a,b,c,d))
            if closest is not None:
                distance,surface,px,py,rect=closest
                hit,_,_,_=surface.ray_cast(Vector((px,py,100.)),Vector((0.,0.,-1.)))
                if hit is None:
                    # BVH edge rays can miss by float storage precision. A1mm
                    # inward fallback samples the same boundary neighborhood.
                    a,b,c,d=rect
                    ix=max(a+.001,min(c-.001,px));iy=max(b+.001,min(d-.001,py))
                    hit,_,_,_=surface.ray_cast(Vector((ix,iy,100.)),Vector((0.,0.,-1.)))
                if hit is None:raise RuntimeError(f'Measured boundary sampling missed at{x},{y} ->{px},{py}')
                t=distance/SEAM_WIDTH;smooth=t*t*(3.-2.*t)
                correction=(hit.z-sample_grid(grid,px,py))*(1.-smooth)
                z+=correction
                if not in_measured(x,y):
                    transition_count+=1;max_correction=max(max_correction,abs(correction))
                if distance<1e-7:max_boundary_error=max(max_boundary_error,abs(z-hit.z))
            vertices.append((x,y,z))
    faces=[];width=len(xs)
    for j in range(len(ys)-1):
        for i in range(width-1):
            if in_measured((xs[i]+xs[i+1])/2,(ys[j]+ys[j+1])/2):continue
            a=j*width+i
            # Match rendered ground raycasts to this exact fixed diagonal.
            faces.extend(((a,a+1,a+width+1),(a,a+width+1,a+width)))
    used=sorted({v for face in faces for v in face});remap={old:new for new,old in enumerate(used)}
    data=bpy.data.meshes.new('USGS regional terrain50m outside measured grids')
    data.from_pydata([vertices[i] for i in used],[],[tuple(remap[v] for v in f) for f in faces])
    data.materials.append(material);data.update()
    for face in data.polygons:face.use_smooth=True
    obj=bpy.data.objects.new('Regional context ground | USGS3DEP50m',data)
    collection.objects.link(obj);obj[TAG]=True
    obj['evidence_source']='research/regional_context_ground_grid.json'
    obj['evidence']='Bilinear50m regional DEM, outside-only75m boundary transition; original lidar meshes unchanged.'
    receipt={'source':obj['evidence_source'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'object':obj.name,'vertices':len(data.vertices),'triangles':len(data.polygons),'extent':grid['extent'],
        'source_spacing_m':50,'source_scene_z_range_m':grid['scene_z_range_m'],
        'measured_holes_xy_m':[rect for _,rect in MEASURED],
        'boundary_ray_inward_fallback_m':.001,'outside_transition_width_m':SEAM_WIDTH,'transition_vertices':transition_count,
        'max_outside_transition_correction_m':max_correction,'max_boundary_match_error_m':max_boundary_error,
        'rendered_min_z_m':min(v.co.z for v in data.vertices),'rendered_max_z_m':max(v.co.z for v in data.vertices),
        'scope':'Continuous DEM surface outside original measured meshes; no per-woodland platform or margin.'}
    return obj,_surface(obj),receipt
