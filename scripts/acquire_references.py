#!/usr/bin/env python3
"""Acquire the three attributed photograph caches used by the comparison viewer.

Python standard library only. Existing matching files are reused. The committed
manifest preserves the exact cached image hashes and original acquisition dates.

    python scripts/acquire_references.py --dry-run
    python scripts/acquire_references.py --verify-only
    python scripts/acquire_references.py

Public accessibility does not establish a redistribution license. Consult the
source ledger and manifest rights note before distributing reference imagery.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'research/reference-cache-manifest.json'
USER_AGENT = 'ProtolabsCampusReconstruction/1.0 (public architectural reference cache)'
RETRYABLE_HTTP = {408, 429, 500, 502, 503, 504}
EXPECTED_FILENAMES = {
    'protolabs-official-hq-drone.jpg',
    'businessjournal-entrance-2018.jpg',
    'machine-design-frontage-2024.png',
}


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify(path: Path, entry: dict) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f'Missing cache: {path.name}')
    size = path.stat().st_size
    if size != entry['size_bytes']:
        raise ValueError(f'{path.name}: size differs from the recorded reference snapshot')
    digest = checksum(path)
    if digest != entry['sha256']:
        raise ValueError(f'{path.name}: SHA256 differs from the recorded reference snapshot')
    return {'filename': path.name, 'size_bytes': size, 'sha256': digest}


def download(path: Path, entry: dict, attempts: int = 3) -> dict:
    """Retry transient HTTP/network errors; changed image content is never accepted."""
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + '.part')
    request = Request(entry['asset_url'], headers={
        'User-Agent': USER_AGENT,
        'Accept': '*/*',
        'Referer': entry['source_page_url'],
    })
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=45) as response:
                limit = entry['max_download_bytes']
                if int(response.headers.get('Content-Length') or 0) > limit:
                    raise ValueError(f'{path.name}: server response exceeds the bounded download limit')
                size = 0
                with partial.open('wb') as destination:
                    while chunk := response.read(256 * 1024):
                        size += len(chunk)
                        if size > limit:
                            raise ValueError(f'{path.name}: download exceeded its byte limit')
                        destination.write(chunk)
            result = verify(partial, entry)
            partial.replace(path)
            return {**result, 'filename': path.name, 'status': 'downloaded',
                    'retrieved_utc': datetime.now(timezone.utc).isoformat()}
        except HTTPError as error:
            if error.code not in RETRYABLE_HTTP or attempt + 1 == attempts:
                raise
            time.sleep(min(2 ** attempt, 4))
        except (URLError, TimeoutError, ConnectionError):
            if attempt + 1 == attempts:
                raise
            time.sleep(min(2 ** attempt, 4))
        finally:
            if partial.exists():
                partial.unlink()
    raise RuntimeError('Reference download did not complete')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--dry-run', action='store_true', help='Show exactly three source URLs and cache paths without network or writes')
    modes.add_argument('--verify-only', action='store_true', help='Verify existing cache sizes and SHA256s without network or writes')
    parser.add_argument('--cache-dir', type=Path, default=ROOT / 'research/images', help='Override the local cache directory')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    entries = manifest['references']
    if len(entries) != 3 or {e['filename'] for e in entries} != EXPECTED_FILENAMES:
        raise ValueError('Manifest must contain exactly the three comparison photographs')
    for entry in entries:
        if Path(entry['filename']).name != entry['filename']:
            raise ValueError('Manifest cache filenames must not contain directory traversal')
    if args.dry_run:
        print(json.dumps({'mode': 'dry-run', 'network_requests': 0,
                          'snapshot_date': manifest['manifest_created_date'],
                          'references': [{k: e[k] for k in ('filename', 'cache_path', 'viewer_path', 'asset_url', 'sha256', 'size_bytes')} for e in entries]}, indent=2))
        return 0
    results, errors = [], []
    for entry in entries:
        path = args.cache_dir / entry['filename']
        try:
            if args.verify_only or path.exists():
                result = {**verify(path, entry), 'status': 'verified-existing'}
            else:
                result = download(path, entry)
            results.append(result)
            print(f'{result["status"]}: {entry["filename"]} ({result["size_bytes"]} bytes)')
        except (OSError, ValueError) as error:
            errors.append({'filename': entry['filename'], 'error': str(error)})
            print(f'ERROR: {entry["filename"]}: {error}', file=sys.stderr)
    # The immutable committed manifest is never rewritten by acquisition.
    if any(r['status'] == 'downloaded' for r in results):
        receipt = {'checked_utc': datetime.now(timezone.utc).isoformat(),
                   'source_manifest': 'research/reference-cache-manifest.json',
                   'results': results, 'errors': errors}
        (args.cache_dir / 'reference-acquisition-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    if errors:
        print('Preserve or remove a mismatching cache explicitly after reviewing the source; this script does not overwrite or accept changed images.', file=sys.stderr)
        return 1
    print('All three reference caches match the recorded snapshot.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
