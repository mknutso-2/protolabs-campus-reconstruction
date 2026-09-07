"""Correct only four entrance parking rows from recorded aerial paint boundaries.

Original derived geometry; MIT. Photographs remain research inputs, never textures.
"""
import hashlib
import json
import math
from pathlib import Path

TAG = 'protolabs_entrance_parking_correction'


def _mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def _rounded(points, radius):
    result = []
    for i, p in enumerate(points):
        prev, nxt = points[i-1], points[(i+1) % len(points)]
        d = min(radius, math.dist(prev, p)*.22, math.dist(p, nxt)*.22)
        a = _mix(p, prev, d/math.dist(prev, p))
        b = _mix(p, nxt, d/math.dist(nxt, p))
        for j in range(5):
            t = j/4
            result.append(tuple((1-t)**2*a[k] + 2*(1-t)*t*p[k] + t*t*b[k] for k in range(2)))
    return result


def _hatches(polygon, direction, spacing):
    length = math.hypot(*direction)
    d = tuple(v/length for v in direction)
    n = (-d[1], d[0])
    across = [sum(p[i]*n[i] for i in range(2)) for p in polygon]
    for index in range(math.ceil(min(across)/spacing), math.floor(max(across)/spacing)+1):
        k = index*spacing
        hits = []
        for a, b in zip(polygon, polygon[1:]+polygon[:1]):
            qa, qb = sum(a[i]*n[i] for i in range(2)), sum(b[i]*n[i] for i in range(2))
            if (qa > k) == (qb > k):
                continue
            point = _mix(a, b, (k-qa)/(qb-qa))
            hits.append(sum(point[i]*d[i] for i in range(2)))
        hits.sort()
        for low, high in zip(hits[::2], hits[1::2]):
            if high-low > 1:
                yield [(n[0]*k+d[0]*t, n[1]*k+d[1]*t) for t in (low+.3, high-.3)]


def marking_paths(record):
    """Return (label, pixel polyline) pairs; pure Python for plan/projection QA."""
    paths = []
    dividers = []
    for row in record['rows']:
        left, right = row['boundary_x_px']
        for i in range(row['bay_count']+1):
            y = row['first_divider_y_px'] + (row['last_divider_y_px']-row['first_divider_y_px'])*i/row['bay_count']
            segment = [(left,y),(right,y)]
            paths.append((row['source_row_id']+' divider '+str(i), segment))
            dividers.append((left,right,y))
    for i, segment in enumerate(record['center_lines_px']):
        paths.append(('Shared row center '+str(i),segment))
    for cap in record['hatched_ends']:
        poly = _rounded(cap['points_px'], cap['corner_rounding_px'])
        for i, (a,b) in enumerate(zip(poly, poly[1:]+poly[:1])):
            if math.dist(a,b)<.001:
                continue
            # Omit horizontal cap-border portions already painted by dividers.
            covered = False
            if abs(a[1]-b[1])<1e-7:
                intervals=sorted((lo,hi) for lo,hi,y in dividers if abs(y-a[1])<1e-7)
                cursor=min(a[0],b[0])
                for lo,hi in intervals:
                    if lo<=cursor+1e-7:cursor=max(cursor,hi)
                covered=cursor>=max(a[0],b[0])-1e-7
            if not covered:paths.append((cap['id']+' border '+str(i),[a,b]))
        for i, segment in enumerate(_hatches(poly,record['hatch_direction_image'],record['hatch_normal_spacing_px'])):
            paths.append((cap['id']+' hatch '+str(i),segment))
    return paths


def _pixel_to_local(layout, point, origin):
    extent=layout['extent'];width,height=layout['image_size_px']
    return (extent['xmin']+point[0]/width*(extent['xmax']-extent['xmin'])-origin[0],
            extent['ymax']-point[1]/height*(extent['ymax']-extent['ymin'])-origin[1])


def _ground_sampler(terrain):
    tx,ty,tz=terrain['x'],terrain['y'],terrain['z']
    def ground(x,y):
        fx=max(0,min(len(tx)-1.001,(x-tx[0])/(tx[1]-tx[0])))
        fy=max(0,min(len(ty)-1.001,(y-ty[0])/(ty[1]-ty[0])))
        ix,iy=int(fx),int(fy);u,v=fx-ix,fy-iy
        return (tz[iy][ix]*(1-u)+tz[iy][ix+1]*u)*(1-v)+(tz[iy+1][ix]*(1-u)+tz[iy+1][ix+1]*u)*v
    return ground


def _inside(point, polygon):
    x,y=point;inside=False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            inside=not inside
    return inside


def _clip_outside(a, b, polygons, clearance):
    """Split a segment at polygon boundaries; preserve only outside intervals."""
    direction=(b[0]-a[0],b[1]-a[1]);length=math.hypot(*direction)
    cross=lambda u,v:u[0]*v[1]-u[1]*v[0]
    ts=[0.,1.]
    for polygon in polygons:
        for p,q in zip(polygon,polygon[1:]+polygon[:1]):
            edge=(q[0]-p[0],q[1]-p[1]);den=cross(direction,edge)
            if abs(den)<1e-12:continue
            delta=(p[0]-a[0],p[1]-a[1]);t=cross(delta,edge)/den;u=cross(delta,direction)/den
            if 0<=t<=1 and 0<=u<=1:ts.append(t)
    ts=sorted(set(round(t,12) for t in ts))
    for start,end in zip(ts,ts[1:]):
        if any(_inside(_mix(a,b,(start+end)*.5),p) for p in polygons):continue
        # Stop the full paint width short of the curb, not merely its centerline.
        if start>0:start+=clearance/length
        if end<1:end-=clearance/length
        if end>start:yield [_mix(a,b,start),_mix(a,b,end)]


def apply_parking_finish(root):
    """Replace 38 matched row stripes and clip 10 legacy aisle hatches at the apron.

    Invoke after site stripe generation, before saving/exporting. The paint uses
    the existing material, so the later material-quality pass remains applicable.
    Returns a serializable report and never saves the scene or writes files.
    """
    import bpy
    from mathutils import Vector
    root=Path(root)
    source=root/'research/entrance-parking-correction.json'
    raw=source.read_bytes();record=json.loads(raw)
    source_hash=hashlib.sha256(raw).hexdigest()
    existing=[o for o in bpy.data.objects if o.get(TAG)]
    if existing:
        if len(existing)==1 and existing[0].get('parking_record_sha256')==source_hash:
            return {'status':'already_applied','object':existing[0].name,'source_sha256':source_hash}
        raise ValueError('Existing parking correction differs; rebuild the scene')
    layout_path=root/record['source_layout']
    if hashlib.sha256(layout_path.read_bytes()).hexdigest()!=record['source_layout_sha256']:
        raise ValueError('Parking source layout changed; recheck the derived trace')
    layout=json.loads(layout_path.read_text())
    terrain=json.loads((root/'research/terrain_grid.json').read_text())
    origin=terrain['origin_utm_m'];ground=_ground_sampler(terrain)
    pixel=lambda p:_pixel_to_local(layout,p,origin)
    row_ids={r['source_row_id'] for r in record['rows']}
    expected=[]
    for row in layout['parking_rows']:
        if row['id'] not in row_ids:continue
        a,b=[pixel(q) for q in row['car_centerline_px']]
        count=row['estimated_bays'];step=tuple((b[i]-a[i])/(count-1) for i in range(2))
        heading=row['vehicle_heading_image'];norm=math.hypot(*heading)
        hd=(heading[0]/norm,-heading[1]/norm)
        depth=row['bay_depth_px']*(layout['extent']['xmax']-layout['extent']['xmin'])/layout['image_size_px'][0]
        for i in range(count+1):
            center=tuple(a[k]+step[k]*(i-.5) for k in range(2))
            expected.append((tuple(center[k]-hd[k]*depth*.5 for k in range(2)),
                             tuple(center[k]+hd[k]*depth*.5 for k in range(2))))
    matched={}
    for obj in bpy.data.objects:
        if obj.type!='CURVE' or not obj.name.startswith('Traced parking stripe') or len(obj.data.splines)!=1:continue
        points=obj.data.splines[0].points
        ends=[tuple((obj.matrix_world@Vector(p.co[:3]))[:2]) for p in (points[0],points[-1])]
        for i,(a,b) in enumerate(expected):
            if min(max(math.dist(ends[0],a),math.dist(ends[1],b)),
                   max(math.dist(ends[0],b),math.dist(ends[1],a)))<.002:
                if i in matched:raise ValueError('Duplicate legacy parking stripe found')
                matched[i]=obj
    if len(expected)!=38 or len(matched)!=len(expected):
        raise ValueError(f'Expected 38 legacy entrance stripes; matched {len(matched)}')
    collection=bpy.data.collections.get('Site | aerial trace')
    paint=bpy.data.materials.get('Faded parking paint')
    if collection is None or paint is None:raise ValueError('Site collection or paint material is missing')
    # The separate hard-coded hatch crosses the actual entry apron. Keep its
    # original direction/location outside that mesh and mark this as inferred.
    apron=bpy.data.objects.get('Entry concrete apron')
    if apron is None or apron.type!='MESH':raise ValueError('Entry concrete apron mesh is missing')
    broad_faces=[p for p in apron.data.polygons if len(p.vertices)>3 and abs(p.normal.z)>.8]
    if not broad_faces:raise ValueError('Entry apron topology changed; inspect its footprint before clipping')
    face=max(broad_faces,key=lambda p:len(p.vertices))
    footprint=[tuple((apron.matrix_world@apron.data.vertices[i].co)[:2]) for i in face.vertices]
    aisle_sources=[o for o in bpy.data.objects if o.name.startswith('Accessible access aisle hatch')]
    if len(aisle_sources)!=10 or any(o.type!='CURVE' or len(o.data.splines)!=1 or len(o.data.splines[0].points)!=2 for o in aisle_sources):
        raise ValueError('Expected ten original access-aisle hatch curves')
    aisle_paths=[]
    for old in aisle_sources:
        a,b=[tuple((old.matrix_world@Vector(p.co[:3]))[:2]) for p in old.data.splines[0].points]
        for segment in _clip_outside(a,b,[footprint],record['paint_width_m']*.5+.03):
            aisle_paths.append((old.name,segment))
    vertices=[];faces=[];paths=marking_paths(record)
    half=record['paint_width_m']*.5;offset=record['paint_ground_offset_m']
    local_paths=[(label,[pixel(p) for p in points]) for label,points in paths]+aisle_paths
    for label,local in local_paths:
        for a,b in zip(local,local[1:]):
            length=math.dist(a,b)
            if length<.001:continue
            normal=(-(b[1]-a[1])/length*half,(b[0]-a[0])/length*half)
            steps=max(1,math.ceil(length/.75))
            for i in range(steps):
                p,q=_mix(a,b,i/steps),_mix(a,b,(i+1)/steps)
                corners=[(p[0]-normal[0],p[1]-normal[1]),(q[0]-normal[0],q[1]-normal[1]),
                         (q[0]+normal[0],q[1]+normal[1]),(p[0]+normal[0],p[1]+normal[1])]
                start=len(vertices)
                vertices.extend((x,y,ground(x,y)+offset) for x,y in corners)
                faces.append(tuple(range(start,start+4)))
    mesh=bpy.data.meshes.new('Evidence-corrected entrance paint mesh')
    mesh.from_pydata(vertices,[],faces);mesh.materials.append(paint);mesh.update()
    obj=bpy.data.objects.new('Evidence-corrected entrance parking paint',mesh);collection.objects.link(obj)
    obj[TAG]=True;obj['parking_record_sha256']=source_hash
    obj['evidence']='Manual aerial paint trace; four entrance rows only; approximate worn geometry, not a site survey'
    removed=[o.name for o in matched.values()]
    for old in matched.values():bpy.data.objects.remove(old,do_unlink=True)
    aisle_names=[o.name for o in aisle_sources]
    for old in aisle_sources:bpy.data.objects.remove(old,do_unlink=True)
    return {'status':'applied','source':'research/entrance-parking-correction.json','source_sha256':source_hash,
            'removed_legacy_stripes':removed,'removed_count':len(removed),'replacement_object':obj.name,
            'paint_paths':len(local_paths),'paint_triangles':len(faces)*2,'rendered_bays':[r['bay_count'] for r in record['rows']],
            'access_aisle':{'source_curve_names':aisle_names,'clip_footprint_object':apron.name,
                            'retained_paths_xy_m':[p for _,p in aisle_paths],'curb_clearance_m':half+.03,
                            'status':'Original inferred hatch outside actual apron footprint; no surveyed access-aisle claim'},
            'scope':record['scope']}
