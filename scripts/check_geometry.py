#!/usr/bin/env python3
"""Check the cube helper's winding and selected closed Blender scene boxes.

Without Blender:
    python scripts/check_geometry.py --source-only
Inside Blender, after opening a generated master:
    blender --background scene/protolabs-campus.blend --python-exit-code 1 \
        --python scripts/check_geometry.py -- --output geometry-check.json

The checks inspect only known closed cube meshes. They do not modify normals,
recalculate arbitrary surfaces, render images, or claim photographic fidelity.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
CLOSED_BOX_NAMES = (
    'Main block occupied volume',
    'Long lower logo canopy',
    'Dark monument sign',
)


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cube_source_check(root):
    """Execute only the real cube helper with a mesh recorder, then test geometry."""
    source_path = root / 'scripts/build_scene.py'
    module = ast.parse(source_path.read_text(), filename=str(source_path))
    helper = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == 'cube')
    captured = {}

    def record_mesh(name, vertices, faces, material):
        captured['vertices'] = vertices
        captured['faces'] = faces
        return SimpleNamespace(location=None)

    namespace = {'mesh': record_mesh}
    isolated = ast.Module(body=[helper], type_ignores=[])
    exec(compile(isolated, str(source_path), 'exec'), namespace)
    namespace['cube']('Winding regression unit box', (0, 0, 0), (2, 2, 2), None, 0)
    vertices, faces = captured['vertices'], captured['faces']
    volume, outward = 0.0, []
    for face in faces:
        a, b, c = (vertices[i] for i in face[:3])
        normal = cross(subtract(b, a), subtract(c, a))
        center = tuple(sum(vertices[i][axis] for i in face) / len(face) for axis in range(3))
        outward.append(dot(normal, center))
        for index in range(1, len(face) - 1):
            volume += dot(vertices[face[0]], cross(vertices[face[index]], vertices[face[index + 1]])) / 6
    passed = abs(volume - 8.0) < 1e-8 and all(value > 0 for value in outward)
    return {'check': 'source cube helper unit box', 'passed': passed,
            'signed_volume': volume, 'expected_outward_volume': 8.0,
            'face_normal_dot_outward': outward}


def scene_box_checks():
    import bpy
    import bmesh
    from mathutils import Vector

    results = []
    for name in CLOSED_BOX_NAMES:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != 'MESH':
            results.append({'object': name, 'passed': False, 'error': 'Required closed mesh is missing'})
            continue
        data = obj.data
        center = sum((vertex.co for vertex in data.vertices), Vector()) / len(data.vertices)
        outward = [float(poly.normal.dot(poly.center - center)) for poly in data.polygons]
        bm = bmesh.new()
        bm.from_mesh(data)
        volume = bm.calc_volume(signed=True)
        manifold = all(edge.is_manifold for edge in bm.edges)
        bm.free()
        lo = [min(vertex.co[axis] for vertex in data.vertices) for axis in range(3)]
        hi = [max(vertex.co[axis] for vertex in data.vertices) for axis in range(3)]
        expected = (hi[0] - lo[0]) * (hi[1] - lo[1]) * (hi[2] - lo[2])
        volume_matches = abs(volume - expected) <= max(1e-5, expected * 1e-5)
        passed = volume > 0 and volume_matches and manifold and all(value > 0 for value in outward)
        results.append({'object': name, 'passed': passed, 'vertex_count': len(data.vertices),
                        'face_count': len(data.polygons), 'signed_volume_local_m3': volume,
                        'expected_box_volume_m3': expected, 'closed_manifold': manifold,
                        'face_normal_dot_outward': outward})
    return results


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--root', type=Path, default=ROOT, help='Source checkout whose actual cube helper is tested')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    source = cube_source_check(args.root)
    report = {'source': source, 'scope': 'Closed cube winding only; no photographic or full-scene surface acceptance'}
    if not args.source_only:
        report['scene_boxes'] = scene_box_checks()
    report['passed'] = source['passed'] and all(result['passed'] for result in report.get('scene_boxes', []))
    encoded = json.dumps(report, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    print(encoded, end='')
    if not report['passed']:
        raise RuntimeError('Closed cube winding regression failed; see signed volumes and face normals')


if __name__ == '__main__':
    main()
