"""Original procedural generic vehicles for site visualization.

License: MIT. Copyright (c) 2026 Reconstruction contributors.
No downloaded vehicle geometry, manufacturer designs, badges or textures are used.
Public entry point: create_vehicle_asset(name, color=(.22,.28,.33), variant='sedan').
Returns ONE mesh object with applied modifiers and ground-centered origin.
Coordinates are meters; +Y is forward; +Z is up; minimum Z is 0.
"""
import math
import bpy
from mathutils import Vector


def _material(name, color, metallic=0.0, roughness=.4, emission=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
    rgba = tuple(color[:3]) + (1.0,)
    mat.diffuse_color = rgba
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = rgba
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    if 'Coat Weight' in bs.inputs:
        bs.inputs['Coat Weight'].default_value = .32 if metallic > .2 else .05
        bs.inputs['Coat Roughness'].default_value = .2
    if emission:
        bs.inputs['Emission Color'].default_value = rgba
        bs.inputs['Emission Strength'].default_value = emission
    return mat


def _mesh(name, vertices, faces, material, parts, bevel=0.0):
    data = bpy.data.meshes.new(name + '_mesh')
    data.from_pydata(vertices, [], faces)
    data.materials.append(material)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    parts.append(obj)
    if bevel:
        mod = obj.modifiers.new('Small manufactured edge radii', 'BEVEL')
        mod.width = bevel
        mod.segments = 2 if name.endswith('_body') or '_mirror' in name else 1
        mod.affect = 'EDGES'
        mod.limit_method = 'ANGLE'
        mod.angle_limit = .35
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
    # Profiled tire barrel, X axis. Seven ring sections create shoulders and sidewalls.
    sign = 1 if x > 0 else -1
    profiles = [(-.115, .225),(-.113,.286),(-.080,radius),(.080,radius),
                (.113,.286),(.115,.225)]
    n = 20
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
    _rod(name+'_rim',(outer-sign*.035,y,radius),(outer,y,radius),.225,alloy,parts,20)
    _rod(name+'_recess',(outer,y,radius),(outer+sign*.004,y,radius),.178,dark,parts,20)
    # Five modest metal spokes, hub and wheel nut detail. Low cost at site distance.
    for k in range(5):
        theta=k*math.tau/5+.2
        p=(outer+sign*.012,y+math.cos(theta)*.19,radius+math.sin(theta)*.19)
        _rod(name+'_spoke%d'%k,(outer+sign*.012,y,radius),p,.027,alloy,parts,5)
    _rod(name+'_hub',(outer+sign*.01,y,radius),(outer+sign*.027,y,radius),.064,alloy,parts,12)


def _inset_quad(name, corners, material, parts, inset=.075, normal_offset=.006):
    v=[Vector(q) for q in corners]
    center=sum(v,Vector())/len(v)
    normal=(v[1]-v[0]).cross(v[2]-v[0]).normalized()
    # Named face corner winding points outward.
    v=[tuple(center+(q-center)*(1-inset)+normal*normal_offset) for q in v]
    return _mesh(name,v,[(0,1,2,3)],material,parts)


def create_vehicle_asset(name, color=(.22,.28,.33), variant='sedan'):
    """Create an original generic sedan or compact SUV as ONE joined mesh.

    Approximate sedan bounds: 4.66 m long, 2.24 m including mirrors, 1.52 m high.
    Compact SUV: 4.66 m long, 2.24 m including mirrors, 1.85 m high.
    Both have 1.85–1.90 m body width. Mesh has well below 6,000 triangles.
    Reuse obj.data for linked parking instances. No other objects remain created.
    """
    variant=variant.lower()
    if variant not in ('sedan','suv','compact_suv'):
        raise ValueError("variant must be 'sedan' or 'suv' / 'compact_suv'")
    suv=variant!='sedan'
    parts=[]
    key='_'.join('%03d'%max(0,min(255,round(c*255))) for c in color[:3])
    paint=_material('Generic_vehicle_paint_'+key,color,.62,.28)
    glass=_material('Generic_vehicle_blue_black_glass',(.027,.057,.075),.30,.16)
    rubber=_material('Generic_vehicle_tire_rubber',(.012,.016,.019),0,.79)
    trim=_material('Generic_vehicle_charcoal_trim',(.025,.033,.039),.10,.48)
    chrome=_material('Generic_vehicle_satin_alloy',(.47,.52,.56),.82,.26)
    lamps=_material('Generic_vehicle_headlamp',(.78,.87,.96),.15,.18,.12)
    red=_material('Generic_vehicle_taillamp',(.42,.016,.010),.10,.22,.06)
    amber=_material('Generic_vehicle_indicator',(.84,.29,.025),.10,.25)
    plate=_material('Generic_vehicle_blank_plate',(.68,.70,.67),.08,.55)
    # Body rings, with a faceted shoulder and soft bevels. +Y is the nose.
    sections=[(-2.28,.76,.91),(-2.16,.89,1.00),(-1.52,.93,1.06),
              (-.75,.94,1.07),(.42,.94,1.07),(1.30,.91,1.04),
              (2.12,.86,.94),(2.30,.74,.84)]
    if suv:
        sections=[(y,w*1.015,z+.13) for y,w,z in sections]
    vv=[]
    for y,w,z in sections:
        cross=[(-w*.87,.39),(-w*.98,.46),(-w,.73),(-w*.99,z-.10),
               (-w*.87,z),(-w*.55,z+.035),(0,z+.045),
               (w*.55,z+.035),(w*.87,z),(w*.99,z-.10),(w,.73),(w*.98,.46),(w*.87,.39)]
        vv.extend([(x,y,zz) for x,zz in cross])
    n=13
    ff=[tuple(reversed(range(n)))]
    for k in range(len(sections)-1):
        for j in range(n): ff.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
    ff.append(tuple((len(sections)-1)*n+j for j in range(n)))
    body=_mesh(name+'_body',vv,ff,paint,parts,.024)
    # Dark rocker strips and bumpers reveal tire clearance and lower silhouette.
    _box(name+'_underbody',(0,0,.37),(1.48,3.72,.18),trim,parts,.035)
    for side in [-1,1]:
        _box(name+'_rocker',(side*.929,-.02,.46),(.035,2.02,.12),trim,parts,.02)
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
    _mesh(name+'_cabin',cabin,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],paint,parts,.018)
    _inset_quad(name+'_rear_window',[cabin[i] for i in [0,1,5,4]],glass,parts,.14,.013)
    _inset_quad(name+'_windshield',[cabin[i] for i in [2,3,7,6]],glass,parts,.11,.014)
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
        _inset_quad(name+'_rear_side_glass',back,glass,parts,.12,.011)
        _inset_quad(name+'_front_side_glass',front,glass,parts,.10,.011)
        # Door handles and clean, modest seam at B pillar.
        for yy in [-.79,.34]:
            _box(name+'_door_handle',(side*.931,yy,zbase-.08),(.028,.18,.035),chrome,parts,.012)
        _rod(name+'_door_seam',(side*.944,split_y,.57),(side*.944,split_y,zbase-.03),.006,trim,parts,5)
        # Mirror stalk + body. Mirror width included in total bounds, body remains ~1.85m.
        _rod(name+'_mirror_stalk',(side*.83,.72,zbase+.02),(side*1.00,.75,zbase+.05),.025,trim,parts,6)
        _box(name+'_mirror',(side*1.014,.75,zbase+.09),(.21,.22,.125),paint,parts,.045)
        _box(name+'_mirror_glass',(side*1.016,.636,zbase+.09),(.145,.015,.075),glass,parts,.01)
    # Front fascia, split headlamps, grille slots, blank plates; no brand badges.
    zlight=.91+(.13 if suv else 0)
    for side in [-1,1]:
        _box(name+'_headlight',(side*.57,2.206,zlight),(.43,.065,.135),lamps,parts,.035)
        _box(name+'_front_indicator',(side*.784,2.177,zlight-.015),(.065,.08,.08),amber,parts,.015)
        _box(name+'_taillight',(side*.64,-2.188,zlight),(.30,.065,.16),red,parts,.023)
        _box(name+'_reverse_light',(side*.52,-2.225,zlight),(.06,.02,.045),lamps,parts,.008)
    _box(name+'_grille',(0,2.302,.75+(.1 if suv else 0)),(.68,.019,.19),trim,parts,.025)
    for z in [.71,.765,.82]:
        _box(name+'_grille_slat',(0,2.316,z+(.1 if suv else 0)),(.63,.012,.012),chrome,parts)
    _box(name+'_front_plate',(0,2.34,.58),(.40,.022,.12),plate,parts,.009)
    _box(name+'_rear_plate',(0,-2.295,.74),(.40,.025,.12),plate,parts,.01)
    # Four road wheels, with exposed silver hubs and profiled rubber sidewalls.
    radius=.36 if suv else .335
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
        for mod in list(ob.modifiers):
            bpy.ops.object.modifier_apply(modifier=mod.name)
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
    joined['asset_provenance']='Original procedural generic vehicle; no manufacturer branding or downloaded geometry.'
    joined['license']='MIT'
    joined['vehicle_variant']='compact_suv' if suv else 'sedan'
    joined['forward_axis']='+Y'
    joined['units']='meters'
    joined.data.calc_loop_triangles()
    joined['triangle_count']=len(joined.data.loop_triangles)
    if joined['triangle_count']>6000:
        raise RuntimeError('Vehicle exceeds 6,000-triangle budget: %s'%joined['triangle_count'])
    return joined
