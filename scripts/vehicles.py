"""Original procedural generic vehicles for site visualization.

License: MIT. Copyright (c) 2026 Reconstruction contributors.
No downloaded vehicle geometry, manufacturer designs, badges or textures are used.
Public entry point: create_vehicle_asset(name, color=(.22,.28,.33), variant='sedan').
Returns ONE mesh object with applied modifiers and ground-centered origin.
Coordinates are meters; +Y is forward; +Z is up; minimum Z is 0.
"""
import math
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def _material(name, color, metallic=0.0, roughness=.4, emission=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
    # The caller supplies ordinary sRGB paint swatches; Blender node values are linear.
    rgba = tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
                 for c in color[:3]) + (1.0,)
    mat.diffuse_color = rgba
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = rgba
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    if 'Coat Weight' in bs.inputs:
        bs.inputs['Coat Weight'].default_value = .65 if 'paint' in name else .10
        bs.inputs['Coat Roughness'].default_value = .16
    bs.inputs['Emission Color'].default_value = rgba
    bs.inputs['Emission Strength'].default_value = emission
    return mat


def _mesh(name, vertices, faces, material, parts, bevel=0.0):
    data = bpy.data.meshes.new(name + '_mesh')
    data.from_pydata(vertices, [], faces)
    # Closed components get consistent outward face winding before bevel/Boolean work.
    bm = bmesh.new(); bm.from_mesh(data)
    if bm.edges and all(e.is_manifold for e in bm.edges):
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        if bm.calc_volume(signed=True) < 0:
            bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
        bm.to_mesh(data)
    bm.free()
    data.materials.append(material)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    parts.append(obj)
    if bevel:
        mod = obj.modifiers.new('Small manufactured edge radii', 'BEVEL')
        mod.width = bevel
        mod.segments = 4
        mod.affect = 'EDGES'
        mod.limit_method = 'ANGLE'
        mod.angle_limit = .40
        mod.harden_normals = True
    return obj


def _box(name, center, dimensions, material, parts, bevel=0.0):
    x, y, z = center
    a, b, c = [v / 2 for v in dimensions]
    vv = [(x+sx*a, y+sy*b, z+sz*c)
          for sz in [-1,1] for sy in [-1,1] for sx in [-1,1]]
    ff = [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    return _mesh(name, vv, ff, material, parts, bevel)


def _rod(name, a, b, radius, material, parts, vertices=8):
    a, b = Vector(a), Vector(b)
    d = b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                       depth=d.length, location=(a+b)*.5)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    ob.data.materials.append(material)
    parts.append(ob)
    return ob


def _wheel(name, x, y, radius, tire, alloy, dark, parts):
    # Rounded 48-sided tire barrel. Recessed rim lip and split spokes are separate
    # surfaces, so the wheel reads as rubber around an alloy wheel, not a flat disk.
    sign = 1 if x > 0 else -1
    rim = radius * .665
    profiles = [(-.113, rim),(-.117,radius*.86),(-.097,radius*.975),
                (-.072,radius),(.072,radius),(.097,radius*.975),
                (.117,radius*.86),(.113,rim)]
    n = 48
    vv=[]
    for xx,r in profiles:
        vv.extend([(x+xx,y+math.cos(j*math.tau/n)*r,radius+math.sin(j*math.tau/n)*r)
                   for j in range(n)])
    ff=[]
    for k in range(len(profiles)-1):
        for j in range(n):
            ff.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
    # Close inner walls around axle. Rim disks cover the center aperture.
    for j in range(n):
        ff.append((j,(len(profiles)-1)*n+j,(len(profiles)-1)*n+(j+1)%n,(j+1)%n))
    ob=_mesh(name+'_rubber',vv,ff,tire,parts)
    for face in ob.data.polygons: face.use_smooth=True
    outer=x+sign*.117
    _rod(name+'_rim',(outer-sign*.035,y,radius),(outer,y,radius),rim,alloy,parts,48)
    _rod(name+'_recess',(outer,y,radius),(outer+sign*.004,y,radius),rim*.88,dark,parts,48)
    _rod(name+'_brake_disc',(outer+sign*.006,y,radius),(outer+sign*.008,y,radius),rim*.74,alloy,parts,32)
    _rod(name+'_hub_recess',(outer+sign*.009,y,radius),(outer+sign*.010,y,radius),rim*.63,dark,parts,32)
    # Paired tapered spokes, a central hub and five recessed fasteners.
    for k in range(5):
        theta=k*math.tau/5+.2
        for offset in [-.095,.095]:
            aa=theta+offset
            p=(outer+sign*.018,y+math.cos(aa)*rim*.92,radius+math.sin(aa)*rim*.92)
            q=(outer+sign*.028,y+math.cos(theta)*.045,radius+math.sin(theta)*.045)
            _rod(name+'_split_spoke%d'%k,q,p,.015,alloy,parts,6)
        py=y+math.cos(theta)*.039; pz=radius+math.sin(theta)*.039
        _rod(name+'_lug',(outer+sign*.031,py,pz),(outer+sign*.037,py,pz),.009,dark,parts,6)
    _rod(name+'_hub',(outer+sign*.01,y,radius),(outer+sign*.030,y,radius),.057,alloy,parts,24)


def _inset_quad(name, corners, material, parts, inset=.075, normal_offset=.006):
    v=[Vector(q) for q in corners]
    center=sum(v,Vector())/len(v)
    normal=(v[1]-v[0]).cross(v[2]-v[0]).normalized()
    # Named face corner winding points outward.
    v=[center+(q-center)*(1-inset)+normal*normal_offset for q in v]
    # Gently compound-curved glazing with a closed 6 mm backing; the side faces
    # retain a narrow body-colored surround and the glass reflects continuously.
    nx, ny = 12, 6
    points=[]; faces=[]
    for j in range(ny+1):
        t=j/ny
        for i in range(nx+1):
            u=i/nx
            q=v[0].lerp(v[1],u).lerp(v[3].lerp(v[2],u),t)
            q+=normal*(.021*math.sin(math.pi*u)*math.sin(math.pi*t))
            points.append(tuple(q))
    for j in range(ny):
        for i in range(nx):
            k=j*(nx+1)+i; faces.append((k,k+1,k+nx+2,k+nx+1))
    ob=_mesh(name,points,faces,material,parts)
    for face in ob.data.polygons: face.use_smooth=True
    mod=ob.modifiers.new('Glazing thickness','SOLIDIFY');mod.thickness=.006;mod.offset=-1
    return ob


def _catmull(values, steps, closed=False):
    """Bounded smooth samples through a profile; no external geometry assets."""
    points=[Vector(v) for v in values];result=[]
    end=len(points) if closed else len(points)-1
    at=lambda i:points[i%len(points)] if closed else points[min(max(i,0),len(points)-1)]
    for i in range(end):
        p0,p1,p2,p3=[at(i+j) for j in (-1,0,1,2)]
        for k in range(steps):
            t=k/steps
            result.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    if not closed:result.append(points[-1])
    return result


def _apply_modifiers(obj):
    bpy.context.view_layer.objects.active=obj
    for mod in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)


def _front_lamp(name, side, z, material, parts, body):
    # Lamp follows the front corner taper instead of sitting as a luminous box
    # on the hood. Parked vehicles have reflective lenses, with no emitted light.
    surface=BVHTree.FromPolygons([v.co for v in body.data.vertices],
        [list(f.vertices) for f in body.data.polygons],all_triangles=False)
    xmin,xmax=sorted([side*.28,side*.80]);nx,ny=16,4;vertices=[];faces=[]
    for j in range(ny+1):
        t=j/ny
        for i in range(nx+1):
            u=i/nx;x=xmin+(xmax-xmin)*u
            zz=z+(t-.5)*(.082-.026*abs(x)/.8)
            hit,normal,_,_=surface.ray_cast(Vector((x,3,zz)),Vector((0,-1,0)))
            if hit is None:raise RuntimeError('Lamp projection missed vehicle body')
            vertices.append((x,hit.y+.012,zz))
    for j in range(ny):
        for i in range(nx):
            k=j*(nx+1)+i;faces.append((k,k+nx+1,k+nx+2,k+1))
    ob=_mesh(name,vertices,faces,material,parts)
    for f in ob.data.polygons:f.use_smooth=True
    mod=ob.modifiers.new('Closed reflector lens','SOLIDIFY');mod.thickness=.008;mod.offset=-1
    return ob


def _wheel_arches(body, radius, parts):
    """Cut real, rounded wheel apertures through the hull at both axles."""
    _apply_modifiers(body)
    for axle in [-1.47,1.47]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius+.073,depth=2.8,
            location=(0,axle,radius),rotation=(0,math.pi/2,0))
        cutter=bpy.context.object;cutter.name='Temporary wheel aperture cutter'
        bpy.context.view_layer.objects.active=body
        mod=body.modifiers.new('Physical wheel aperture','BOOLEAN');mod.operation='DIFFERENCE'
        mod.solver='EXACT';mod.object=cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
    for face in body.data.polygons:face.use_smooth=True
    mod=body.modifiers.new('Wheel aperture paint lip','BEVEL');mod.width=.009
    mod.segments=2;mod.limit_method='ANGLE';mod.angle_limit=.65;mod.harden_normals=True
    mod=body.modifiers.new('Area weighted body normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=30


def create_vehicle_asset(name, color=(.22,.28,.33), variant='sedan'):
    """Create an original generic sedan or compact SUV as ONE joined mesh.

    Approximate sedan bounds: 4.66 m long, 2.24 m including mirrors, 1.52 m high.
    Compact SUV: 4.66 m long, 2.24 m including mirrors, 1.85 m high.
    Both have about 1.9 m body width. Each mesh stays below 30,000 triangles.
    Reuse obj.data for linked parking instances. No other objects remain created.
    """
    variant=variant.lower()
    if variant not in ('sedan','suv','compact_suv'):
        raise ValueError("variant must be 'sedan' or 'suv' / 'compact_suv'")
    suv=variant!='sedan'
    parts=[]
    key='_'.join('%03d'%max(0,min(255,round(c*255))) for c in color[:3])
    paint=_material('Generic_vehicle_paint_'+key,color,.48,.245)
    glass=_material('Generic_vehicle_blue_black_glass',(.075,.11,.135),.05,.105)
    rubber=_material('Generic_vehicle_tire_rubber',(.07,.073,.077),0,.72)
    trim=_material('Generic_vehicle_charcoal_trim',(.10,.115,.125),.05,.44)
    chrome=_material('Generic_vehicle_satin_alloy',(.63,.65,.68),.90,.24)
    lamps=_material('Generic_vehicle_headlamp',(.68,.73,.77),.28,.17)
    red=_material('Generic_vehicle_taillamp',(.42,.016,.010),.10,.22)
    amber=_material('Generic_vehicle_indicator',(.84,.29,.025),.10,.25)
    plate=_material('Generic_vehicle_blank_plate',(.68,.70,.67),.08,.55)
    # Dense smooth loft, including crown and bumper taper. +Y is the nose.
    sections=[(-2.28,.67,.88),(-2.24,.77,.92),(-2.10,.87,.98),
              (-1.52,.94,1.055),(-.75,.935,1.06),(.42,.935,1.07),
              (1.30,.935,1.035),(1.94,.89,.96),(2.23,.76,.88),(2.30,.63,.80)]
    if suv:
        sections=[(y,w*1.015,z+.13) for y,w,z in sections]
    sections=_catmull(sections,3)
    vv=[]
    for y,w,z in sections:
        cross=[(-w*.77,.37),(-w*.92,.40),(-w*.99,.53),(-w,.76),
               (-w*.98,z-.10),(-w*.86,z),(-w*.45,z+.033),(0,z+.045),
               (w*.45,z+.033),(w*.86,z),(w*.98,z-.10),(w,.76),
               (w*.99,.53),(w*.92,.40),(w*.77,.37),(0,.365)]
        vv.extend([(x,y,zz) for x,zz in _catmull(cross,2,closed=True)])
    n=32
    ff=[tuple(reversed(range(n)))]
    for k in range(len(sections)-1):
        for j in range(n): ff.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
    ff.append(tuple((len(sections)-1)*n+j for j in range(n)))
    body=_mesh(name+'_body',vv,ff,paint,parts)
    radius=.36 if suv else .335
    _wheel_arches(body,radius,parts)
    # Dark rocker strips and bumpers reveal tire clearance and lower silhouette.
    _box(name+'_underbody',(0,0,.37),(1.48,3.72,.18),trim,parts,.035)
    for side in [-1,1]:
        _box(name+'_rocker',(side*.916,-.02,.435),(.035,1.94,.10),trim,parts,.025)
    _box(name+'_front_bumper',(0,2.24,.58),(1.45,.17,.19),trim,parts,.05)
    _box(name+'_rear_bumper',(0,-2.22,.59),(1.49,.14,.15),trim,parts,.04)
    # Colored cabin shell; inset windows supply distinct A/B/C pillars and frames.
    if suv:
        rear_base,front_base=-1.84,1.13
        rear_top,front_top=-1.36,.43
        zbase,ztop=1.16,1.76
        wbase,wtop=.865,.715
    else:
        rear_base,front_base=-1.52,1.05
        rear_top,front_top=-.79,.23
        zbase,ztop=1.06,1.52
        wbase,wtop=.84,.685
    cabin=[(-wbase,rear_base,zbase),(wbase,rear_base,zbase),
           (wbase,front_base,zbase),(-wbase,front_base,zbase),
           (-wtop,rear_top,ztop),(wtop,rear_top,ztop),
           (wtop,front_top,ztop),(-wtop,front_top,ztop)]
    shell=_mesh(name+'_cabin',cabin,[(0,1,5,4),(1,2,6,5),(2,3,7,6),
        (3,0,4,7),(4,5,6,7),(3,2,1,0)],paint,parts,.072)
    for face in shell.data.polygons:face.use_smooth=True
    mod=shell.modifiers.new('Stable cabin highlight normals','WEIGHTED_NORMAL');mod.keep_sharp=True
    _inset_quad(name+'_rear_window',[cabin[i] for i in [0,1,5,4]],glass,parts,.19,.015)
    _inset_quad(name+'_windshield',[cabin[i] for i in [2,3,7,6]],glass,parts,.16,.016)
    # Two curved roof crown panels create a shallow continuous highlight, with
    # the upper silhouette softened across both width and longitudinal direction.
    roof=[cabin[i] for i in [4,5,6,7]]
    _inset_quad(name+'_roof_crown',roof,paint,parts,.065,.011)
    # Side windows split at B-pillar, with actual side slope following cabin.
    for side in [-1,1]:
        x0=side*wbase
        x1=side*wtop
        split_y=-.38 if suv else -.36
        back=[(x0,rear_base,zbase),(x0,split_y-.028,zbase),
              (x1,split_y-.028,ztop),(x1,rear_top,ztop)]
        front=[(x0,split_y+.028,zbase),(x0,front_base,zbase),
               (x1,front_top,ztop),(x1,split_y+.028,ztop)]
        if side<0: back.reverse();front.reverse()
        _inset_quad(name+'_rear_side_glass',back,glass,parts,.17,.014)
        _inset_quad(name+'_front_side_glass',front,glass,parts,.15,.014)
        # Door handles and clean, modest seam at B pillar.
        for yy in [-.79,.34]:
            _box(name+'_door_handle',(side*.938,yy,zbase-.09),(.018,.16,.025),paint,parts,.01)
        _rod(name+'_door_seam',(side*.942,split_y,.57),(side*.927,split_y,zbase-.03),.0035,trim,parts,6)
        # Mirror stalk + body. Mirror width included in total bounds, body remains ~1.85m.
        _rod(name+'_mirror_stalk',(side*.83,.72,zbase+.02),(side*1.00,.75,zbase+.05),.025,trim,parts,6)
        _box(name+'_mirror',(side*1.014,.75,zbase+.09),(.21,.22,.125),paint,parts,.047)
        _box(name+'_mirror_glass',(side*1.016,.636,zbase+.09),(.145,.015,.075),glass,parts,.01)
    # Front fascia, split headlamps, grille slots, blank plates; no brand badges.
    zlight=.91+(.13 if suv else 0)
    for side in [-1,1]:
        _front_lamp(name+'_headlight',side,.795+(.13 if suv else 0),lamps,parts,body)
        _box(name+'_front_indicator',(side*.790,2.176,zlight-.106),(.035,.025,.052),amber,parts,.010)
        _box(name+'_taillight',(side*.64,-2.188,zlight),(.30,.065,.16),red,parts,.023)
        _box(name+'_reverse_light',(side*.52,-2.225,zlight),(.06,.02,.045),lamps,parts,.008)
    _box(name+'_grille',(0,2.302,.75+(.1 if suv else 0)),(.68,.019,.19),trim,parts,.025)
    for z in [.71,.765,.82]:
        _box(name+'_grille_slat',(0,2.316,z+(.1 if suv else 0)),(.63,.012,.012),chrome,parts)
    _box(name+'_front_plate',(0,2.34,.58),(.40,.022,.12),plate,parts,.009)
    _box(name+'_rear_plate',(0,-2.295,.74),(.40,.025,.12),plate,parts,.01)
    # Four road wheels, with exposed silver hubs and profiled rubber sidewalls.
    for side in [-1,1]:
        for yy in [-1.47,1.47]:
            _wheel(name+'_wheel',side*.927,yy,radius,rubber,chrome,trim,parts)
    if suv:
        # Discreet roof rails support SUV silhouette without brand-specific details.
        for side in [-1,1]:
            _rod(name+'_roof_rail',(side*.61,-1.18,ztop+.065),(side*.61,.22,ztop+.065),.023,chrome,parts,8)
            for yy in [-1.13,.17]:
                _box(name+'_rail_foot',(side*.61,yy,ztop+.023),(.09,.12,.05),trim,parts,.012)
    # Bake only created parts. Preserve unrelated objects in caller scene.
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:
        ob.select_set(True)
        bpy.context.view_layer.objects.active=ob
        _apply_modifiers(ob)
    bpy.context.view_layer.objects.active=body
    bpy.ops.object.join()
    joined=bpy.context.object
    joined.name=name
    joined.data.name=name+'_mesh'
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    # Body is created in world-origin coordinates. Make root strictly identity and
    # shift tire low point to ground; centering concerns wheelbase/length, not mirrors.
    minz=min(v.co.z for v in joined.data.vertices)
    for vertex in joined.data.vertices: vertex.co.z-=minz
    joined.location=(0,0,0)
    joined.rotation_euler=(0,0,0)
    joined.scale=(1,1,1)
    joined.data.update()
    # All parts are closed after glazing solidification. Recompute consistent
    # component winding without relying on the caller's later scene repair.
    bm=bmesh.new();bm.from_mesh(joined.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(joined.data);bm.free()
    joined.data.update()
    joined['asset_provenance']='Original procedural generic vehicle; no manufacturer branding or downloaded geometry.'
    joined['license']='MIT'
    joined['vehicle_variant']='compact_suv' if suv else 'sedan'
    joined['forward_axis']='+Y'
    joined['units']='meters'
    joined.data.calc_loop_triangles()
    joined['triangle_count']=len(joined.data.loop_triangles)
    joined['asset_revision']='v07 curved loft and physical wheel apertures'
    if joined['triangle_count']>30000:
        raise RuntimeError('Vehicle exceeds 30,000-triangle budget: %s'%joined['triangle_count'])
    return joined
