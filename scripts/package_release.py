"""Package a clean revision and hash-bound, inspected local deliverables.

The ZIP contains editable scenes, final stills, film/sample, offline gallery,
provenance, reproduction source and a Git history bundle. Raw lidar and installed
dependencies are restored through the documented workflow. FFmpeg must be able
to decode both videos; inspection remains a separate recorded human/agent action.
"""
import argparse
import datetime as dt
from fractions import Fraction
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile
import zipfile

from frame_integrity import inspect_png

ROOT = Path(__file__).resolve().parents[1]
VIEW_NAMES = ('reference_aerial', 'entrance_detail', 'arrival', 'campus_overview')
REQUIRED_FILES = [
    'scene/protolabs-campus.blend', 'scene/protolabs-motion.blend',
    'scene/protolabs-campus.glb', 'scene/protolabs-campus-viewer.glb',
    'scene/viewer-export.json', 'scene/cameras.json', 'scene/materials.json',
    'scene/viewer-package.json', 'viewer/public/models/campus.glb',
    *[f'deliverables/stills/{name}.{suffix}' for name in VIEW_NAMES for suffix in ('png', 'json')],
    'deliverables/flythrough.mp4', 'deliverables/cinematic/path.json',
    'deliverables/motion-sample.mp4', 'deliverables/motion-sample/path.json',
    'deliverables/comparison/index.html', 'deliverables/comparison/manifest.json',
]
REVIEW_FILE = 'deliverables/delivery-review.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''): digest.update(chunk)
    return digest.hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def local_file(name):
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Unsafe release path: ' + name)
    path = ROOT / relative
    if not path.resolve().is_relative_to(ROOT.resolve()) or path.is_symlink():
        raise ValueError('Release input must be an ordinary file inside the project: ' + name)
    return path


def read_json(name):
    value = json.loads(local_file(name).read_text())
    if not isinstance(value, dict): raise ValueError('Expected JSON object: ' + name)
    return value


def inspect_video(ffmpeg, name, path, expected_frames):
    command = [str(ffmpeg), '-hide_banner', '-nostdin', '-v', 'info', '-xerror',
               '-i', str(local_file(name)), '-map', '0:v:0', '-an', '-vf', 'showinfo',
               '-fps_mode', 'passthrough', '-f', 'null', '-']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode:
        raise RuntimeError('Video failed complete decoding: ' + name + '\n' + result.stderr[-1500:])
    frames = re.findall(r'\[Parsed_showinfo[^\]]*\]\s+n:\s*(\d+).*?\bs:(\d+)x(\d+)\b.*?\bpts_time:([^\s]+)', result.stderr)
    # showinfo places pts_time before size in supported FFmpeg releases.
    if not frames:
        frames = [(n, w, h, pts) for n, pts, w, h in re.findall(
            r'\[Parsed_showinfo[^\]]*\]\s+n:\s*(\d+).*?\bpts_time:([^\s]+).*?\bs:(\d+)x(\d+)\b', result.stderr)]
    rates = re.findall(r'config in time_base:.*?frame_rate:\s*([0-9]+/[0-9]+)', result.stderr)
    expected_fps = Fraction(str(path['fps'])) / Fraction(str(path.get('fps_base', 1)))
    if not rates or any(Fraction(rate) != expected_fps for rate in rates):
        raise RuntimeError('Video fps differs from motion path: ' + name)
    if len(frames) != expected_frames or [int(row[0]) for row in frames] != list(range(expected_frames)):
        raise RuntimeError('Video decoded frame count differs from motion path: ' + name)
    if any((int(w), int(h)) != (path['width'], path['height']) for _, w, h, _ in frames):
        raise RuntimeError('Video dimensions differ from motion path: ' + name)
    times = [float(row[3]) for row in frames]
    # Encoder starts MP4 timestamps at zero even when PNG numbers begin at 61.
    if any(abs(time - index / float(expected_fps)) > .0001 for index, time in enumerate(times)):
        raise RuntimeError('Video presentation timestamps are not the documented continuous cadence: ' + name)
    return {'frames': len(frames), 'width': path['width'], 'height': path['height'],
            'fps': str(expected_fps), 'duration_seconds': expected_frames / float(expected_fps),
            'complete_decode': True, 'continuous_timestamps': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--ffmpeg', type=Path, default=Path(os.environ.get('FFMPEG', '/usr/bin/ffmpeg')))
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9.-]+)?', args.version):
        parser.error('Use a semantic version, for example 0.1.0')
    if git('status', '--porcelain').strip():
        raise RuntimeError('Commit the complete source state before packaging')
    revision = git('rev-parse', '--verify', 'HEAD').decode().strip()
    missing = [name for name in REQUIRED_FILES + [REVIEW_FILE] if not local_file(name).is_file()]
    if missing: raise RuntimeError('Deliverables are incomplete: ' + ', '.join(missing))
    ffmpeg = args.ffmpeg.expanduser().resolve()
    if not ffmpeg.is_file() or not os.access(ffmpeg, os.X_OK):
        raise RuntimeError('A usable FFmpeg executable is required for complete video verification')
    output = (args.output or ROOT.parent / f'protolabs-campus-{args.version}.zip').resolve()
    destinations = [output, output.with_suffix('.sha256'), output.with_suffix('.json')]
    if output.suffix.lower() != '.zip': parser.error('--output must end in .zip')
    if any(os.path.lexists(path) for path in destinations):
        raise FileExistsError('Existing release or receipt is preserved: ' + ', '.join(str(p) for p in destinations if os.path.lexists(p)))
    review = read_json(REVIEW_FILE)
    if review.get('schema_version') != 1 or any(review.get(key) != 'inspected' for key in ('still_review', 'motion_review', 'motion_sample_review')):
        raise RuntimeError('Record actual still, sample and complete-film inspection before packaging')
    if review.get('source_revision') != revision:
        raise RuntimeError('Review receipt does not identify the clean source revision')
    if not isinstance(review.get('notes'), str) or not review['notes'].strip():
        raise RuntimeError('Review receipt must retain inspection notes and remaining approximations')
    try:
        reviewed_at = dt.datetime.fromisoformat(review['reviewed_at_utc'].replace('Z', '+00:00'))
        if reviewed_at.utcoffset() != dt.timedelta(0): raise ValueError('Use UTC')
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError('Review receipt requires an actual UTC inspection timestamp') from error
    hashes = {name: file_sha(local_file(name)) for name in REQUIRED_FILES}
    review_hash = file_sha(local_file(REVIEW_FILE))
    reviewed_files = review.get('reviewed_files', {})
    if not isinstance(reviewed_files, dict): raise RuntimeError('Review reviewed_files must map paths to SHA256 strings')
    for name, digest in hashes.items():
        if reviewed_files.get(name) != digest:
            raise RuntimeError('Review does not bind the current artifact bytes: ' + name)
    master_hash = hashes['scene/protolabs-campus.blend']
    if review.get('master_sha256') != master_hash: raise RuntimeError('Review master hash differs from the current master')
    viewer = read_json('scene/viewer-export.json')
    viewer_package = read_json('scene/viewer-package.json')
    path = read_json('deliverables/cinematic/path.json')
    sample = read_json('deliverables/motion-sample/path.json')
    if any(receipt.get('master_sha256') != master_hash for receipt in (viewer, path, sample)):
        raise RuntimeError('Scene, browser export, film and sample masters do not agree')
    if viewer.get('viewer_glb_sha256') != hashes['scene/protolabs-campus-viewer.glb']:
        raise RuntimeError('The browser export differs from its SHA256 receipt')
    if (viewer_package.get('master_sha256') != master_hash
            or viewer_package.get('source_glb_sha256') != hashes['scene/protolabs-campus-viewer.glb']
            or viewer_package.get('palette_sha256') != hashes['scene/materials.json']
            or viewer_package.get('optimized_glb_sha256') != hashes['viewer/public/models/campus.glb']):
        raise RuntimeError('The optimized walkthrough differs from its master, source or package receipt')
    precision = viewer_package.get('position_compression', {})
    if precision.get('positionComponentType') != 5126 or precision.get('decodedPositionsExact') is not True:
        raise RuntimeError('The walkthrough package lacks verified full-precision positions')
    if not re.fullmatch(r'[0-9a-f]{64}', path.get('camera_path_sha256', '')):
        raise RuntimeError('The full motion path fingerprint is missing')
    for key in ('camera_path_sha256', 'camera_path_hash_schema', 'camera_path_frame_count',
                'total_path_frames', 'width', 'height', 'fps', 'fps_base', 'path_seconds',
                'engine', 'motion_blur_shutter'):
        if sample.get(key) != path.get(key): raise RuntimeError('Sample and film have incompatible paths/settings: ' + key)
    total = path.get('total_path_frames')
    if not isinstance(total, int) or total < 1 or path.get('render_start') != 1 or path.get('render_end') != total:
        raise RuntimeError('The cinematic manifest does not describe the complete path')
    if path.get('camera_path_frame_count') != total or total != round(path['path_seconds'] * path['fps'] / path.get('fps_base', 1)):
        raise RuntimeError('Cinematic frame count, duration and path fingerprint coverage disagree')
    if not 1 <= sample.get('render_start', 0) <= sample.get('render_end', 0) <= total:
        raise RuntimeError('Invalid motion-sample frame range')
    gallery = read_json('deliverables/comparison/manifest.json')
    if gallery.get('current_pending_review') is not False or gallery.get('reviewed_iteration') != gallery.get('latest_version'):
        raise RuntimeError('The gallery still describes an unreviewed or historical current image')
    if gallery.get('current_aerial', {}).get('sha256') != hashes['deliverables/stills/reference_aerial.png']:
        raise RuntimeError('The gallery aerial is not the final production aerial (probe files are separate)')
    for name in VIEW_NAMES:
        filename = f'deliverables/stills/{name}.png'
        receipt = read_json(f'deliverables/stills/{name}.json')
        if receipt.get('master_sha256') != master_hash or receipt.get('image_sha256') != hashes[filename] or receipt.get('camera') != name:
            raise RuntimeError('Per-view receipt does not bind the final still and master: ' + name)
        if not inspect_png(local_file(filename), (receipt.get('width'), receipt.get('height')))['valid']:
            raise RuntimeError('Invalid or dimension-mismatched final still: ' + filename)
        if name != 'reference_aerial' and gallery.get('displayed_saved_views', {}).get(name, {}).get('sha256') != hashes[filename]:
            raise RuntimeError('The gallery displays a stale or historical saved view: ' + name)
    videos = {'film': inspect_video(ffmpeg, 'deliverables/flythrough.mp4', path, total),
              'sample': inspect_video(ffmpeg, 'deliverables/motion-sample.mp4', sample, sample['render_end'] - sample['render_start'] + 1)}
    assets = set(REQUIRED_FILES + [REVIEW_FILE])
    for pattern in ('research/images/*', 'deliverables/iterations/*/reference_aerial.png',
                    'deliverables/iterations/*/cameras.json', 'deliverables/iterations/*/stills/*.png',
                    'deliverables/iterations/*/motion-sample.mp4'):
        assets.update(str(p.relative_to(ROOT)) for p in ROOT.glob(pattern) if p.is_file())
    material_manifest = read_json('research/material-assets.json')
    for asset in material_manifest['assets']:
        if asset.get('status') == 'rejected_candidate': continue
        for entry in asset['files']:
            name = material_manifest['asset_directory'] + '/' + entry['filename']
            if file_sha(local_file(name)) != entry['sha256']:
                raise RuntimeError('Asset differs from its source receipt: ' + name)
            assets.add(name)
    output.parent.mkdir(parents=True, exist_ok=True)
    prefix = 'protolabs-campus/'
    manifest = {'version': args.version, 'source_revision': revision, 'master_sha256': master_hash,
                'video_verification': videos, 'files': {}}
    # Stage beside the destination, enabling an atomic no-overwrite hard link.
    with tempfile.TemporaryDirectory(prefix='.protolabs-release-', dir=output.parent) as temporary:
        temporary = Path(temporary)
        bundle = temporary / 'source-history.bundle'
        subprocess.run(['git', 'bundle', 'create', str(bundle), '--all'], cwd=ROOT, check=True)
        staged = temporary / 'release.zip'
        with zipfile.ZipFile(staged, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            def add(name, data):
                local_file(name)
                if name == 'DELIVERY-MANIFEST.json': raise ValueError('Reserved release path: ' + name)
                if name in manifest['files']:
                    if manifest['files'][name] != {'sha256': sha(data), 'bytes': len(data)}:
                        raise RuntimeError('Source and generated payload disagree: ' + name)
                    return
                archive.writestr(prefix + name, data)
                manifest['files'][name] = {'sha256': sha(data), 'bytes': len(data)}
            with tarfile.open(fileobj=io.BytesIO(git('archive', '--format=tar', revision))) as source:
                for item in source.getmembers():
                    if item.isfile(): add(item.name, source.extractfile(item).read())
                    elif not item.isdir(): raise ValueError('Unsupported source archive entry: ' + item.name)
            for name in sorted(assets): add(name, local_file(name).read_bytes())
            add('source-history.bundle', bundle.read_bytes())
            archive.writestr(prefix + 'DELIVERY-MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
        with zipfile.ZipFile(staged) as archive:
            for name, record in manifest['files'].items():
                data = archive.read(prefix + name)
                if len(data) != record['bytes'] or sha(data) != record['sha256']:
                    raise RuntimeError('Release verification failed: ' + name)
            # Catch a file replaced during packaging, not just corruption of the ZIP.
            for name, digest in {**hashes, REVIEW_FILE: review_hash}.items():
                if manifest['files'][name]['sha256'] != digest:
                    raise RuntimeError('Reviewed artifact changed while packaging: ' + name)
        receipt = {'archive': str(output), 'bytes': staged.stat().st_size,
                   'sha256': file_sha(staged), 'verified_files': len(manifest['files']),
                   'source_revision': revision, 'version': args.version, 'video_verification': videos}
        staged_sha = temporary / 'release.sha256'
        staged_json = temporary / 'release.json'
        staged_sha.write_text(receipt['sha256'] + '  ' + output.name + '\n')
        staged_json.write_text(json.dumps(receipt, indent=2) + '\n')
        published = []
        try:
            for source, destination in zip((staged, staged_sha, staged_json), destinations):
                os.link(source, destination)
                published.append((source, destination))
        except BaseException:
            for source, destination in published:
                if destination.exists() and os.path.samefile(source, destination): destination.unlink()
            raise
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__': main()
