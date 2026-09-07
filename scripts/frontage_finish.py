"""Photo-interpreted lower fascia correction, separate from lidar roof planes."""
import math,json,hashlib
from pathlib import Path


def apply_frontage_finish(root=Path(__file__).resolve().parents[1]):
    import bpy
    from mathutils import Vector
    source=root/'research/frontage-fascia-fit.json';record=json.loads(source.read_text());fit=record['fit']
    if hashlib.sha256((root/record['camera']).read_bytes()).hexdigest()!=record['camera_constraints']['sha256']:
        raise RuntimeError('Frontage fit camera source changed; refit before applying')
    a=Vector((*fit['a_xy'],0))
    b=Vector((*fit['b_xy'],0))
    edge=(b-a).normalized(); inward=Vector((-edge.y,edge.x,0))
    length=(b-a).length; depth=fit['inferred_depth_m']; top=fit['top_z']; height=fit['height']
    yaw=math.atan2(edge.y,edge.x)
    canopy=bpy.data.objects['Long lower logo canopy']
    if canopy.get('Photo frontage fit'):raise RuntimeError('Frontage finish already applied; rebuild before replacing')
    canopy.location=(a+b)/2+inward*depth/2+Vector((0,0,top-height/2))
    canopy.rotation_euler.z=yaw;canopy.scale=(length/27,depth/4.5,height/1.2)
    canopy['Photo frontage fit']='research/frontage-fascia-fit.json; photo inferred, not a measured structural dimension'
    canopy['Frontage fit SHA256']=hashlib.sha256(source.read_bytes()).hexdigest()
    soffit=bpy.data.objects['Under canopy dark soffit']
    soffit.location=(a+b)/2+inward*depth/2+Vector((0,0,top-height-.045))
    soffit.rotation_euler.z=yaw;soffit.scale=((length-.15)/26.8,(depth-.12)/4.3,1)
    # Facade lettering and its mark share the corrected fascia plane.
    word=bpy.data.objects['Current fascia wordmark']
    word.location=a+edge*8.30-inward*.025+Vector((0,0,top-1.32))
    word.rotation_euler=(math.pi/2,0,yaw);word.data.size=1.08
    logo_center=a+edge*5.40-inward*.045+Vector((0,0,top-.99))
    from mathutils import Matrix
    transform=Matrix.Translation(logo_center)@Matrix.Rotation(yaw,4,'Z')@Matrix.Translation(Vector((-55.6,3.09,-4.61)))
    # Exact original facade mark names; monument has suffixed object names.
    for name in ['Hexagonal Protolabs outline','Mark inner bars','Mark inner bars.001']:
        ob=bpy.data.objects[name];ob.matrix_world=transform@ob.matrix_world
    # Sparse, shallow panel joints follow the clearly visible fascia divisions.
    joint_material=bpy.data.materials['Ivory coated aluminum'].copy()
    joint_material.name='Lower fascia subtle panel joints'
    bs=joint_material.node_tree.nodes.get('Principled BSDF')
    if bs:bs.inputs['Base Color'].default_value=(.37,.42,.43,1)
    collection=canopy.users_collection[0]
    for index in range(1,round(length/1.4)):
        center=a+edge*(index*length/round(length/1.4))-inward*.012
        curve=bpy.data.curves.new('Lower fascia joint','CURVE');curve.dimensions='3D';curve.bevel_depth=.007;curve.bevel_resolution=0
        spline=curve.splines.new('POLY');spline.points.add(1)
        spline.points[0].co=(*center[:2],top-.03,1);spline.points[1].co=(*center[:2],top-height+.03,1)
        ob=bpy.data.objects.new('Lower fascia panel joint',curve);collection.objects.link(ob);curve.materials.append(joint_material)
    # Earlier speculative full-height door pairs cut across the brick window run.
    for ob in bpy.data.objects:
        if ob.name.startswith('Lower reception doors'):
            ob.hide_render=True;ob.hide_viewport=True
    # One photo-interpreted narrow secondary door under the fascia, ahead of the
    # opaque connector backing. It does not assert an accurate interior.
    door_center=Vector((65.03,4.675,0)); door_edge=Vector((16.6,8.5,0)).normalized()
    door_inward=Vector((-door_edge.y,door_edge.x,0))
    points=[door_center+door_edge*x-door_inward*.035+Vector((0,0,z)) for x,z in [(-.48,.12),(.48,.12),(.48,2.75),(-.48,2.75)]]
    data=bpy.data.meshes.new('Secondary frontage door');data.from_pydata(points,[],[(0,1,2,3)]);data.materials.append(bpy.data.materials['Blue reflective insulated glazing'])
    ob=bpy.data.objects.new('Photo-interpreted secondary frontage door',data);collection.objects.link(ob)
    for start,end in [(points[0],points[1]),(points[1],points[2]),(points[2],points[3]),(points[3],points[0])]:
        curve=bpy.data.curves.new('Secondary door frame','CURVE');curve.dimensions='3D';curve.bevel_depth=.035;curve.bevel_resolution=1
        spline=curve.splines.new('POLY');spline.points.add(1)
        spline.points[0].co=(*(start-door_inward*.015),1);spline.points[1].co=(*(end-door_inward*.015),1)
        ob=bpy.data.objects.new('Secondary frontage door frame',curve);collection.objects.link(ob);curve.materials.append(bpy.data.materials['Anodized blue grey mullions'])
    # Monument text scale is a visual typography approximation inside the fitted panel.
    brand=bpy.data.objects['Monument brand'];brand.data.size=.84
    brand.location+=brand.matrix_world.to_3x3()@Vector((.38,0,0))
    bpy.data.objects['Monument tagline'].data.size=.24
    bpy.data.objects['Monument address'].data.size=.34
    bpy.context.view_layer.update()
    return {'front_edge_a':list(a),'front_edge_b':list(b),'top_z':top,'height':height,'depth':depth,'yaw_degrees':math.degrees(yaw)}
