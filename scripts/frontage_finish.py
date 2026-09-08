"""Photo-interpreted lower fascia correction, separate from lidar roof planes."""
import math,json,hashlib
from pathlib import Path


def trim_frontage_return(root=Path(__file__).resolve().parents[1]):
    """Stop the low fascia and rear return at the existing vestibule header.

    The 2018 entrance photograph shows a continuous header above the glazed
    vestibule, not the deep downstand created by extruding the aerial-fit front
    rectangle unchanged through the door volume. Depth and this hidden junction
    are interpreted. The occluded lower-right aerial pick is superseded by
    this close-view evidence; the top edge, visible branded span, lettering,
    main roofs and cameras are unchanged. Separate closed boxes preserve QA.
    """
    import bpy
    from mathutils import Vector
    canopy=bpy.data.objects['Long lower logo canopy']
    if canopy.get('Frontage return correction'):
        return json.loads(canopy['Frontage return correction'])
    if not canopy.get('Photo frontage fit'):
        raise RuntimeError('Apply the fitted front panel before trimming its hidden return')
    record=json.loads((root/'research/frontage-fascia-fit.json').read_text());fit=record['fit']
    a=Vector((*fit['a_xy'],0));b=Vector((*fit['b_xy'],0))
    edge=(b-a).normalized();inward=Vector((-edge.y,edge.x,0));length=(b-a).length
    depth=fit['inferred_depth_m'];top=fit['top_z'];bottom=top-fit['height']
    vestibule=bpy.data.objects['Vestibule white fascia']
    header_bottom=min((vestibule.matrix_world@v.co).z for v in vestibule.data.vertices)
    # The existing east-facing vestibule plane supplies a termination anchor;
    # it is not a new surveyed corner. The last low segment must rise with
    # the hidden return, rather than leave a plate hanging across the glass.
    panel_depth=.18
    run=(vestibule.location.x-a.x)/edge.x
    if not .2<run<length-.2 or not bottom<header_bottom<top or not panel_depth<depth:
        raise RuntimeError('Unexpected fascia/vestibule relationship; review the return junction')
    yaw=math.atan2(edge.y,edge.x);collection=canopy.users_collection[0]
    def body(name,start,span,width,center_v,z0,z1):
        ob=canopy.copy();ob.data=canopy.data.copy();ob.name=name;collection.objects.link(ob)
        ob.location=a+edge*(start+span/2)+inward*center_v+Vector((0,0,(z0+z1)/2))
        ob.rotation_euler=(0,0,yaw);ob.scale=(span/27,width/4.5,(z1-z0)/1.2)
        ob['evidence']='Close-view interpreted fascia termination at existing vestibule header; occluded aerial lower-right pick superseded; top edge and branded span retained'
        return ob
    rear_depth=depth-panel_depth;rear_center=panel_depth+rear_depth/2
    body('Lower fascia main rear return',0,run,rear_depth,rear_center,bottom,top)
    body('Lower fascia return above vestibule header',run,length-run,rear_depth,rear_center,header_bottom,top)
    body('Lower fascia front panel above vestibule header',run,length-run,panel_depth,panel_depth/2,header_bottom,top)
    canopy.location=a+edge*run/2+inward*panel_depth/2+Vector((0,0,(top+bottom)/2))
    canopy.scale=(run/27,panel_depth/4.5,(top-bottom)/1.2)
    soffit=bpy.data.objects['Under canopy dark soffit']
    terminal=soffit.copy();terminal.data=soffit.data.copy();terminal.name='Fascia return soffit above vestibule';collection.objects.link(terminal)
    terminal.location=a+edge*((run+length)/2)+inward*depth/2+Vector((0,0,header_bottom-.045))
    terminal.rotation_euler=(0,0,yaw);terminal.scale=((length-run-.15)/26.8,(depth-.12)/4.3,1)
    terminal['evidence']='Interpreted soffit termination at existing vestibule fascia bottom; no measured roof change'
    soffit.location=a+edge*run/2+inward*depth/2+Vector((0,0,bottom-.045))
    soffit.scale=((run-.15)/26.8,(depth-.12)/4.3,1)
    result={'front_panel_depth_m':panel_depth,'low_return_length_m':run,
            'raised_terminal_length_m':length-run,'terminal_bottom_z_m':header_bottom,
            'previous_terminal_bottom_z_m':bottom,
            'reference':'research/images/businessjournal-entrance-2018.jpg',
            'superseded_aerial_constraint':'Occluded lower-right front-face corner; last fascia segment raised to continuous close-view header',
            'interpretation':'Return depth and junction inferred from continuous photographed entrance header; fitted front plane/top edge, visible branded span, mark, main roofs and cameras retained'}
    canopy['Frontage return correction']=json.dumps(result)
    bpy.context.view_layer.update()
    return result


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
    return_geometry=trim_frontage_return(root)
    return {'front_edge_a':list(a),'front_edge_b':list(b),'top_z':top,'height':height,'depth':depth,'yaw_degrees':math.degrees(yaw),'return_correction':return_geometry}
