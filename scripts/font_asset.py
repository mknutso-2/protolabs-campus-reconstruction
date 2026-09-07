"""Verify and load the exact, redistributable font used by the reconstruction.

The tracked font supports offline checkout. Only byte-identical system copies
may substitute for it; missing/corrupt fonts never fall back to Blender Bfont.
Ordinary Python needs only its standard library. bpy is imported by the loader.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _local_file(root, name):
    relative = Path(name)
    path = root / relative
    if relative.is_absolute() or '..' in relative.parts or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Font asset path must remain inside the source checkout')
    return path


def _manifest(root):
    record = json.loads((root/'research/font-asset.json').read_text())
    if record.get('schema_version') != 1:
        raise ValueError('Unsupported font manifest schema')
    notice = _local_file(root, record['license']['file'])
    if not notice.is_file() or file_sha(notice) != record['license']['sha256']:
        raise ValueError('The required pinned font license notice is missing or changed')
    return record


def _matches(path, record):
    try:
        return path.is_file() and path.stat().st_size == record['bytes'] and file_sha(path) == record['sha256']
    except OSError:
        return False


def resolve_font_path(root=ROOT, *, prefer_system=True, system_path=None):
    """Return a verified font path; never replace it with a different typeface."""
    root = Path(root)
    record = _manifest(root)
    bundled = _local_file(root, record['file'])
    if not _matches(bundled, record):
        raise ValueError('Tracked font missing or changed: restore ' + record['file'] +
                         ' from the source revision, or use --restore-from-system with matching bytes')
    system = Path(system_path) if system_path is not None else Path(record['acquisition']['system_path'])
    return system if prefer_system and _matches(system, record) else bundled


def restore_from_system(root=ROOT, *, system_path=None):
    """Restore only a missing tracked asset from an exact matching local file."""
    root = Path(root)
    record = _manifest(root)
    destination = _local_file(root, record['file'])
    if destination.exists() or destination.is_symlink():
        if not _matches(destination, record):
            raise FileExistsError('Existing mismatching font is preserved: ' + str(destination))
        return destination
    system = Path(system_path) if system_path is not None else Path(record['acquisition']['system_path'])
    if not _matches(system, record):
        raise ValueError('System font does not match the pinned bytes; restore the tracked source asset')
    data = system.read_bytes()
    if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
        raise ValueError('System font changed during verification')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        stream.write(data)
    return destination


def load_blender_font(root=ROOT, *, prefer_system=True, system_path=None):
    """Load verified outlines once per Blender data path; generator packs on save."""
    path = resolve_font_path(root, prefer_system=prefer_system, system_path=system_path)
    import bpy
    return bpy.data.fonts.load(str(path), check_existing=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--system-font', type=Path, help='Alternate local source; exact pinned bytes are still required')
    parser.add_argument('--bundled-only', action='store_true', help='Verify and select the tracked copy without using a system font')
    parser.add_argument('--restore-from-system', action='store_true', help='Restore a missing bundled font from an exact local match; preserve existing files')
    args = parser.parse_args()
    if args.restore_from_system:
        restore_from_system(args.root, system_path=args.system_font)
    selected = resolve_font_path(args.root, prefer_system=not args.bundled_only, system_path=args.system_font)
    record = _manifest(args.root)
    print(json.dumps({'font': str(selected), 'bytes': selected.stat().st_size,
                      'sha256': file_sha(selected), 'license': record['license']['file'],
                      'bundled_font_verified': True, 'network_required': False}, indent=2))
