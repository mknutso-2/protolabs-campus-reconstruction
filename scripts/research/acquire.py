#!/usr/bin/env python3
"""Download bounded, attributed evidence from a versioned source manifest.
Example: python acquire.py --raw-dir data/research/raw --include-reference-photos
Raw binary downloads are never required to be committed to Git.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path
import requests
MANIFEST=Path(__file__).with_name('sources.json')
UA='ProtolabsCampusReconstruction/1.0 (bounded public architecture research)'

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def fetch(session,source,destination,overwrite=False):
    expected=source.get('sha256')
    if destination.exists() and not overwrite:
        digest=sha256(destination)
        if expected and digest!=expected:raise ValueError(f'Existing {destination} fails recorded SHA256; preserve or remove it explicitly.')
        return {'status':'existing','sha256':digest,'size_bytes':destination.stat().st_size}
    url=source['url'];params=source.get('params');form=source.get('form');limit=source.get('max_bytes',150_000_000)
    if source.get('kind')=='arcgis_export':
        response=session.get(url,params=params,timeout=(20,120));response.raise_for_status();metadata=response.json()
        if 'href' not in metadata:raise ValueError(f'ArcGIS export error: {metadata}')
        (destination.parent/'aerial_2026_export.json').write_text(json.dumps(metadata,indent=2)+'\n')
        url=metadata['href'];params=None
    temporary=destination.with_name(destination.name+'.part')
    size=0
    try:
        response=session.post(url,data=form,timeout=(20,120),stream=True) if form else session.get(url,params=params,timeout=(20,120),stream=True)
        with response:
            response.raise_for_status()
            if int(response.headers.get('Content-Length',0))>limit:raise ValueError(f'{source["id"]}: server response exceeds bounded {limit} byte limit')
            with temporary.open('wb') as f:
                for chunk in response.iter_content(1024*1024):
                    if not chunk:continue
                    size+=len(chunk)
                    if size>limit:raise ValueError(f'{source["id"]}: response exceeds {limit} byte limit')
                    f.write(chunk)
        digest=sha256(temporary)
        if expected and digest!=expected:raise ValueError(f'{source["id"]}: SHA256 mismatch. Source changed; inspect before accepting new evidence.')
        if source.get('json'):
            body=json.loads(temporary.read_text())
            if 'error' in body:raise ValueError(f'{source["id"]}: API error: {body["error"]}')
        temporary.replace(destination)
        return {'status':'downloaded','sha256':digest,'size_bytes':size}
    finally:
        if temporary.exists():temporary.unlink()

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--raw-dir',type=Path,required=True);ap.add_argument('--include-reference-photos',action='store_true');ap.add_argument('--overwrite',action='store_true');ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
    manifest=json.loads(MANIFEST.read_text());sources=[s for s in manifest['sources'] if not s.get('optional_reference_photo') or args.include_reference_photos]
    if args.dry_run:
        print(json.dumps({'raw_dir':str(args.raw_dir),'download_count':len(sources),'bounded_maximum_bytes':sum(s['max_bytes'] for s in sources),'sources':[{k:s[k] for k in ['id','url','filename','max_bytes']} for s in sources]},indent=2));return
    args.raw_dir.mkdir(parents=True,exist_ok=True)
    session=requests.Session();session.headers['User-Agent']=UA;results=[]
    for source in sources:
        print('Acquiring',source['id'],flush=True);result=fetch(session,source,args.raw_dir/source['filename'],args.overwrite)
        results.append({'source_id':source['id'],'source_url':source['url'],'filename':source['filename'],'acquired_utc':datetime.now(timezone.utc).isoformat(),**result})
        (args.raw_dir/'acquisition_receipt.json').write_text(json.dumps({'manifest_date':manifest['snapshot_date'],'results':results},indent=2)+'\n')
    print('Complete. Geometry processing: python process.py --raw-dir',args.raw_dir,'--output-dir PATH')
if __name__=='__main__':main()
