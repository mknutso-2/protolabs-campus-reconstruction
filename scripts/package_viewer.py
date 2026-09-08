"""Prepare and receipt every generated asset needed by the offline browser viewer."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import shutil
import subprocess
import tempfile

from PIL import Image
from prepare_viewer_materials import prepare_viewer_materials, verify_optimized_materials

root = Path(__file__).resolve().parents[1]
VIEW_NAMES = ('reference_aerial', 'entrance_detail', 'arrival', 'campus_overview')
REFERENCE_COPIES = {
    'research/images/protolabs-official-hq-drone.jpg': 'viewer/public/references/hq.jpg',
    'research/images/businessjournal-entrance-2018.jpg': 'viewer/public/references/entrance.jpg',
    'research/images/machine-design-frontage-2024.png': 'viewer/public/references/arrival.png',
}
JSON_COPIES = {
    'scene/cameras.json': 'viewer/public/models/cameras.json',
    'scene/materials.json': 'viewer/public/models/materials.json',
    'research/terrain_grid.json': 'viewer/public/models/terrain.json',
}
PUBLIC_FILES = (
    'viewer/public/models/campus.glb', *JSON_COPIES.values(),
    *[f'viewer/public/renders/{name}.jpg' for name in VIEW_NAMES],
    'viewer/public/renders/flythrough.mp4', *REFERENCE_COPIES.values(),
)


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-film', action='store_true')
    args = parser.parse_args()
    master_hash = file_sha(root/'scene/protolabs-campus.blend')
    metadata = json.loads((root/'scene/viewer-export.json').read_text())
    if metadata['master_sha256'] != master_hash:
        raise RuntimeError('Browser export is stale. Run scripts/export_viewer.py with the current master.')
    if metadata.get('viewer_glb_sha256') != file_sha(root/'scene/protolabs-campus-viewer.glb'):
        raise RuntimeError('Browser GLB differs from its export receipt.')
    cameras = json.loads((root/'scene/cameras.json').read_text())
    stills = {}
    for name in VIEW_NAMES:
        if name not in cameras:
            raise RuntimeError(f'Missing fixed-view camera: {name}')
        src = root/'deliverables/stills'/f'{name}.png'
        data = src.read_bytes()
        receipt = json.loads(src.with_suffix('.json').read_text())
        if receipt['master_sha256'] != master_hash or receipt['image_sha256'] != hashlib.sha256(data).hexdigest():
            raise RuntimeError(f'Stale fixed-view render: {name}')
        # Convert the exact bytes checked above, even if a file changes later.
        stills[name] = data
    film = root/'deliverables/flythrough.mp4'
    if args.require_film and not film.is_file():
        raise RuntimeError('Final viewer requires the encoded flythrough')
    missing_references = [name for name in REFERENCE_COPIES if not (root/name).is_file()]
    if args.require_film and missing_references:
        raise RuntimeError('Final viewer requires all reference images: ' + ', '.join(missing_references))
    for name in ('renders', 'models', 'references'):
        (root/'viewer/public'/name).mkdir(parents=True, exist_ok=True)
    for src, dst in JSON_COPIES.items():
        shutil.copyfile(root/src, root/dst)
    for name, data in stills.items():
        with Image.open(io.BytesIO(data)) as image:
            image.convert('RGB').save(root/f'viewer/public/renders/{name}.jpg', quality=94)
    for src, dst in REFERENCE_COPIES.items():
        if (root/src).is_file():
            shutil.copyfile(root/src, root/dst)
        else:
            # A preview may be incomplete, but must not silently show an old copy.
            (root/dst).unlink(missing_ok=True)
            print('Reference pending:', src)
    if film.is_file():
        shutil.copyfile(film, root/'viewer/public/renders/flythrough.mp4')
    else:
        (root/'viewer/public/renders/flythrough.mp4').unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix='campus-viewer-materials-') as temporary:
        prepared = Path(temporary)/'campus-materials.glb'
        joined = Path(temporary)/'campus-joined.glb'
        report = prepare_viewer_materials(root/'scene/protolabs-campus-viewer.glb', root/'scene/materials.json', prepared)
        subprocess.run(['npx', 'gltf-transform', 'optimize', str(prepared), str(joined), '--compress', 'false',
                        '--simplify', 'false', '--palette', 'false', '--texture-compress', 'false'], cwd=root/'viewer', check=True)
        optimized = root/'viewer/public/models/campus.glb'
        compression = subprocess.run(['node', str(root/'scripts/compress_viewer_lossless.mjs'), str(joined), str(optimized)],
                                     cwd=root/'viewer', check=True, capture_output=True, text=True)
        report['position_compression'] = json.loads(compression.stdout.strip().splitlines()[-1])
        report.update(verify_optimized_materials(optimized, report))
        report['master_sha256'] = master_hash
        # Keys are project-relative, matching release paths and the delivery manifest.
        report['public_payload_sha256'] = {name: file_sha(root/name) for name in PUBLIC_FILES if (root/name).is_file()}
        report['public_render_source_sha256'] = {
            f'viewer/public/renders/{name}.jpg': hashlib.sha256(data).hexdigest() for name, data in stills.items()}
        report['public_payload_complete'] = len(report['public_payload_sha256']) == len(PUBLIC_FILES)
        if args.require_film and not report['public_payload_complete']:
            raise RuntimeError('Final viewer payload is incomplete')
        (root/'scene/viewer-package.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
