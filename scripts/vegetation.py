"""Original deterministic vegetation for the Protolabs reconstruction.

SPDX-License-Identifier: MIT
Copyright (c) 2026 Protolabs campus reconstruction contributors

No downloaded meshes, image textures, or external dependencies. The trees are
artistic generic deciduous planting, not evidence of an exact on-site species.

Usage in Blender 4.2+:
    from vegetation import create_tree_asset, create_tree_instance
    oak = create_tree_asset('Tree_Broad', seed=21, height=12.0, crown=7.0,
                            variant='broad')
    oak.location = (10, 2, 0)
    twin = create_tree_instance(oak, 'Tree_Broad_02', (18, 4, 0), rotation=1.4)

Every tree asset is one mesh object, with real tapered branches and individual folded
leaf cards (two triangles each). Original packed procedural textures define
leaf outlines and veins. Linked instances reuse the same mesh data.
Tree crown is the overall diameter in metres, height includes the foliage.
Supported variants: broad, upright, spreading. Mature crowns use 8,000 packed
alpha leaf cards and remain below 20,000 triangles per reusable tree.
"""

import math
import random

import bpy
from mathutils import Vector


VARIANTS = ('broad', 'upright', 'spreading')


def _basis(axis):
    axis = Vector(axis).normalized()
    reference = Vector((0, 0, 1)) if abs(axis.z) < 0.90 else Vector((1, 0, 0))
    right = axis.cross(reference).normalized()
    return right, axis.cross(right).normalized()


def _leaf_image(name, color):
    """Create an original alpha leaf texture; fully packed, including for glTF."""
    image = bpy.data.images.get(name)
    if image is not None:
        return image
    width, height = 256, 128
    image = bpy.data.images.new(name, width=width, height=height, alpha=True)
    pixels = []
    for y in range(height):
        v = (y+.5)/height
        for x in range(width):
            u = (x+.5)/width
            contour = math.sin(math.pi*u)**.78
            contour *= 1 + .021*math.sin(u*math.pi*34)
            edge = contour-abs(v-.5)*2
            alpha = max(0,min(1,edge*height*.5+.5))
            # Restrained central vein, alternating lateral veins and mottling.
            center_vein = math.exp(-((v-.5)/.010)**2)
            side_line = abs(((u-abs(v-.5)*.65)*8)%1-.5)
            lateral_vein = math.exp(-(side_line/.035)**2)*(1-center_vein)
            mottling = math.sin(u*91+v*67)*math.sin(v*49-u*31)
            brightness = .88+.09*math.sin(u*math.pi)+.16*center_vein+.055*lateral_vein+.024*mottling
            # Image values are encoded sRGB so node values match the supplied
            # linear-space leaf palette after the texture color transform.
            for channel in color:
                linear = max(0,min(1,channel*brightness))
                pixels.append(12.92*linear if linear <= .0031308 else 1.055*linear**(1/2.4)-.055)
            pixels.append(alpha)
    image.pixels.foreach_set(pixels)
    image.alpha_mode = 'STRAIGHT'
    image.pack()
    return image


def _materials():
    bark = bpy.data.materials.get('CampusVeg_Bark')
    if bark is None:
        bark = bpy.data.materials.new('CampusVeg_Bark')
        bark.diffuse_color = (0.19, 0.15, 0.10, 1)
        bark.use_nodes = True
        n, l = bark.node_tree.nodes, bark.node_tree.links
        p = n.get('Principled BSDF')
        p.inputs['Roughness'].default_value = 0.88
        tex = n.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 7.0
        tex.inputs['Detail'].default_value = 3.0
        mapping = n.new('ShaderNodeVectorMath')
        mapping.operation = 'MULTIPLY'
        mapping.inputs[1].default_value = (6, 6, 0.7)
        coords = n.new('ShaderNodeTexCoord')
        l.new(coords.outputs['Object'], mapping.inputs[0])
        l.new(mapping.outputs['Vector'], tex.inputs['Vector'])
        ramp = n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (0.047, 0.039, 0.027, 1)
        ramp.color_ramp.elements[1].color = (0.27, 0.23, 0.16, 1)
        l.new(tex.outputs['Fac'], ramp.inputs[0])
        l.new(ramp.outputs[0], p.inputs['Base Color'])
        bump = n.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = 0.40
        bump.inputs['Distance'].default_value = 0.024
        l.new(tex.outputs['Fac'], bump.inputs['Height'])
        l.new(bump.outputs['Normal'], p.inputs['Normal'])
    materials = [bark]
    # Linear-space greens chosen to remain believable in direct sunlight.
    colors = [(0.042, 0.112, 0.019), (0.062, 0.155, 0.026),
              (0.091, 0.203, 0.039), (0.120, 0.237, 0.050),
              (0.034, 0.091, 0.017)]
    for i, color in enumerate(colors):
        material = bpy.data.materials.get('CampusVeg_DenseLeaf_v2_%02d' % i)
        if material is None:
            material = bpy.data.materials.new('CampusVeg_DenseLeaf_v2_%02d' % i)
            material.diffuse_color = (*color, 1)
            material.use_nodes = True
            n, l = material.node_tree.nodes, material.node_tree.links
            p = n.get('Principled BSDF')
            p.inputs['Base Color'].default_value = (*color, 1)
            p.inputs['Roughness'].default_value = 0.76
            p.inputs['Specular IOR Level'].default_value = 0.20
            p.inputs['Subsurface Weight'].default_value = 0.045
            texture = n.new('ShaderNodeTexImage')
            texture.image = _leaf_image('CampusVeg_DenseLeafTexture_v2_%02d'%i, color)
            texture.interpolation = 'Linear'
            texture.extension = 'CLIP'
            l.new(texture.outputs['Color'], p.inputs['Base Color'])
            # Explicit clipping maps to glTF MASK, avoiding per-card sorting
            # artifacts from BLEND when thousands of leaves overlap.
            clip = n.new('ShaderNodeMath')
            clip.operation = 'ROUND'
            l.new(texture.outputs['Alpha'], clip.inputs[0])
            l.new(clip.outputs[0], p.inputs['Alpha'])
            material.surface_render_method = 'DITHERED'
        materials.append(material)
    return materials


class _MeshBuilder:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.materials = []
        self.smooth = []
        self.leaf_count = 0

    def face(self, indices, material=0, smooth=False):
        self.faces.append(tuple(indices))
        self.materials.append(material)
        self.smooth.append(smooth)

    def branch(self, points, radii, sides=5):
        points = list(map(Vector, points))
        start = len(self.vertices)
        for i, (point, radius) in enumerate(zip(points, radii)):
            direction = points[min(i + 1, len(points)-1)] - points[max(i-1, 0)]
            u, v = _basis(direction)
            for j in range(sides):
                a = j * math.tau / sides
                self.vertices.append(point + radius * (u * math.cos(a) + v * math.sin(a)))
        for i in range(len(points)-1):
            for j in range(sides):
                a = start + i * sides + j
                b = start + i * sides + (j+1) % sides
                self.face((a, b, b+sides, a+sides), smooth=True)
        self.face(tuple(start + j for j in reversed(range(sides))))
        self.face(tuple(start+(len(points)-1)*sides+j for j in range(sides)))

    def leaf(self, point, length, width, normal, spin, material):
        normal = Vector(normal).normalized()
        u, v = _basis(normal)
        u, v = u*math.cos(spin)+v*math.sin(spin), v*math.cos(spin)-u*math.sin(spin)
        point = Vector(point)
        start = len(self.vertices)
        # Per-leaf UV cards retain real leaf spacing and work in PBR exporters.
        self.vertices.extend([
            point-u*length*.5-v*width*.5-normal*width*.10,
            point+u*length*.5-v*width*.5,
            point+u*length*.5+v*width*.5+normal*width*.10,
            point-u*length*.5+v*width*.5,
        ])
        self.face((start, start+1, start+2), material)
        self.face((start, start+2, start+3), material)
        self.leaf_count += 1

    def object(self, name, properties):
        mesh = bpy.data.meshes.new(name + '_Mesh')
        mesh.from_pydata(self.vertices, [], self.faces)
        mesh.update()
        uv_layer = mesh.uv_layers.new(name='LeafUV')
        leaf_uvs = ((0,0),(1,0),(1,1),(0,1))
        for polygon, material in zip(mesh.polygons,self.materials):
            if material:
                # Each leaf starts with triangle (a,a+1,a+2), then (a,a+2,a+3).
                base = min(polygon.vertices)
                for loop_index in polygon.loop_indices:
                    vertex_index = mesh.loops[loop_index].vertex_index
                    uv_layer.data[loop_index].uv = leaf_uvs[vertex_index-base]
        for material in _materials():
            mesh.materials.append(material)
        for polygon, material, smooth in zip(mesh.polygons, self.materials, self.smooth):
            polygon.material_index = material
            polygon.use_smooth = smooth
        mesh.calc_loop_triangles()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        obj['asset_provenance'] = 'Original procedural geometry; MIT; no third-party assets'
        obj['source_species'] = 'Generic deciduous artistic approximation'
        obj['triangle_count'] = len(mesh.loop_triangles)
        obj['individual_leaves'] = self.leaf_count
        for key, value in properties.items():
            obj[key] = value
        return obj


def create_tree_asset(name, seed=21, height=12.0, crown=7.0, variant=None):
    """Create a single reusable tree mesh rooted at origin, with metres as units.

    `variant` is 'broad', 'upright', or 'spreading'; omitted selects seed % 3.
    It does not select, delete, move, or modify other objects in the scene.
    """
    if height <= 0 or crown <= 0:
        raise ValueError('height and crown must be positive')
    variant = variant or VARIANTS[seed % len(VARIANTS)]
    if variant not in VARIANTS:
        raise ValueError('Unknown tree variant: ' + str(variant))
    rng = random.Random(seed)
    b = _MeshBuilder()
    radius = crown * 0.5
    bottom = {'broad': .28, 'upright': .25, 'spreading': .30}[variant] * height
    top = height * .98
    middle = (bottom + top) * .5
    vertical_radius = (top-bottom) * .5
    trunk_radius = min(height * .027, crown * .044)
    lean = Vector((rng.uniform(-.11,.11)*height, rng.uniform(-.05,.05)*height, 0))

    def trunk_at(z):
        f = z/height
        return Vector((lean.x*f*f, lean.y*f*f, z))

    trunk_points = [trunk_at(height * i/10 * .88) for i in range(11)]
    trunk_radii = [trunk_radius * ((1-i/11)**1.1 + .025) for i in range(11)]
    trunk_radii[0] *= 1.45
    b.branch(trunk_points, trunk_radii, sides=8)
    # Shallow buttress roots connect trunk and ground without a cylindrical plug.
    for i in range(5):
        angle = i*math.tau/5 + rng.uniform(-.2,.2)
        direction = Vector((math.cos(angle), math.sin(angle), 0))
        b.branch([Vector((0,0,trunk_radius*.8)), direction*trunk_radius*2.2,
                  direction*trunk_radius*3.7-Vector((0,0,.015))],
                 [trunk_radius*.54, trunk_radius*.19, .003], sides=4)

    def crown_clip(point, jitter=False):
        # Bound foliage-bearing twig ends to an irregular mature crown envelope.
        # This prevents sparse outlier twigs from shrinking the entire crown
        # when final nominal dimensions are fitted below.
        point = Vector(point)
        point.z = max(bottom+height*.012, min(height*.979, point.z))
        center = trunk_at(point.z)
        offset = Vector((point.x-center.x,point.y-center.y,0))
        angle = math.atan2(offset.y,offset.x)
        zf = (point.z-middle)/vertical_radius
        lobes = .89 + .075*math.sin(angle*3+seed*.31) + .045*math.cos(angle*5-seed*.17)
        allowed = radius*lobes*(.13+.87*math.sqrt(max(.02,1-zf*zf)))
        if offset.length > allowed:
            offset *= allowed/max(.0001,offset.length)
            if jitter: offset *= rng.uniform(.90,1.0)
            point.x, point.y = center.x+offset.x, center.y+offset.y
        return point

    leaf_sites = []
    # Ten asymmetrical scaffold branches, each with three secondary branches
    # and three tertiary twigs, produce 90 distinct sprays of real leaf planes.
    for primary in range(10):
        angle = primary * 2.399963 + rng.uniform(-.26,.26)
        f = primary/9
        attach_z = height * (.28 + f*.46)
        end_z = bottom + vertical_radius*(.57+f*.92) + rng.uniform(-.18,.18)*vertical_radius
        radial_envelope = math.sqrt(max(.14, 1-((end_z-middle)/vertical_radius)**2))
        spread = radius*radial_envelope*rng.uniform(.62,.86)
        if variant == 'upright':
            end_z += height*.035
        elif variant == 'spreading':
            attach_z -= height*.045
        p0 = trunk_at(attach_z)
        endpoint = crown_clip(trunk_at(end_z)+Vector((math.cos(angle)*spread, math.sin(angle)*spread, 0)))
        p1 = p0.lerp(endpoint, .31)-Vector((0,0,height*.032))
        p2 = p0.lerp(endpoint, .67)-Vector((0,0,height*.017))
        p3 = endpoint
        primary_radius = trunk_radius*(.48-.19*f)*rng.uniform(.86,1.12)
        b.branch([p0,p1,p2,p3], [primary_radius,primary_radius*.70,primary_radius*.40,.009], 6)

        for secondary in range(3):
            sf = .44 + .23*secondary
            start = p0.lerp(endpoint,sf)
            side_angle = angle + (-.70,.55,.13)[secondary] + rng.uniform(-.19,.19)
            extension = radius*rng.uniform(.20,.34)*(1-.22*f)
            growth = Vector((math.cos(side_angle)*extension, math.sin(side_angle)*extension,
                             height*rng.uniform(.035,.11)))
            end = crown_clip(start + growth)
            b.branch([start,start.lerp(end,.46)-Vector((0,0,height*.010)),end],
                     [primary_radius*.34,primary_radius*.15,.0035], 5)

            for twig in range(3):
                origin = start.lerp(end,.48+twig*.25)
                twig_angle = side_angle + (-.85,.70,.0)[twig] + rng.uniform(-.3,.3)
                twig_length = radius*rng.uniform(.14,.22)
                delta = Vector((math.cos(twig_angle)*twig_length,
                                math.sin(twig_angle)*twig_length,
                                height*rng.uniform(.012,.055)))
                tip = crown_clip(origin + delta)
                b.branch([origin,tip], [.0045,.0009], 3)
                leaf_sites.append((origin,tip))

    # Two triangles per folded leaf: fine silhouette and crisp moving shadows.
    # Dense sprays plus an irregular interior foliage layer create mature
    # leaf-on canopies at medium distance without opaque blob meshes.
    leaf_length = min(.30, max(.19, crown*.045))
    for index,(origin,tip) in enumerate(leaf_sites):
        axis = (tip-origin).normalized()
        u,v = _basis(axis)
        for leaf in range(70):
            along = rng.uniform(-.07,1.15)
            sideways = rng.gauss(0, radius*.095)
            radial = rng.gauss(0, radius*.081)
            point = crown_clip(origin.lerp(tip,along) + u*sideways + v*radial, jitter=True)
            # Keep the crown within the requested height, while retaining an
            # irregular silhouette rather than clipping to a geometric sphere.
            if point.z > height-leaf_length*.3:
                point.z = height-leaf_length*.3-rng.uniform(0,leaf_length*.5)
            length = leaf_length*rng.uniform(.78,1.38)
            width = length*rng.uniform(.43,.63)
            normal = Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(.12,1.3)))
            b.leaf(point,length,width,normal,rng.uniform(0,math.tau),
                   rng.choices([1,2,3,4,5],[17,32,26,10,15])[0])
    # Interior/surface foliage connects sprays into a substantially closed crown.
    # 6,300 twig-attached leaves + 1,700 infill leaves = 8,000 cards, 16k tris.
    # The scaffold remains visible below the crown and through small openings.
    for leaf in range(1700):
        theta = rng.uniform(0,math.tau)
        unit_z = rng.uniform(-1,1)
        radial = math.sqrt(max(0,1-unit_z*unit_z))
        shell = rng.uniform(.07,1.0)**(1/3)
        z = middle + unit_z*vertical_radius*shell
        center = trunk_at(z)
        point = center + Vector((math.cos(theta)*radius*radial*shell,
                                 math.sin(theta)*radius*radial*shell,0))
        point = crown_clip(point, jitter=True)
        length = leaf_length*rng.uniform(.80,1.35)
        normal = Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(.03,1.3)))
        b.leaf(point,length,length*rng.uniform(.47,.65),normal,
               rng.uniform(0,math.tau),rng.choices([1,2,3,4,5],[23,31,22,7,17])[0])
    obj = b.object(name, {'seed': seed, 'vegetation_variant': variant,
                         'nominal_height_m': height, 'nominal_crown_m': crown})
    # Correct for asymmetrical branch reach so requested planting dimensions
    # really are the generated mesh dimensions, not just scaffold dimensions.
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    horizontal_scale = crown/max(max(xs)-min(xs),max(ys)-min(ys))
    vertical_scale = height/max(zs)
    for vertex in obj.data.vertices:
        vertex.co.x *= horizontal_scale
        vertex.co.y *= horizontal_scale
        vertex.co.z *= vertical_scale
    obj.data.update()
    assert obj['triangle_count'] < 20000, 'Tree triangle budget exceeded'
    return obj


def create_tree_instance(asset, name, location=(0,0,0), scale=1.0, rotation=0.0):
    """Create a lightweight linked mesh instance; rotation is radians about Z."""
    instance = asset.copy()
    instance.data = asset.data
    instance.name = name
    instance.location = location
    instance.rotation_euler = (0,0,rotation)
    instance.scale = (scale,scale,scale) if isinstance(scale,(int,float)) else scale
    bpy.context.collection.objects.link(instance)
    return instance


def create_shrub_asset(name, seed=101, height=.95, width=1.5):
    """Create an open branched shrub with 420 leaves and no canopy blobs."""
    rng = random.Random(seed)
    b = _MeshBuilder()
    for stem in range(14):
        angle = stem*2.399963+rng.uniform(-.3,.3)
        radius = width*.5*rng.uniform(.26,.8)
        top = Vector((math.cos(angle)*radius,math.sin(angle)*radius,
                      height*rng.uniform(.56,.91)))
        origin = Vector((rng.uniform(-.06,.06),rng.uniform(-.06,.06),0))
        b.branch([origin,top*.50,top], [.017,.007,.001], 4)
        for j in range(30):
            p = origin.lerp(top,rng.uniform(.33,1.08))
            p += Vector((rng.gauss(0,width*.10),rng.gauss(0,width*.10),rng.gauss(0,height*.09)))
            length = rng.uniform(.10,.18)
            b.leaf(p,length,length*.58,(rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(.1,1.3)),
                   rng.uniform(0,math.tau),rng.randint(1,5))
    return b.object(name, {'seed': seed, 'vegetation_variant': 'shrub',
                          'nominal_height_m': height, 'nominal_crown_m': width})
