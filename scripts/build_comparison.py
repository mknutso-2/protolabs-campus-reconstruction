#!/usr/bin/env python3
"""Build an offline comparison from existing reference and render files.

Run: python3 scripts/build_comparison.py --latest-version v07
The latest image is pending review unless --reviewed-latest is explicitly used
AFTER full-image inspection. Existing iteration snapshots are read-only inputs;
this script never creates, copies, refreshes, or overwrites them.
No external libraries, network requests, image alterations, or build tooling.
"""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import html
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'deliverables/comparison'

def png_size(path):
    with path.open('rb') as f:
        head=f.read(24)
    if len(head) != 24 or head[:8] != b'\x89PNG\r\n\x1a\n' or head[12:16] != b'IHDR':
        raise ValueError('Expected PNG: '+str(path))
    return list(struct.unpack('>II',head[16:24]))

def record(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'size_bytes':path.stat().st_size, 'size_px':png_size(path),
            'file_modified_utc':dt.datetime.fromtimestamp(path.stat().st_mtime,dt.timezone.utc).isoformat()}

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--latest-version',default='v07',help='Version assigned to the current working images (default: v07)')
parser.add_argument('--reviewed-latest',action='store_true',help='Use only after inspecting the latest aerial and all three latest saved stills; this records inspection, not photographic equivalence')
args=parser.parse_args()
if not re.fullmatch(r'v[0-9]{2,}',args.latest_version):
    parser.error('--latest-version must look like v06 or v12')
current=ROOT/'deliverables/reference_aerial.png'
current_url='../reference_aerial.png'
if args.reviewed_latest:
    current=ROOT/'deliverables/stills/reference_aerial.png'
    current_url='../stills/reference_aerial.png'
    master_hash=hashlib.sha256((ROOT/'scene/protolabs-campus.blend').read_bytes()).hexdigest()
    for name in ('reference_aerial','entrance_detail','arrival','campus_overview'):
        path=ROOT/f'deliverables/stills/{name}.png'
        receipt=json.loads(path.with_suffix('.json').read_text())
        if receipt['master_sha256']!=master_hash or receipt['image_sha256']!=hashlib.sha256(path.read_bytes()).hexdigest():
            raise SystemExit('Reviewed gallery requires all four renders from the current master: '+name)
if not current.exists(): raise SystemExit('Missing current aerial: '+str(current))
if not (ROOT/'scene/cameras.json').exists(): raise SystemExit('Missing current camera record')
fit=json.loads((ROOT/'research/reference_drone_camera_fit.json').read_text())
notes={
 'v01':'Early massing and initial daylight image. Roof extent, grading artifacts and facade treatment visibly differ from the photograph.',
 'v02':'Landscape and material iteration. Sparse tree crowns, window recesses and entrance roof treatment remain conspicuous.',
 'v03':'Revised framing and generic parked vehicles. Sparse foliage and dark glazing are still visible.',
 'v04':'Preserved reviewed iteration. Fitted aerial camera, dense procedural crowns, revised glazing and entrance roof treatment. Photographic realism remains incomplete.',
 'v05':'Preserved rejected landscape iteration. The oversized continuous forest band placed trees across pond and open ground. Its scene, stills and one-second motion sample remain available as a historical record, not an accepted landscape solution.',
 'v06':'North context revised using 102 eligible canopy-envelope candidates and a ground grid derived from the cached 2022 lidar tile. Candidate centers are inferred envelope peaks, not surveyed trunks; crown shape and species remain procedural. The 2026 aerial cross-check only covers the southern portion.',
 'v07':'Licensed metric textures and reference-oriented sunset lighting; corrected campus canopy heights and aerial crown widths; fitted monument assembly, refined glazing, doors, flag and vehicle geometry. Distant woods use traced belts and conservative NLCD forest interiors, with inferred crown shapes and heights. Species, detailed landscaping and unseen elevations remain approximate.'}
versions=[]
iteration_root=ROOT/'deliverables/iterations'
snapshots=sorted((p for p in iteration_root.iterdir() if p.is_dir() and re.fullmatch(r'v[0-9]{2,}',p.name)),key=lambda p:int(p.name[1:])) if iteration_root.exists() else []
for directory in snapshots:
    path=directory/'reference_aerial.png'
    if not path.exists(): continue
    if not (directory/'cameras.json').exists(): raise SystemExit('Missing preserved camera record: '+str(directory/'cameras.json'))
    version=directory.name
    versions.append({'id':version,'label':version.upper(),'url':f'../iterations/{version}/reference_aerial.png',
        'camera':f'../iterations/{version}/cameras.json','note':notes.get(version,'Preserved iteration; no reviewed fidelity claim.'),
        'preserved':True,'review_status':'reviewed_with_limitations' if version=='v04' else ('landscape_rejected' if version=='v05' else 'historical'),
        'caption':version.upper()+' · '+('landscape rejected' if version=='v05' else 'preserved iteration'),
        'additional_artifacts':{name:f'../iterations/{version}/{name}' for name in ('stills/entrance_detail.png','stills/arrival.png','stills/campus_overview.png','motion-sample.mp4') if (directory/name).exists()},**record(path)})
preserved_versions=list(versions)
if any(v['id']==args.latest_version for v in versions):
    raise SystemExit('Latest version already has a preserved snapshot. Choose a new --latest-version; snapshots are never replaced.')
if versions and int(args.latest_version[1:])<=max(int(v['id'][1:]) for v in versions):
    raise SystemExit('--latest-version must be newer than all preserved iterations')
latest_status='reviewed_with_limitations' if args.reviewed_latest else 'pending_review'
latest_suffix='visually inspected; limitations remain' if args.reviewed_latest else 'pending full-image review'
latest_note=notes.get(args.latest_version,'Latest working reconstruction; fidelity and motion acceptance require separate checks.')+' '+latest_suffix.capitalize()+'.'
latest={'id':args.latest_version,'label':args.latest_version.upper()+' · latest','url':current_url,
    'camera':'../../scene/cameras.json','note':latest_note,'preserved':False,'review_status':latest_status,
    'caption':args.latest_version.upper()+' · '+latest_suffix,**record(current)}
versions.append(latest)
default=latest
view_names=('entrance_detail','arrival','campus_overview')
if args.reviewed_latest:
    missing=[name for name in view_names if not (ROOT/f'deliverables/stills/{name}.png').exists()]
    if missing: raise SystemExit('--reviewed-latest requires all three latest stills; missing: '+', '.join(missing))
reviewed_version=args.latest_version if args.reviewed_latest else 'v04'
views_root=ROOT/'deliverables/stills' if args.reviewed_latest else ROOT/'deliverables/iterations/v04/stills'
views_url='../stills' if args.reviewed_latest else '../iterations/v04/stills'
manifest={'gallery_kind':'Offline visual comparison; not the interactive 3D viewer',
    'source_reference':'research/images/protolabs-official-hq-drone.jpg',
    'generated_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
    'reviewed_iteration':reviewed_version,'review_claim':'Image inspection only; photographic equivalence and motion acceptance are not implied.',
    'latest_version':args.latest_version,'latest_review_status':latest_status,'current_pending_review':not args.reviewed_latest,
    'current_aerial':record(current),'iterations':versions,
    'displayed_saved_views':{name:record(views_root/f'{name}.png') for name in view_names if (views_root/f'{name}.png').exists()},
    'canopy_evidence':'docs/canopy-evidence.md',
    'accuracy_summary':'docs/accuracy-summary.md',
    'camera_fit':{'weighted_rms_px':fit['rms_pixel_weighted'],'unweighted_rmse_px':fit['rmse_pixel_unweighted'],
        'landmarks':len(fit['landmarks']),'source_size_px':fit['reference_size'],
        'note':'Residuals describe selected manually annotated landmarks, not whole-image fidelity or metric survey accuracy.'}}
DEST.mkdir(parents=True,exist_ok=True)
(DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

TEMPLATE=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Protolabs · Evidence & iteration</title>
<style>
:root{--ink:#152a36;--muted:#5f6f78;--line:#d8e0e3;--paper:#f4f6f5;--blue:#087aa1;--white:#fff;--accent:#daf0f4}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:var(--blue);text-underline-offset:3px}a:hover{color:#034d68}button,input{font:inherit}button,a{touch-action:manipulation}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #d79522;outline-offset:3px}header{background:#142b38;color:#f7fbfc;padding:42px max(24px,calc((100vw - 1320px)/2)) 35px}header p{max-width:860px;margin:.6rem 0;color:#cbdde5}.eyebrow{font-size:12px;font-weight:750;letter-spacing:.17em;text-transform:uppercase}.eyebrow span{color:#6bd3e9}h1{font-size:clamp(30px,4vw,49px);line-height:1.12;letter-spacing:-.035em;margin:14px 0}nav{display:flex;gap:22px;flex-wrap:wrap;margin-top:24px}nav a{color:#bce7f1;font-size:14px}main{max-width:1370px;margin:auto;padding:32px 25px 65px}h2{font-size:25px;line-height:1.25;letter-spacing:-.025em;margin:0 0 9px}h3{font-size:18px;margin:0 0 6px}p{margin:.4em 0 .9em}section{margin-bottom:42px}.lead{color:var(--muted);max-width:1020px}.notice{border-left:4px solid var(--blue);padding:15px 20px;background:#e5f0f2;margin:0 0 28px}.notice p{margin:0}.tools{display:flex;justify-content:space-between;gap:16px;align-items:center;flex-wrap:wrap;margin:20px 0 12px}.segmented{display:flex;flex-wrap:wrap;gap:3px;background:#e0e7e9;padding:4px;border-radius:7px}.segmented button{border:0;border-radius:4px;background:transparent;color:var(--ink);padding:9px 16px;cursor:pointer;font-size:14px}.segmented button[aria-pressed="true"]{background:var(--white);box-shadow:0 1px 3px #1232;color:#045f80;font-weight:750}.frames{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0;min-width:0;background:var(--white);border:1px solid var(--line);border-radius:7px;overflow:hidden}figure img{display:block;width:100%;height:auto}figcaption{font-size:13px;color:var(--muted);padding:12px 15px}figcaption strong{display:block;color:var(--ink);font-size:14px;margin-bottom:3px}.caption-links{display:flex;gap:18px;flex-wrap:wrap;margin:12px 0;color:var(--muted);font-size:13px}.version-note{font-size:14px;color:var(--muted);min-height:2em}.wipe{position:relative;aspect-ratio:3/2;background:#d9e2e5;border-radius:7px;overflow:hidden;border:1px solid var(--line)}.wipe img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.wipe .top{clip-path:inset(0 0 0 50%)}.divider{position:absolute;top:0;bottom:0;left:50%;border-left:2px solid #fff;filter:drop-shadow(0 1px 3px #0008);pointer-events:none}.divider:after{content:'↔';position:absolute;top:48%;left:-20px;width:38px;height:38px;background:white;color:#12333f;border-radius:50%;text-align:center;font-size:24px;line-height:34px}.wipe-tag{position:absolute;top:14px;padding:5px 9px;background:#102c3dd9;color:#fff;border-radius:4px;font-size:12px;z-index:3}.wipe-tag.left{left:14px}.wipe-tag.right{right:14px}.range-label{display:flex;align-items:center;gap:18px;margin:12px 0;color:var(--muted);font-size:13px}.range-label input{flex:1;accent-color:var(--blue)}[hidden]{display:none!important}.archive{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}.archive img{aspect-ratio:3/2;object-fit:contain;background:#dce2e1}.archive figcaption{min-height:145px}.archive a.image-link{display:block}.badge{display:inline-block;background:var(--accent);color:#075e77;border-radius:4px;padding:3px 7px;font-size:11px;font-weight:700;vertical-align:middle;margin-left:5px}.review-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}.review-box{background:white;border:1px solid var(--line);border-radius:7px;padding:23px}.review-box ul,.review-box ol{padding-left:20px;margin:12px 0 0}.review-box li{margin:0 0 10px}.review-box li:last-child{margin:0}.mini{font-size:13px;color:var(--muted)}.pair{margin-top:25px}.pair .frames figure img{aspect-ratio:3/2;object-fit:contain;background:#dce2e1}.wide-image{max-width:100%;display:block;border-radius:7px;border:1px solid var(--line)}details{background:white;border:1px solid var(--line);border-radius:7px;padding:15px 20px;margin:15px 0}summary{font-weight:650;cursor:pointer}details p{margin:15px 0 5px}.source-list{display:grid;grid-template-columns:1fr 1fr;gap:18px}.source{border-top:1px solid var(--line);padding:16px 0 0}.source p{font-size:14px;color:var(--muted)}footer{border-top:1px solid var(--line);padding-top:22px;color:var(--muted);font-size:13px}.metric{font-variant-numeric:tabular-nums;font-weight:750;color:var(--ink)}@media(max-width:900px){.archive{grid-template-columns:1fr 1fr}.frames,.review-grid,.source-list{grid-template-columns:1fr}.tools{align-items:flex-start}.archive figcaption{min-height:0}header{padding:32px 25px}.frames figure img{max-height:none}.segmented button{padding:9px 12px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{header{background:white;color:black;padding:0}header p,nav a{color:#333}main{padding:18px 0}.tools,.range-label,nav{display:none}.archive{grid-template-columns:1fr 1fr}.review-grid{grid-template-columns:1fr}figure,section{break-inside:avoid}.wipe-wrap{display:none!important}.frames{display:grid!important}a{color:inherit}}
</style></head><body>
<header><div class="eyebrow">Protolabs / Maple Plain <span>· Evidence & iteration</span></div>
<h1>A reconstruction, beside its evidence.</h1>
<p>5540 Pioneer Creek Drive, Minnesota. __HISTORY_COUNT__ preserved aerial iterations, the latest working render, the photographs that informed them, and the visible limits of the current model.</p>
<nav aria-label="Page sections"><a href="#compare">Compare</a><a href="#iterations">Iteration history</a><a href="#review">Visual review</a><a href="#other-views">Other saved views</a><a href="#sources">Sources & dates</a></nav></header>
<main>
<div class="notice"><p>__LATEST_NOTICE__</p></div>
<section id="compare"><h2>__COMPARE_TITLE__</h2><p class="lead">The aerial camera was fitted to selected roof, flagpole and facade landmarks. Materials, lighting, planting and parking still differ visibly. The wipe is an inspection aid; it is not a whole-image accuracy score.</p>
<div class="tools"><div class="segmented" aria-label="Choose reconstruction iteration">__VERSION_BUTTONS__</div><div class="segmented" aria-label="Comparison display"><button id="sideButton" type="button" aria-pressed="true">Side by side</button><button id="wipeButton" type="button" aria-pressed="false">Image wipe</button></div></div>
<div id="sideFrames" class="frames"><figure><img src="../../research/images/protolabs-official-hq-drone.jpg" alt="Official Protolabs headquarters aerial at sunset, showing the brick left block, sloping silver entrance roof and white glazed right wing"><figcaption><strong>Photographic reference · Proto Labs, Inc.</strong>Undated official aerial. Same photographic setup as the official file named “2024”; exact capture date is unverified.</figcaption></figure><figure><img id="renderSide" src="__DEFAULT_URL__" alt="Selected reconstruction rendered from the saved aerial camera"><figcaption><strong id="renderCaption">__DEFAULT_CAPTION__</strong>Lighting varies across iterations; V07 uses a low-sun environment. Images are shown without retouching.</figcaption></figure></div>
<div id="wipeWrap" class="wipe-wrap" hidden><div class="wipe"><img src="../../research/images/protolabs-official-hq-drone.jpg" alt="Official headquarters photographic reference"><img id="renderWipe" class="top" src="__DEFAULT_URL__" alt="Reconstruction overlay"><span class="wipe-tag left">Photograph</span><span id="wipeTag" class="wipe-tag right">__DEFAULT_CAPTION__</span><span id="divider" class="divider"></span></div><label class="range-label" for="wipeRange">Photograph ←<input id="wipeRange" type="range" min="0" max="100" value="50" aria-label="Move the boundary between photograph and reconstruction">→ Reconstruction</label></div>
<div class="caption-links"><a href="../../research/images/protolabs-official-hq-drone.jpg" target="_blank" rel="noopener">Open full reference</a><a id="fullRender" href="__DEFAULT_URL__" target="_blank" rel="noopener">Open full reconstruction</a><a id="cameraLink" href="__DEFAULT_CAMERA__">Saved camera data</a><a href="__CURRENT_URL__" target="_blank" rel="noopener">Current aerial</a></div><p id="versionNote" class="version-note">__DEFAULT_NOTE__</p>
<details><summary>What does the camera fit establish?</summary><p>Eleven manually annotated landmarks were fitted to 3D correspondences. On the 1200 × 800 source, the recorded weighted RMS is <span class="metric">3.17 px</span>; the unweighted RMSE is <span class="metric">7.87 px</span>. One partly obscured roof correspondence is about 20 px away. These residuals apply only to the selected points, depend on their manual annotation and weights, and do not certify whole-building dimensions or photographic fidelity. <a href="../../research/reference_drone_camera_fit.json">Inspect the complete fit.</a></p><p class="mini">The current render is __CURRENT_DIMENSIONS__, close to the source aspect ratio. Scaling within this page does not refit either camera. Earlier iterations deliberately retain their earlier cameras.</p></details></section>
<section id="iterations"><h2>Preserved iterations, kept intact.</h2><p class="lead">Each card opens its original image and camera record. The latest working __LATEST_VERSION__ is separate and is labelled with its explicit review state. The generator reads existing snapshots without copying or replacing them. V05 remains as evidence of the rejected forest-band treatment.</p><div class="archive">__ARCHIVE__</div></section>
<section id="review"><h2>What matches, and what remains visible.</h2><p class="lead"><a href="../../docs/accuracy-summary.md">Read the concise accuracy account</a> for evidence dates, inferred details and differences between the rendered and interactive views.</p><div class="review-grid"><div class="review-box"><h3>Recognizable features</h3><ul><li>The broad low-rise composition: a darker left block, white right wing and central sloping silver roof.</li><li>The projecting white entrance truss, fan braces, dark cylindrical supports and glass vestibule.</li><li>The left facade’s repeated narrow windows and the right wing’s continuous glazed band.</li><li>The flagpole island, monument sign, parking surfaces and planted edges establish the arrival setting.</li><li>The fitted aerial brings several important silhouette landmarks into approximate image alignment.</li></ul></div><div class="review-box"><h3>Largest remaining discrepancies</h3><ol><li><strong>Material and light response.</strong> V07 adds metric surface scans and a coherent low-sun environment. These are licensed material and lighting proxies: the source photograph’s richer color, weathering and sky are not reproduced exactly.</li><li><strong>Glazing and entrance detail.</strong> Coated glazing and a fitted lower fascia improve the frontage. Reflections remain less varied than the photograph; door, column, truss connection and hidden return dimensions remain partly inferred.</li><li><strong>Landscape.</strong> Near-campus heights use dated lidar constraints, with explicit omissions and limited inferred placements. Distant woods use traced coverage, inferred crowns and a coarse regional DEM. Generic tree forms, incomplete distant woodland, homes and roads remain visible limitations. <a href="../../docs/canopy-evidence.md">Near canopy evidence.</a> <a href="../../docs/distant-context.md">Distant terrain and woods.</a></li><li><strong>Parking and ground treatment.</strong> Surface boundaries and markings are interpreted from the aerial; curbs, accessibility details, drainage and seasonal water extent are approximate. Forecourt vehicles are omitted to match the empty reference, while distant occupancy remains generic.</li><li><strong>Small details and unseen areas.</strong> Branding geometry, flag pose, hydrant, curb profiles and rooftop equipment are simplified. Rear elevations and hidden equipment are not verified by these frontage photographs.</li></ol></div></div><p class="mini" style="margin-top:15px">Earlier images retain their original geometry and appearance. V05’s landscape was rejected; later iterations correct specific discrepancies documented in the accuracy record. __REVIEW_STATE__ This is a visual record, not an engineering survey. <a href="../../docs/visual-accuracy.md">Read the full accuracy record and missing quality milestones.</a></p></section>
<section id="other-views"><h2>__VIEWS_HEADING__</h2><p class="lead">__VIEWS_INTRO__ Their cameras are intentionally labelled approximate. A related photograph is context, not proof that the two views are registered. Historic branding and seasonal conditions also differ.</p>
__OTHER_VIEWS__
<div class="pair"><h3>Campus overview <span class="badge">Approximate oblique overview</span></h3><p class="mini">Useful for footprint, parking and landscape context. It is not aligned to the county’s top-down aerial, and the vegetation and vehicles are an inferred presentation state.</p><a href="__OVERVIEW_URL__" target="_blank" rel="noopener"><img class="wide-image" src="__OVERVIEW_URL__" alt="__VIEWS_VERSION__ high oblique campus overview reconstruction" loading="lazy"></a></div></section>
<section id="sources"><h2>Sources, attribution and capture dates</h2><p class="lead">The page and its images open offline. The following links lead to the original publishers when an internet connection is available. Reference photographs remain attributed to their owners; public access is not a redistribution license.</p><div class="source-list">
<div class="source"><h3>Official headquarters aerials</h3><p>Proto Labs, Inc. The wide drone image is undated. The current locations-page filename includes “2024”; that does not independently establish the capture date. Retrieved 7 September 2026.</p><a href="https://www.protolabs.com/media/s4dignhf/hq-drone.jpg">Wide drone image</a> · <a href="https://www.protolabs.com/media/sj0nwkxv/hq_mp_exterior_2024.jpg">Official “2024” image</a> · <a href="https://www.protolabs.com/about-us/locations/">Location directory</a></div>
<div class="source"><h3>Entrance close-up</h3><p>Minneapolis / St. Paul Business Journal, article dated 6 December 2018; exact photograph date and photographer were not independently verified. Historic green/blue lettering differs from the current interpretation.</p><a href="https://www.bizjournals.com/twincities/news/2018/12/06/2018-business-of-manufacturing-proto-labs-inc.html">Original article</a></div>
<div class="source"><h3>Ground-level arrival</h3><p>Machine Design, image credited to Protolabs; article dated 26 January 2024. The photograph’s capture date is unknown. Snow and dormant planting document a different season from the render.</p><a href="https://www.machinedesign.com/automation-iiot/article/21281562/protolabs-qa-protolabs-rebranded-manufacturing-partner-network-expands-capabilities">Original article</a></div>
<div class="source"><h3>Geospatial and asset provenance</h3><p>Hennepin County imagery and public lidar constrain the site independently of the photograph. Visual traces, dates and measurement limits are retained in the ledger. Vegetation and vehicles are original generic procedural assets.</p><a href="../../research/geospatial-sources.json">Geospatial sources</a> · <a href="../../research/architecture-sources.json">Architecture ledger</a> · <a href="../../docs/vegetation-provenance.md">Vegetation asset provenance</a> · <a href="../../docs/canopy-evidence.md">North canopy placement evidence</a> · <a href="../../research/north_context_canopy_constraints.json">Canopy constraints</a> · <a href="../../docs/vehicle-provenance.md">Vehicle provenance</a></div></div></section>
<footer>This gallery is separate from the 3D viewer. No network fetches, external fonts or external scripts are required. Rebuild with <code>python3 scripts/build_comparison.py</code>. <a href="manifest.json">Image hashes, dimensions and snapshot manifest</a>.</footer>
</main><script>
'use strict';
const versions=__VERSIONS_JSON__;
const q=id=>document.getElementById(id);
for(const button of document.querySelectorAll('[data-version]')) button.addEventListener('click',()=>{
 const v=versions.find(item=>item.id===button.dataset.version);
 for(const b of document.querySelectorAll('[data-version]')) b.setAttribute('aria-pressed',String(b===button));
 q('renderSide').src=v.url;q('renderWipe').src=v.url;q('renderSide').alt=v.caption+' reconstruction';q('fullRender').href=v.url;q('cameraLink').href=v.camera;
 q('renderCaption').textContent=v.caption;q('wipeTag').textContent=v.caption;q('versionNote').textContent=v.note;
});
function mode(wipe){q('sideFrames').hidden=wipe;q('wipeWrap').hidden=!wipe;q('sideButton').setAttribute('aria-pressed',String(!wipe));q('wipeButton').setAttribute('aria-pressed',String(wipe));}
q('sideButton').addEventListener('click',()=>mode(false));q('wipeButton').addEventListener('click',()=>mode(true));
q('wipeRange').addEventListener('input',event=>{const v=event.target.value;q('renderWipe').style.clipPath='inset(0 0 0 '+v+'%)';q('divider').style.left=v+'%';});
</script></body></html>'''

buttons=''.join(f'<button type="button" data-version="{v["id"]}" aria-pressed="{str(v["id"]==default["id"]).lower()}">{v["label"]}</button>' for v in versions)
archive=''
artifact_labels={'stills/entrance_detail.png':'Entrance','stills/arrival.png':'Arrival','stills/campus_overview.png':'Overview','motion-sample.mp4':'Preliminary motion sample'}
for v in preserved_versions:
    badge=' <span class="badge">Historical review</span>' if v['id']=='v04' else (' <span class="badge">Landscape rejected</span>' if v['id']=='v05' else '')
    extra=' · '.join(f'<a href="{url}" target="_blank" rel="noopener">{artifact_labels[name]}</a>' for name,url in v['additional_artifacts'].items())
    archive+=f'<figure><a class="image-link" href="{v["url"]}" target="_blank" rel="noopener"><img src="{v["url"]}" alt="Preserved {v["id"]} aerial reconstruction" loading="lazy"></a><figcaption><strong>{v["label"]}{badge}</strong>{html.escape(v["note"])}<br><a href="{v["camera"]}">Camera record</a> · {v["size_px"][0]} × {v["size_px"][1]}'+(f'<br>{extra}' if extra else '')+'</figcaption></figure>'
pairs=[('Entrance detail','entrance_detail','businessjournal-entrance-2018.jpg','Historic entrance photograph · published 2018','White fan braces, cylindrical supports, sloping roof and vestibule provide the structural reference. Precise framing and dimensions are not established by the approximate saved camera.'),
       ('Arrival','arrival','machine-design-frontage-2024.png','Protolabs image in Machine Design · published 2024','The reference has winter planting and snow; the render uses a leaf-on, low-sun setting and an approximate arrival camera.')]
other=''
for title,name,ref,label,note in pairs:
    if not (views_root/f'{name}.png').exists():
        other+=f'<p>{title}: no preserved reviewed still is available at generation.</p>'
        continue
    view_url=f'{views_url}/{name}.png'
    other+=f'<div class="pair"><h3>{title} <span class="badge">Approximate camera</span></h3><p class="mini">{note}</p><div class="frames"><figure><a href="../../research/images/{ref}" target="_blank" rel="noopener"><img src="../../research/images/{ref}" alt="{label}" loading="lazy"></a><figcaption><strong>{label}</strong>Exact capture date unverified.</figcaption></figure><figure><a href="{view_url}" target="_blank" rel="noopener"><img src="{view_url}" alt="Reviewed {reviewed_version} {title.lower()} reconstruction still" loading="lazy"></a><figcaption><strong>Inspected {reviewed_version.upper()} {title.lower()} still</strong>Approximate saved view; not photographically registered.</figcaption></figure></div></div>'
if args.reviewed_latest:
    latest_notice=f'<strong>{args.latest_version.upper()} visually inspected:</strong> the latest aerial and three saved stills have been inspected. Documented geometry, materials and landscape limitations remain; this status does not claim photographic equivalence or accept motion quality.'
    review_state=f'{args.latest_version.upper()} latest images have been visually inspected; the review label records inspection, not a final-quality pass.'
    views_intro='These latest saved stills were explicitly marked inspected when this gallery was generated.'
else:
    latest_notice=f'<strong>{args.latest_version.upper()} pending review:</strong> this latest working render has not yet been marked inspected. The historical v04 assessment established recognizable architecture with substantial visual approximations; v05’s oversized forest band was rejected.'
    review_state=f'{args.latest_version.upper()} remains pending full-image inspection.'
    views_intro='These preserved v04 stills are the historical images inspected for the earlier review. They are separate from the latest working render.'
values={'__VERSION_BUTTONS__':buttons,'__ARCHIVE__':archive,'__DEFAULT_NOTE__':html.escape(default['note']),
 '__OTHER_VIEWS__':other,'__VERSIONS_JSON__':json.dumps(versions).replace('</','<\\/'),
 '__CURRENT_URL__':current_url,'__DEFAULT_URL__':default['url'],'__DEFAULT_CAMERA__':default['camera'],'__DEFAULT_CAPTION__':default['caption'],
 '__COMPARE_TITLE__':'Official aerial / '+default['label'],'__HISTORY_COUNT__':str(len(preserved_versions)),
 '__LATEST_VERSION__':args.latest_version.upper(),'__LATEST_NOTICE__':latest_notice,'__REVIEW_STATE__':review_state,
 '__CURRENT_DIMENSIONS__':str(default['size_px'][0])+' × '+str(default['size_px'][1]),
 '__VIEWS_HEADING__':('Inspected latest ' if args.reviewed_latest else 'Historical reviewed ')+reviewed_version.upper()+' saved views',
 '__VIEWS_INTRO__':views_intro,'__VIEWS_VERSION__':reviewed_version.upper(),'__OVERVIEW_URL__':views_url+'/campus_overview.png'}
page=TEMPLATE
for key,value in values.items():page=page.replace(key,value)
if re.search(r'__[A-Z_]+__',page):raise RuntimeError('Unfilled gallery template value')
(DEST/'index.html').write_text(page)
print('Built',DEST/'index.html')
print('Read',len(preserved_versions),'preserved iterations without modifying them;',args.latest_version,latest_status)
