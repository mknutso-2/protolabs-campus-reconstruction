"""Small, explicitly inferred exterior corrections; preserves measured massing.

Call ``apply_visual_finish()`` after building geometry, before material export,
packing and saving. ``entrance=False`` limits the change to flag cloth and smooth
column normals. No roof, building volume, ground, pole, or camera is repositioned.

Flag pattern proportions: Executive Order 10834, standard proportions table:
https://www.govinfo.gov/content/pkg/USCODE-2018-title4/pdf/USCODE-2018-title4-chap1.pdf
https://www.archives.gov/federal-register/codification/executive-order/10834.html
Its campus cloth dimensions, color rendering and static wind pose remain inferred.
Door portal and pulls follow the pale-frame motif visible in the 2018 entrance
reference. Their detailed dimensions are illustrative, not a measured shop drawing.
"""
import math
import bpy
from mathutils import Vector

PREFIX = 'Visual finish | '


def _material(name, srgb, roughness=.45, metallic=0.0):
    name = PREFIX + name
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in srgb]
    m.diffuse_color = (*linear, 1)
    m.use_nodes = True
    shader = m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*linear, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    return m


def _replace_flag():
    ob = bpy.data.objects.get('US flag cloth')
    if ob is None or ob.type != 'MESH':
        raise RuntimeError('Expected the original US flag cloth mesh before finishing')
    if ob.get('visual_finish_pattern') == '13 stripes; 50 five-point stars per face':
        return {'stripes': 13, 'stars_per_face': 50, 'already_applied': True}
    # The existing mesh stores the hoist in local geometry and the site offset in
    # its object transform. Retain that transform and its original top attachment.
    anchor = min(ob.data.vertices, key=lambda v: (v.co.x, -v.co.z)).co.copy()
    fly = max(v.co.x for v in ob.data.vertices) - anchor.x
    if not 1.0 < fly < 5.0:
        raise RuntimeError('Unexpected original flag dimensions')
    hoist = fly / 1.9
    # Darker display-oriented albedos keep textile red/navy legible under the
    # scene's bright physical daylight. These are not certified textile colors.
    red = _material('Flag textile red', (.44, .025, .055), .82)
    white = _material('Flag textile white', (.93, .94, .92), .72)
    blue = _material('Flag textile navy', (.045, .065, .15), .82)
    for mat in (red, white, blue):
        mat.node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value = .05
    def surface(u, v, offset=0.0):
        # Same attachment and modest static wind interpretation as the original.
        wave = .23 * math.sin(u * 7 + v * 1.2) * u
        return (anchor.x + u * fly, anchor.y + wave + offset,
                anchor.z - v * hoist - .16 * u)
    verts = []
    faces = []
    indices = []
    columns, rows = 50, 26  # union width .4 fly; two bands per exact 1/13 stripe
    for j in range(rows + 1):
        for i in range(columns + 1):
            verts.append(surface(i / columns, j / rows))
    for j in range(rows):
        for i in range(columns):
            a = j * (columns + 1) + i
            faces.append((a, a + 1, a + columns + 2, a + columns + 1))
            indices.append(2 if j < 14 and i < 20 else (j // 2) % 2)
    # 9 staggered rows: 6,5,6,5,6,5,6,5,6 = 50. Outer star diameter
    # is .0616 of hoist; inner radius gives regular five-point geometry.
    outer = .0308 * hoist
    inner = outer * math.sin(math.pi / 10) / math.sin(3 * math.pi / 10)
    star_count = 0
    for row in range(9):
        count = 6 if row % 2 == 0 else 5
        for col in range(count):
            center_x = (.76 * hoist / 12) * ((1 if count == 6 else 2) + 2 * col)
            center_down = (7 / 13 * hoist / 10) * (row + 1)
            star_count += 1
            for side in (-1, 1):
                center = len(verts)
                verts.append(surface(center_x / fly, center_down / hoist, side * .0015))
                for k in range(10):
                    angle = math.pi / 2 + k * math.pi / 5
                    radius = outer if k % 2 == 0 else inner
                    u = (center_x + math.cos(angle) * radius) / fly
                    v = (center_down - math.sin(angle) * radius) / hoist
                    verts.append(surface(u, v, side * .0015))
                for k in range(10):
                    face = (center, center + 1 + k, center + 1 + (k + 1) % 10)
                    faces.append(face if side < 0 else tuple(reversed(face)))
                    indices.append(1)
    mesh = bpy.data.meshes.new(PREFIX + 'US flag 13 stripes 50 stars')
    mesh.from_pydata(verts, [], faces)
    for material in (red, white, blue):
        mesh.materials.append(material)
    for polygon, index in zip(mesh.polygons, indices):
        polygon.material_index = index
        polygon.use_smooth = True
    mesh.update()
    old = ob.data
    ob.data = mesh
    if old.users == 0:
        bpy.data.meshes.remove(old)
    ob['visual_finish_pattern'] = '13 stripes; 50 five-point stars per face'
    ob['pattern_source'] = 'EO 10834 standard proportions; govinfo.gov USCODE-2018-title4-chap1'
    ob['evidence'] = 'National flag pattern verified; campus cloth size and static wind pose inferred'
    ob['cloth_fly_m'] = fly
    ob['cloth_hoist_m'] = hoist
    return {'stripes': 13, 'stars_per_face': star_count, 'fly_m': fly, 'hoist_m': hoist,
            'triangles': sum(len(p.vertices) - 2 for p in mesh.polygons)}


def _beam(collection, name, a, b, radius, material, sides=12):
    a, b = Vector(a), Vector(b)
    delta = b - a
    phase = math.pi / 4 if sides == 4 else 0
    verts = [(radius * math.cos(i * math.tau / sides + phase), radius * math.sin(i * math.tau / sides + phase), z)
             for z in (-delta.length / 2, delta.length / 2) for i in range(sides)]
    faces = [tuple(reversed(range(sides))), tuple(range(sides, sides * 2))]
    faces += [(i, (i + 1) % sides, (i + 1) % sides + sides, i + sides) for i in range(sides)]
    mesh = bpy.data.meshes.new(PREFIX + name)
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    for polygon in mesh.polygons[2:]: polygon.use_smooth = sides > 4
    ob = bpy.data.objects.new(PREFIX + name, mesh)
    collection.objects.link(ob)
    ob.location = (a + b) / 2
    ob.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    ob['evidence'] = 'Photo-informed decorative entrance framing; exact dimensions inferred'
    return ob


def _entrance_portal():
    name = 'Details | inferred entrance finish'
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    for ob in list(collection.objects):
        if ob.name.startswith(PREFIX): bpy.data.objects.remove(ob, do_unlink=True)
    pale = _material('Pale entry aluminum', (.62, .67, .66), .33, .45)
    metal = _material('Door pull satin metal', (.58, .63, .64), .26, .72)
    removed = []
    # Suppress only the decorative blue members crossing the newly articulated
    # door pair. Hidden objects remain editable, and use_visible glTF omits them.
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or not ob.name.startswith('Main vestibule '): continue
        x, y, z = ob.location
        front = abs(x - 76.28) < .02
        redundant_vertical = 'vertical mullion' in ob.name and 3.5 < y < 5.5
        low_crossbar = 'transom' in ob.name and abs(z - .67) < .03
        if front and (redundant_vertical or low_crossbar):
            ob.hide_render = True
            ob.hide_viewport = True
            ob['visual_finish_replaced'] = 'Inferred pale aluminum paired entrance portal'
            removed.append(ob.name)
    # A 2 m opening centered at the existing pulls, with 2.78 m tall leaves.
    # The vestibule volume, glass planes, fascia and camera remain unchanged.
    x = 76.31
    for y in (3.5, 4.5, 5.5):
        _beam(collection, 'Door portal upright', (x, y, .06), (x, y, 4.02), .05, pale, 4)
    for z in (.12, 2.78):
        _beam(collection, 'Door leaf rail', (x, 3.5, z), (x, 5.5, z), .047, pale, 4)
    for ya, yb in ((2, 3.5), (5.5, 7)):
        _beam(collection, 'Retained sidelight rail', (76.285, ya, .67), (76.285, yb, .67), .044, pale, 4)
    for y in (4.24, 4.74):
        for z in (1, 1.7):
            _beam(collection, 'Door pull mounting', (x, y, z), (76.36, y, z), .015, metal, 12)
    return {'added_objects': len(collection.objects), 'hidden_decorative_members': removed,
            'interpretation': 'Pale paired entrance portal; precise dimensions not measured'}


def apply_visual_finish(*, entrance=True):
    """Apply once after geometry creation, returning a compact provenance report."""
    result = {'flag': _replace_flag()}
    smoothed = []
    for ob in bpy.data.objects:
        if ob.type == 'MESH' and ob.name.startswith(('Dark cylindrical entrance column', 'Flagpole')):
            for polygon in ob.data.polygons:
                if len(polygon.vertices) == 4: polygon.use_smooth = True
            smoothed.append(ob.name)
    result['smoothed_cylinders_without_geometry_change'] = smoothed
    if entrance: result['entrance'] = _entrance_portal()
    result['preserves'] = 'Measured roof, building volumes, terrain, flagpole location/height and saved cameras'
    bpy.context.scene['Visual finish provenance'] = str(result)
    return result
