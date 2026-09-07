"""Preserve recorded opaque material albedos before glTF optimization.

Only JSON material factors/map bindings change. BIN data, images and topology
are copied byte-for-byte; the textured Blender master is never opened.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

JSON_CHUNK = 0x4E4F534A


def read_glb(path):
    data = Path(path).read_bytes()
    if len(data) < 20 or struct.unpack_from('<4sII', data) != (b'glTF', 2, len(data)):
        raise ValueError('Expected a complete glTF 2 binary')
    chunks = []
    offset = 12
    while offset < len(data):
        size, kind = struct.unpack_from('<II', data, offset)
        end = offset + 8 + size
        if size % 4 or end > len(data):
            raise ValueError('Invalid GLB chunk boundary')
        chunks.append((kind, data[offset + 8:end]))
        offset = end
    if not chunks or chunks[0][0] != JSON_CHUNK or sum(k == JSON_CHUNK for k, _ in chunks) != 1:
        raise ValueError('GLB must begin with one JSON chunk')
    return data, chunks, json.loads(chunks[0][1])


def prepare_viewer_materials(source, palette_path, output):
    source, palette_path, output = map(Path, (source, palette_path, output))
    if source.resolve() == output.resolve():
        raise ValueError('Prepared GLB must not overwrite the source export')
    data, chunks, document = read_glb(source)
    palette_bytes = palette_path.read_bytes()
    palette = json.loads(palette_bytes)
    applied = []
    for material in document.get('materials', []):
        name = material.get('name', '')
        if name not in palette or material.get('alphaMode', 'OPAQUE') != 'OPAQUE':
            continue
        color = palette[name]['linearColor']
        if len(color) != 3 or not all(isinstance(v, (int, float)) and math.isfinite(v) and 0 <= v <= 1 for v in color):
            raise ValueError(f'Invalid linear albedo for {name}')
        pbr = material.setdefault('pbrMetallicRoughness', {})
        alpha = pbr.get('baseColorFactor', [1, 1, 1, 1])[3]
        pbr['baseColorFactor'] = [*color, alpha]
        removed = pbr.pop('baseColorTexture', None)
        applied.append({'name': name, 'linear_color': color, 'removed_scan_map': removed is not None})
    encoded = json.dumps(document, ensure_ascii=False, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    prepared_chunks = [(JSON_CHUNK, encoded), *chunks[1:]]
    payload = b''.join(struct.pack('<II', len(part), kind) + part for kind, part in prepared_chunks)
    result = struct.pack('<4sII', b'glTF', 2, 12 + len(payload)) + payload
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(result)
    return {
        'source_glb_sha256': hashlib.sha256(data).hexdigest(),
        'prepared_glb_sha256': hashlib.sha256(result).hexdigest(),
        'palette_sha256': hashlib.sha256(palette_bytes).hexdigest(),
        'binary_chunks_sha256': [hashlib.sha256(part).hexdigest() for _, part in chunks[1:]],
        'binary_images_and_topology_unchanged': True,
        'applied_materials': applied,
        'scope': 'Known opaque palette materials use mean linear albedo once; unknown and alpha materials remain unchanged.',
    }


def verify_optimized_materials(path, prepared_report):
    data, _, document = read_glb(path)
    materials = {m.get('name'): m for m in document.get('materials', [])}
    # These formerly shader-equivalent materials were incorrectly merged by
    # optimization. They have distinct recorded colors and must stay distinct.
    critical = ('Weathered asphalt / metric noise', 'Charcoal aggregate membrane',
                'Concrete curbs & walks', 'Warm umber precast / photo colour',
                'Mown summer grass', 'Prairie meadow')
    expected = {m['name']: m['linear_color'] for m in prepared_report['applied_materials']}
    checked = {}
    for name in critical:
        if name not in expected:
            continue
        if name not in materials:
            raise ValueError(f'Optimizer lost distinct material identity: {name}')
        pbr = materials[name].get('pbrMetallicRoughness', {})
        actual = pbr.get('baseColorFactor', [1, 1, 1, 1])[:3]
        if 'baseColorTexture' in pbr or any(abs(a-b) > 1e-6 for a, b in zip(actual, expected[name])):
            raise ValueError(f'Optimizer changed prepared material: {name}')
        checked[name] = actual
    return {'optimized_glb_sha256': hashlib.sha256(data).hexdigest(),
            'distinct_surface_albedos': checked}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--palette', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    report = prepare_viewer_materials(args.source, args.palette, args.output)
    text = json.dumps(report, indent=2) + '\n'
    if args.receipt:
        args.receipt.write_text(text)
    print(text)
