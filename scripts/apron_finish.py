"""Clip interpreted sidewalk joints to the actual evaluated concrete surface.

Original geometry correction; MIT. No terrain-grid approximation, rendering,
master save, or changes to the apron, curb, roof or cameras.
"""
import json
import math

TAG = 'protolabs_apron_joint_finish'
MARGIN = .025
MAX_STEP = .10
CENTER_OFFSET = -.008  # Existing 10 mm radius exposes a 2 mm dark cap.


def _cross(a, b):
    return a[0]*b[1]-a[1]*b[0]


def _mix(a, b, t):
    return tuple(x+(y-x)*t for x,y in zip(a,b))


def _edge_distance(p, a, b):
    d=(b[0]-a[0],b[1]-a[1]);length2=sum(x*x for x in d)
    t=max(0.,min(1.,sum((p[i]-a[i])*d[i] for i in range(2))/length2))
    return math.dist(p,_mix(a,b,t))


def _events(a, b, p, q, margin=0.):
    """Segment parameters crossing an edge or its finite clearance capsule."""
    d=(b[0]-a[0],b[1]-a[1]);e=(q[0]-p[0],q[1]-p[1])
    length=math.hypot(*e);den=_cross(e,d);base=_cross(e,(a[0]-p[0],a[1]-p[1]))
    values=[]
    if abs(den)>1e-12:
        for side in (-margin,margin) if margin else (0.,):
            t=(side*length-base)/den;point=_mix(a,b,t)
            along=sum((point[i]-p[i])*e[i] for i in range(2))/(length*length)
            if 0.<=along<=1.:values.append(t)
    if margin:
        aa=sum(v*v for v in d)
        for c in (p,q):
            delta=(a[0]-c[0],a[1]-c[1]);bb=2*sum(delta[i]*d[i] for i in range(2))
            cc=sum(v*v for v in delta)-margin*margin;disc=bb*bb-4*aa*cc
            if disc>=0:
                values.extend(((-bb-math.sqrt(disc))/(2*aa),(-bb+math.sqrt(disc))/(2*aa)))
    return [t for t in values if 0.<t<1.]


def apply_apron_finish(root=None):
    """Return a receipt; replace only the ten existing joint curve data blocks."""
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    old=bpy.context.scene.get(TAG)
    if old:return json.loads(old)
    apron=bpy.data.objects.get('Entry concrete apron')
    joints=sorted((o for o in bpy.data.objects if o.name.startswith('Entry sidewalk expansion joint')),key=lambda o:o.name)
    if apron is None or apron.type!='MESH' or len(joints)!=10:
        raise ValueError('Expected the original apron and ten sidewalk joints')
    if any(o.type!='CURVE' or len(o.data.splines)!=1 or len(o.data.splines[0].points)!=2 or abs(o.data.bevel_depth-.01)>1e-6 for o in joints):
        raise ValueError('Joint inputs changed; inspect before applying surface correction')
    evaluated=apron.evaluated_get(bpy.context.evaluated_depsgraph_get())
    data=evaluated.to_mesh()
    try:
        data.calc_loop_triangles();vertices=[evaluated.matrix_world@v.co for v in data.vertices]
        faces=[];counts={}
        for tri in data.loop_triangles:
            a,b,c=[vertices[i] for i in tri.vertices]
            normal=(b-a).cross(c-a).normalized()
            if normal.z<=.5:continue
            face=tuple(tri.vertices);faces.append(face)
            for i,j in zip(face,face[1:]+face[:1]):
                key=tuple(sorted((i,j)));counts[key]=counts.get(key,0)+1
        if not faces:raise ValueError('Evaluated apron has no upward-facing top triangles')
        edges=[(tuple(vertices[i][:2]),tuple(vertices[j][:2])) for i,j in counts]
        boundary=[(tuple(vertices[i][:2]),tuple(vertices[j][:2])) for (i,j),count in counts.items() if count==1]
        if not boundary:raise ValueError('Evaluated apron has no top boundary')
        surface=BVHTree.FromPolygons(vertices,faces,all_triangles=True)
        ray_z=max(v.z for v in vertices)+1.
    finally:
        evaluated.to_mesh_clear()

    def hit(xy):
        p,_,_,_=surface.ray_cast(Vector((*xy,ray_z)),Vector((0,0,-1)))
        return p
    def supported(xy):
        return hit(xy) is not None and min(_edge_distance(xy,p,q) for p,q in boundary)>=MARGIN-1e-8

    prepared=[];rows=[]
    for obj in joints:
        original=[obj.matrix_world@Vector(p.co[:3]) for p in obj.data.splines[0].points]
        a,b=[tuple(p[:2]) for p in original];length=math.dist(a,b)
        if length<.01:raise ValueError('Degenerate sidewalk joint')
        events=[0.,1.]
        for p,q in boundary:events.extend(_events(a,b,p,q,MARGIN))
        events=sorted(set(round(t,12) for t in events));intervals=[]
        for start,end in zip(events,events[1:]):
            if end-start>1e-8 and supported(_mix(a,b,(start+end)/2)):
                if intervals and abs(intervals[-1][1]-start)<1e-9:intervals[-1]=(intervals[-1][0],end)
                else:intervals.append((start,end))
        if not intervals:raise ValueError('A complete joint lies outside the apron; review the interpretation')
        curve=obj.data.copy();curve.splines.clear();inverse=obj.matrix_world.inverted()
        retained=0.;point_count=0;min_clearance=float('inf');max_old_float=0.
        for start,end in intervals:
            steps=max(1,math.ceil((end-start)*length/MAX_STEP))
            ts=[start+(end-start)*i/steps for i in range(steps+1)]
            for p,q in edges:ts.extend(t for t in _events(a,b,p,q) if start<t<end)
            ts=sorted(set(round(t,12) for t in ts));spline=curve.splines.new('POLY');spline.points.add(len(ts)-1)
            for dst,t in zip(spline.points,ts):
                xy=_mix(a,b,t);point=hit(xy)
                if point is None:raise ValueError('Retained joint point missed evaluated apron')
                clearance=min(_edge_distance(xy,p,q) for p,q in boundary)
                if clearance<MARGIN-1e-6:raise ValueError('Joint does not clear the apron edge')
                min_clearance=min(min_clearance,clearance)
                max_old_float=max(max_old_float,_mix(tuple(original[0]),tuple(original[1]),t)[2]-point.z)
                point.z+=CENTER_OFFSET;dst.co=(*(inverse@point),1.)
            retained+=(end-start)*length;point_count+=len(ts)
        prepared.append((obj,curve))
        rows.append({'object':obj.name,'source_length_m':length,'retained_length_m':retained,
                     'splines':len(intervals),'points':point_count,'minimum_centerline_edge_clearance_m':min_clearance,
                     'old_centerline_max_height_above_top_m':max_old_float})
    for obj,curve in prepared:
        obj.data=curve;obj[TAG]=True
        obj['evidence']='Interpreted joint rhythm retained inside existing apron; evaluated top-triangle conformance, not a measured joint survey'
    report={'status':'applied','apron_object':apron.name,'source_joints':len(joints),
            'boundary_clearance_m':MARGIN,'maximum_sampling_step_m':MAX_STEP,
            'centerline_offset_from_actual_top_m':CENTER_OFFSET,'visible_joint_cap_height_m':.002,
            'evaluated_top_triangles':len(faces),'joints':rows,
            'scope':'Only ten curve data blocks replaced; original XY lines clipped inside evaluated apron; apron, curbs, other objects and materials unchanged'}
    bpy.context.scene[TAG]=json.dumps(report)
    bpy.context.view_layer.update()
    return report
