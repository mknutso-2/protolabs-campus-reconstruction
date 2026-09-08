"""Conform sidewalk joints and remove the rock slab overlapping the apron.

Original geometry correction; MIT. No terrain-grid approximation, rendering,
master save, or changes to the apron, curb, roof or cameras.
"""
import json
import math

TAG = 'protolabs_apron_joint_finish'
ROCK_TAG = 'protolabs_rock_bed_apron_subtraction'
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


def _subtract_rock_bed(apron):
    """Subtract a vertical prism of the evaluated apron outline from the rock slab.

    The source slabs both used nominal top Z .16 before different terrain
    triangulations, so they intersect. Keep the apron and every exposed rock
    triangle plane; the difference only removes rock inside the apron footprint.
    Temporary Boolean objects never persist in the generated scene.
    """
    import bpy
    import bmesh
    from mathutils import Vector

    rock=bpy.data.objects.get('Facade landscape river stones')
    if rock is None or rock.type!='MESH':raise ValueError('Expected original rock-bed slab')
    if rock.get(ROCK_TAG):return json.loads(rock[ROCK_TAG])
    deps=bpy.context.evaluated_depsgraph_get()
    evaluated=apron.evaluated_get(deps);data=evaluated.to_mesh()
    try:
        data.calc_loop_triangles();world=[evaluated.matrix_world@v.co for v in data.vertices]
        edges={}
        for tri in data.loop_triangles:
            a,b,c=[world[i] for i in tri.vertices]
            if (b-a).cross(c-a).normalized().z<=.5:continue
            face=tuple(tri.vertices)
            for i,j in zip(face,face[1:]+face[:1]):
                key=tuple(sorted((i,j)));edges[key]=edges.get(key,0)+1
        links={}
        for (i,j),count in edges.items():
            if count==1:links.setdefault(i,[]).append(j);links.setdefault(j,[]).append(i)
        if not links or any(len(v)!=2 for v in links.values()):raise ValueError('Apron outline is not one closed loop')
        first=min(links);loop=[first];previous=None;current=first
        while True:
            nxt=next(v for v in links[current] if v!=previous)
            if nxt==first:break
            if nxt in loop:raise ValueError('Apron boundary loops require explicit review')
            loop.append(nxt);previous,current=current,nxt
        if len(loop)!=len(links):raise ValueError('Multiple apron boundaries require explicit review')
        outline=[list(world[i][:2]) for i in loop]
        area=sum(_cross(a,b) for a,b in zip(outline,outline[1:]+outline[:1]))/2
        if area<0:outline.reverse()
    finally:
        evaluated.to_mesh_clear()

    evaluated=rock.evaluated_get(deps);data=evaluated.to_mesh()
    try:
        if data.uv_layers:raise ValueError('Rock UV mapping changed; preserve it explicitly before subtraction')
        data.calc_loop_triangles()
        # Use the exact existing tessellation, so exposed warped n-gons cannot
        # acquire different diagonals/elevations merely from Boolean processing.
        vertices=[tuple(v.co) for v in data.vertices]
        faces=[tuple(t.vertices) for t in data.loop_triangles]
        material_indices=[data.polygons[t.polygon_index].material_index for t in data.loop_triangles]
        materials=list(rock.data.materials)
        zs=[(rock.matrix_world@v.co).z for v in data.vertices]
    finally:
        evaluated.to_mesh_clear()
    prepared=bpy.data.meshes.new('Rock bed exact original tessellation')
    prepared.from_pydata(vertices,[],faces)
    for material in materials:prepared.materials.append(material)
    for face,index in zip(prepared.polygons,material_indices):face.material_index=index
    prepared.update()
    bm=bmesh.new();bm.from_mesh(prepared)
    original_volume=bm.calc_volume(signed=True)
    original_closed=all(e.is_manifold and e.is_contiguous for e in bm.edges);bm.free()
    if not original_closed or original_volume<=0:
        bpy.data.meshes.remove(prepared)
        raise ValueError('Original rock slab must be closed and outward-facing')
    low,high=min(zs)-1.,max(zs)+1.;n=len(outline)
    cutter_data=bpy.data.meshes.new('Temporary apron footprint prism')
    cutter_data.from_pydata([(x,y,z) for z in (low,high) for x,y in outline],[],
        [tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
    cutter_data.update()
    collection=rock.users_collection[0]
    cutter=bpy.data.objects.new('Temporary apron footprint subtraction',cutter_data);collection.objects.link(cutter)
    temporary=bpy.data.objects.new('Temporary exact rock difference',prepared);collection.objects.link(temporary)
    temporary.matrix_world=rock.matrix_world
    result_data=None
    try:
        modifier=temporary.modifiers.new('Subtract actual apron footprint','BOOLEAN')
        modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
        bpy.context.view_layer.update()
        result_data=bpy.data.meshes.new_from_object(temporary.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        result_data.name='Rock bed outside actual apron footprint'
        result_data.materials.clear()
        for material in materials:result_data.materials.append(material)
        bm=bmesh.new();bm.from_mesh(result_data)
        closed=bool(bm.faces) and all(e.is_manifold and e.is_contiguous for e in bm.edges)
        volume=bm.calc_volume(signed=True)
        components=[];unseen=set(bm.faces)
        while unseen:
            pending=[unseen.pop()];component=[]
            while pending:
                face=pending.pop();component.append(face)
                for edge in face.edges:
                    for neighbor in edge.link_faces:
                        if neighbor in unseen:unseen.remove(neighbor);pending.append(neighbor)
            # Closed components must each retain positive signed volume.
            signed=0.
            for face in component:
                points=[v.co for v in face.verts]
                for i in range(1,len(points)-1):signed+=points[0].dot(points[i].cross(points[i+1]))/6
            components.append(signed)
        bm.free()
        if not closed or not 0<volume<original_volume or any(v<=0 for v in components):
            raise ValueError('Rock subtraction failed closed/outward/removed-volume checks')
        report={'status':'applied','rock_object':rock.name,'apron_object':apron.name,
            'outline_xy_m':outline,'method':'Exact Boolean difference of existing rock triangles and vertical evaluated-apron outline prism',
            'original_volume_local_m3':original_volume,'retained_volume_local_m3':volume,
            'closed_outward_components':len(components),'component_signed_volumes_local_m3':components,
            'vertices':len(result_data.vertices),'polygons':len(result_data.polygons),
            'scope':'Rock slab inside apron footprint removed; apron and exposed rock triangle planes/materials/transforms retained; no global lowering'}
        rock.data=result_data;rock[ROCK_TAG]=json.dumps(report)
        rock['evidence']='Original inferred rock bed minus existing apron footprint; resolves intersecting coplanar slabs without relocating exposed planting'
    except Exception:
        if result_data is not None and result_data.users==0:bpy.data.meshes.remove(result_data)
        raise
    finally:
        temporary.modifiers.clear()
        bpy.context.view_layer.update()
        bpy.data.objects.remove(temporary,do_unlink=True);bpy.data.objects.remove(cutter,do_unlink=True)
        # Flush evaluated Boolean dependencies before freeing their source meshes.
        # Blender 4.2 can still reference these meshes until relations update.
        bpy.context.view_layer.update()
        if prepared.users==0:bpy.data.meshes.remove(prepared)
        if cutter_data.users==0:bpy.data.meshes.remove(cutter_data)
    return report


def apply_apron_finish(root=None):
    """Correct ten joint curves and subtract their apron from the rock-bed slab."""
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    apron=bpy.data.objects.get('Entry concrete apron')
    if apron is None or apron.type!='MESH':raise ValueError('Expected original apron')
    rock_report=_subtract_rock_bed(apron)
    old=bpy.context.scene.get(TAG)
    if old:
        report=json.loads(old);report['rock_bed_subtraction']=rock_report
        bpy.context.scene[TAG]=json.dumps(report)
        return report
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
            'rock_bed_subtraction':rock_report,
            'scope':'Ten joint curves corrected and overlapping rock bed subtracted; apron, curbs, other objects and materials unchanged'}
    bpy.context.scene[TAG]=json.dumps(report)
    bpy.context.view_layer.update()
    return report
