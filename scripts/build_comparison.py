#!/usr/bin/env python3
"""Build the self-contained offline comparison page from local deliverables.

Run: python3 scripts/build_comparison.py
First run preserves current aerial/cameras as v04. Later runs keep that snapshot.
Use --refresh-v04 deliberately to replace v04 with a newer current render.
No external libraries, network requests, image alterations, or build tooling.
"""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import html
import json
import shutil
import struct

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'deliverables/comparison'

def png_size(path):
    with path.open('rb') as f:
        head=f.read(24)
    if head[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected PNG: '+str(path))
    return list(struct.unpack('>II',head[16:24]))

def record(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'size_bytes':path.stat().st_size, 'size_px':png_size(path),
            'file_modified_utc':dt.datetime.fromtimestamp(path.stat().st_mtime,dt.timezone.utc).isoformat()}

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--refresh-v04',action='store_true')
args=parser.parse_args()
current=ROOT/'deliverables/reference_aerial.png'
if not current.exists(): raise SystemExit('Missing current aerial: '+str(current))
v04=ROOT/'deliverables/iterations/v04'
v04.mkdir(parents=True,exist_ok=True)
if args.refresh_v04 or not (v04/'reference_aerial.png').exists():
    shutil.copy2(current,v04/'reference_aerial.png')
    shutil.copy2(ROOT/'scene/cameras.json',v04/'cameras.json')
    (v04/'stills').mkdir(exist_ok=True)
    for still in (ROOT/'deliverables/stills').glob('*.png'):
        shutil.copy2(still,v04/'stills'/still.name)
    (v04/'snapshot.json').write_text(json.dumps({'note':'Preserved current v04 aerial and contemporaneous saved cameras; images are unaltered.',
        'aerial':record(v04/'reference_aerial.png'),'source_current':record(current)},indent=2)+'\n')
fit=json.loads((ROOT/'research/reference_drone_camera_fit.json').read_text())
versions=[]
notes={
 'v01':'Early massing and initial daylight image. Roof extent, grading artifacts and facade treatment visibly differ from the photograph.',
 'v02':'Landscape and material iteration. Sparse tree crowns, window recesses and entrance roof treatment remain conspicuous.',
 'v03':'Revised framing and generic parked vehicles. Sparse foliage and dark glazing are still visible.',
 'v04':'Preserved reviewed iteration. Fitted aerial camera, dense procedural crowns, revised glazing and entrance roof treatment. Photographic realism remains incomplete.'}
for version in ('v01','v02','v03','v04'):
    path=ROOT/f'deliverables/iterations/{version}/reference_aerial.png'
    if not path.exists(): raise SystemExit('Missing required preserved iteration: '+str(path))
    versions.append({'id':version,'label':version.upper(), 'url':f'../iterations/{version}/reference_aerial.png',
                     'camera':f'../iterations/{version}/cameras.json','note':notes[version],**record(path)})
preserved_versions=list(versions)
current_is_new=record(current)['sha256']!=record(v04/'reference_aerial.png')['sha256']
if current_is_new:
    versions.append({'id':'v05','label':'V05 · latest','url':'../reference_aerial.png',
        'camera':'../../scene/cameras.json','note':'Latest working v05 image. Pending full-image review; the assessment and comparison stills below document preserved v04. Do not infer that v05 has passed fidelity or motion checks.',**record(current)})
default=versions[-1]
source='../../research/images/protolabs-official-hq-drone.jpg'
manifest={'gallery_kind':'Offline visual comparison; not the interactive 3D viewer',
          'source_reference':'research/images/protolabs-official-hq-drone.jpg',
          'review_date':'2026-09-07','reviewed_iteration':'v04','current_pending_review':current_is_new,'current_aerial':record(current),'iterations':versions,
          'camera_fit':{'weighted_rms_px':fit['rms_pixel_weighted'],'unweighted_rmse_px':fit['rmse_pixel_unweighted'],
                        'landmarks':len(fit['landmarks']),'source_size_px':fit['reference_size'],
                        'note':'Residuals describe selected manually annotated landmarks, not whole-image fidelity or metric survey accuracy.'}}
DEST.mkdir(parents=True,exist_ok=True)
(DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

TEMPLATE=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Protolabs · Evidence & iteration</title>
<style>
:root{--ink:#152a36;--muted:#5f6f78;--line:#d8e0e3;--paper:#f4f6f5;--blue:#087aa1;--white:#fff;--accent:#daf0f4}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:var(--blue);text-underline-offset:3px}a:hover{color:#034d68}button,input{font:inherit}button,a{touch-action:manipulation}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #d79522;outline-offset:3px}header{background:#142b38;color:#f7fbfc;padding:42px max(24px,calc((100vw - 1320px)/2)) 35px}header p{max-width:860px;margin:.6rem 0;color:#cbdde5}.eyebrow{font-size:12px;font-weight:750;letter-spacing:.17em;text-transform:uppercase}.eyebrow span{color:#6bd3e9}h1{font-size:clamp(30px,4vw,49px);line-height:1.12;letter-spacing:-.035em;margin:14px 0}nav{display:flex;gap:22px;flex-wrap:wrap;margin-top:24px}nav a{color:#bce7f1;font-size:14px}main{max-width:1370px;margin:auto;padding:32px 25px 65px}h2{font-size:25px;line-height:1.25;letter-spacing:-.025em;margin:0 0 9px}h3{font-size:18px;margin:0 0 6px}p{margin:.4em 0 .9em}section{margin-bottom:42px}.lead{color:var(--muted);max-width:1020px}.notice{border-left:4px solid var(--blue);padding:15px 20px;background:#e5f0f2;margin:0 0 28px}.notice p{margin:0}.tools{display:flex;justify-content:space-between;gap:16px;align-items:center;flex-wrap:wrap;margin:20px 0 12px}.segmented{display:flex;gap:3px;background:#e0e7e9;padding:4px;border-radius:7px}.segmented button{border:0;border-radius:4px;background:transparent;color:var(--ink);padding:9px 16px;cursor:pointer;font-size:14px}.segmented button[aria-pressed="true"]{background:var(--white);box-shadow:0 1px 3px #1232;color:#045f80;font-weight:750}.frames{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0;min-width:0;background:var(--white);border:1px solid var(--line);border-radius:7px;overflow:hidden}figure img{display:block;width:100%;height:auto}figcaption{font-size:13px;color:var(--muted);padding:12px 15px}figcaption strong{display:block;color:var(--ink);font-size:14px;margin-bottom:3px}.caption-links{display:flex;gap:18px;flex-wrap:wrap;margin:12px 0;color:var(--muted);font-size:13px}.version-note{font-size:14px;color:var(--muted);min-height:2em}.wipe{position:relative;aspect-ratio:3/2;background:#d9e2e5;border-radius:7px;overflow:hidden;border:1px solid var(--line)}.wipe img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.wipe .top{clip-path:inset(0 0 0 50%)}.divider{position:absolute;top:0;bottom:0;left:50%;border-left:2px solid #fff;filter:drop-shadow(0 1px 3px #0008);pointer-events:none}.divider:after{content:'↔';position:absolute;top:48%;left:-20px;width:38px;height:38px;background:white;color:#12333f;border-radius:50%;text-align:center;font-size:24px;line-height:34px}.wipe-tag{position:absolute;top:14px;padding:5px 9px;background:#102c3dd9;color:#fff;border-radius:4px;font-size:12px;z-index:3}.wipe-tag.left{left:14px}.wipe-tag.right{right:14px}.range-label{display:flex;align-items:center;gap:18px;margin:12px 0;color:var(--muted);font-size:13px}.range-label input{flex:1;accent-color:var(--blue)}[hidden]{display:none!important}.archive{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.archive img{aspect-ratio:3/2;object-fit:contain;background:#dce2e1}.archive figcaption{min-height:145px}.archive a.image-link{display:block}.badge{display:inline-block;background:var(--accent);color:#075e77;border-radius:4px;padding:3px 7px;font-size:11px;font-weight:700;vertical-align:middle;margin-left:5px}.review-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}.review-box{background:white;border:1px solid var(--line);border-radius:7px;padding:23px}.review-box ul,.review-box ol{padding-left:20px;margin:12px 0 0}.review-box li{margin:0 0 10px}.review-box li:last-child{margin:0}.mini{font-size:13px;color:var(--muted)}.pair{margin-top:25px}.pair .frames figure img{aspect-ratio:3/2;object-fit:contain;background:#dce2e1}.wide-image{max-width:100%;display:block;border-radius:7px;border:1px solid var(--line)}details{background:white;border:1px solid var(--line);border-radius:7px;padding:15px 20px;margin:15px 0}summary{font-weight:650;cursor:pointer}details p{margin:15px 0 5px}.source-list{display:grid;grid-template-columns:1fr 1fr;gap:18px}.source{border-top:1px solid var(--line);padding:16px 0 0}.source p{font-size:14px;color:var(--muted)}footer{border-top:1px solid var(--line);padding-top:22px;color:var(--muted);font-size:13px}.metric{font-variant-numeric:tabular-nums;font-weight:750;color:var(--ink)}@media(max-width:900px){.archive{grid-template-columns:1fr 1fr}.frames,.review-grid,.source-list{grid-template-columns:1fr}.tools{align-items:flex-start}.archive figcaption{min-height:0}header{padding:32px 25px}.frames figure img{max-height:none}.segmented button{padding:9px 12px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{header{background:white;color:black;padding:0}header p,nav a{color:#333}main{padding:18px 0}.tools,.range-label,nav{display:none}.archive{grid-template-columns:1fr 1fr}.review-grid{grid-template-columns:1fr}figure,section{break-inside:avoid}.wipe-wrap{display:none!important}.frames{display:grid!important}a{color:inherit}}
</style></head><body>
<header><div class="eyebrow">Protolabs / Maple Plain <span>· Evidence & iteration</span></div>
<h1>A reconstruction, beside its evidence.</h1>
<p>5540 Pioneer Creek Drive, Minnesota. Four preserved aerial iterations, the photographs that informed them, and the visible limits of the current model.</p>
<nav aria-label="Page sections"><a href="#compare">Compare</a><a href="#iterations">Four iterations</a><a href="#review">Visual review</a><a href="#other-views">Other saved views</a><a href="#sources">Sources & dates</a></nav></header>
<main>
<div class="notice"><p><strong>Reviewed v04 assessment:</strong> the headquarters is recognizable through its roof, facade composition and entrance structure. The render remains a schematic architectural visualization; it has not reached photographic equivalence.</p></div>
<section id="compare"><h2>__COMPARE_TITLE__</h2><p class="lead">The aerial camera was fitted to selected roof, flagpole and facade landmarks. Materials, lighting, planting and parking still differ visibly. The wipe is an inspection aid; it is not a whole-image accuracy score.</p>
<div class="tools"><div class="segmented" aria-label="Choose reconstruction iteration">__VERSION_BUTTONS__</div><div class="segmented" aria-label="Comparison display"><button id="sideButton" type="button" aria-pressed="true">Side by side</button><button id="wipeButton" type="button" aria-pressed="false">Image wipe</button></div></div>
<div id="sideFrames" class="frames"><figure><img src="../../research/images/protolabs-official-hq-drone.jpg" alt="Official Protolabs headquarters aerial at sunset, showing the brick left block, sloping silver entrance roof and white glazed right wing"><figcaption><strong>Photographic reference · Proto Labs, Inc.</strong>Undated official aerial. Same photographic setup as the official file named “2024”; exact capture date is unverified.</figcaption></figure><figure><img id="renderSide" src="__DEFAULT_URL__" alt="Selected reconstruction rendered from the saved aerial camera"><figcaption><strong id="renderCaption">__DEFAULT_CAPTION__</strong>Daylight interpretation; source photo is at sunset. The image is shown without retouching.</figcaption></figure></div>
<div id="wipeWrap" class="wipe-wrap" hidden><div class="wipe"><img src="../../research/images/protolabs-official-hq-drone.jpg" alt="Official headquarters photographic reference"><img id="renderWipe" class="top" src="__DEFAULT_URL__" alt="Reconstruction overlay"><span class="wipe-tag left">Photograph</span><span id="wipeTag" class="wipe-tag right">__DEFAULT_CAPTION__</span><span id="divider" class="divider"></span></div><label class="range-label" for="wipeRange">Photograph ←<input id="wipeRange" type="range" min="0" max="100" value="50" aria-label="Move the boundary between photograph and reconstruction">→ Reconstruction</label></div>
<div class="caption-links"><a href="../../research/images/protolabs-official-hq-drone.jpg" target="_blank" rel="noopener">Open full reference</a><a id="fullRender" href="__DEFAULT_URL__" target="_blank" rel="noopener">Open full reconstruction</a><a id="cameraLink" href="__DEFAULT_CAMERA__">Saved camera data</a><a href="../reference_aerial.png" target="_blank" rel="noopener">Latest working aerial</a></div><p id="versionNote" class="version-note">__V04_NOTE__</p>
<details><summary>What does the camera fit establish?</summary><p>Eleven manually annotated landmarks were fitted to 3D correspondences. On the 1200 × 800 source, the recorded weighted RMS is <span class="metric">3.17 px</span>; the unweighted RMSE is <span class="metric">7.87 px</span>. One partly obscured roof correspondence is about 20 px away. These residuals apply only to the selected points, depend on their manual annotation and weights, and do not certify whole-building dimensions or photographic fidelity. <a href="../../research/reference_drone_camera_fit.json">Inspect the complete fit.</a></p><p class="mini">The v04 render is 1600 × 1067, close to the source aspect ratio. Scaling within this page does not refit either camera. Earlier iterations deliberately retain their earlier cameras.</p></details></section>
<section id="iterations"><h2>Four iterations, kept intact.</h2><p class="lead">Each card opens its original image. The latest working v05 is shown separately when its image differs from v04 and is pending review. v01–v03 and their camera records are preserved; v04 snapshots the current aerial at gallery generation. Later changes to the working image do not silently replace these snapshots.</p><div class="archive">__ARCHIVE__</div></section>
<section id="review"><h2>What matches, and what remains visible.</h2><div class="review-grid"><div class="review-box"><h3>Recognizable features</h3><ul><li>The broad low-rise composition: a darker left block, white right wing and central sloping silver roof.</li><li>The projecting white entrance truss, fan braces, dark cylindrical supports and glass vestibule.</li><li>The left facade’s repeated narrow windows and the right wing’s continuous glazed band.</li><li>The flagpole island, monument sign, parking surfaces and planted edges establish the arrival setting.</li><li>The fitted aerial brings several important silhouette landmarks into approximate image alignment.</li></ul></div><div class="review-box"><h3>Largest remaining discrepancies</h3><ol><li><strong>Material and light response.</strong> Brick, pavement, roofing and painted panels are too uniform and clean. Daylight exposure differs strongly from the sunset photograph.</li><li><strong>Glazing and entrance detail.</strong> Repeated blue panes lack the reference’s varied reflections; exact mullion, door, column and truss proportions remain inferred.</li><li><strong>Landscape.</strong> Dense crowns improve v04, but generic leaf cards and repeated forms differ from the photographed mature canopy, understory and distant wooded horizon.</li><li><strong>Parking and ground treatment.</strong> Stripe spacing, island edges and accessible markings are approximate. The repeated generic vehicles and occupancy differ from the reference’s empty lot.</li><li><strong>Small details and unseen areas.</strong> Signs, flag, hydrant, curb profiles and rooftop equipment are simplified. Rear elevations and hidden equipment are not verified by these frontage photographs.</li></ol></div></div><p class="mini" style="margin-top:15px">Review date: 7 September 2026. This is a visual assessment of the preserved v04 aerial and current entrance, arrival and campus-overview stills, not an engineering survey. <a href="../../docs/visual-accuracy.md">Read the full accuracy record and missing quality milestones.</a></p></section>
<section id="other-views"><h2>Reviewed v04 saved views</h2><p class="lead">These preserved v04 stills are the images inspected for this review. Their cameras are intentionally labelled approximate. A related photograph is context, not proof that the two views are registered. Historic branding and seasonal conditions also differ.</p>
__OTHER_VIEWS__
<div class="pair"><h3>Campus overview <span class="badge">Approximate oblique overview</span></h3><p class="mini">Useful for footprint, parking and landscape context. It is not aligned to the county’s top-down aerial, and the vegetation and vehicles are an inferred presentation state.</p><a href="../iterations/v04/stills/campus_overview.png" target="_blank" rel="noopener"><img class="wide-image" src="../iterations/v04/stills/campus_overview.png" alt="Reviewed v04 high oblique campus overview reconstruction" loading="lazy"></a></div></section>
<section id="sources"><h2>Sources, attribution and capture dates</h2><p class="lead">The page and its images open offline. The following links lead to the original publishers when an internet connection is available. Reference photographs remain attributed to their owners; public access is not a redistribution license.</p><div class="source-list">
<div class="source"><h3>Official headquarters aerials</h3><p>Proto Labs, Inc. The wide drone image is undated. The current locations-page filename includes “2024”; that does not independently establish the capture date. Retrieved 7 September 2026.</p><a href="https://www.protolabs.com/media/s4dignhf/hq-drone.jpg">Wide drone image</a> · <a href="https://www.protolabs.com/media/sj0nwkxv/hq_mp_exterior_2024.jpg">Official “2024” image</a> · <a href="https://www.protolabs.com/about-us/locations/">Location directory</a></div>
<div class="source"><h3>Entrance close-up</h3><p>Minneapolis / St. Paul Business Journal, article dated 6 December 2018; exact photograph date and photographer were not independently verified. Historic green/blue lettering differs from the current interpretation.</p><a href="https://www.bizjournals.com/twincities/news/2018/12/06/2018-business-of-manufacturing-proto-labs-inc.html">Original article</a></div>
<div class="source"><h3>Ground-level arrival</h3><p>Machine Design, image credited to Protolabs; article dated 26 January 2024. The photograph’s capture date is unknown. Snow and dormant planting document a different season from the render.</p><a href="https://www.machinedesign.com/automation-iiot/article/21281562/protolabs-qa-protolabs-rebranded-manufacturing-partner-network-expands-capabilities">Original article</a></div>
<div class="source"><h3>Geospatial and asset provenance</h3><p>Hennepin County imagery and public lidar constrain the site independently of the photograph. Visual traces, dates and measurement limits are retained in the ledger. Vegetation and vehicles are original generic procedural assets.</p><a href="../../research/geospatial-sources.json">Geospatial sources</a> · <a href="../../research/architecture-sources.json">Architecture ledger</a> · <a href="../../docs/vegetation-provenance.md">Vegetation provenance</a> · <a href="../../docs/vehicles-provenance.md">Vehicle provenance</a></div></div></section>
<footer>This gallery is separate from the 3D viewer. No network fetches, external fonts or external scripts are required. Rebuild with <code>python3 scripts/build_comparison.py</code>. <a href="manifest.json">Image hashes, dimensions and snapshot manifest</a>.</footer>
</main><script>
'use strict';
const versions=__VERSIONS_JSON__;
const q=id=>document.getElementById(id);
for(const button of document.querySelectorAll('[data-version]')) button.addEventListener('click',()=>{
 const v=versions.find(item=>item.id===button.dataset.version);
 for(const b of document.querySelectorAll('[data-version]')) b.setAttribute('aria-pressed',String(b===button));
 q('renderSide').src=v.url;q('renderWipe').src=v.url;q('renderSide').alt=v.label+' preserved reconstruction iteration';q('fullRender').href=v.url;q('cameraLink').href=v.camera;
 q('renderCaption').textContent=v.label+(v.id==='v05'?' · pending review':(v.id==='v04'?' · preserved v04 reconstruction':' · preserved iteration'));q('wipeTag').textContent=v.label+' reconstruction';q('versionNote').textContent=v.note;
});
function mode(wipe){q('sideFrames').hidden=wipe;q('wipeWrap').hidden=!wipe;q('sideButton').setAttribute('aria-pressed',String(!wipe));q('wipeButton').setAttribute('aria-pressed',String(wipe));}
q('sideButton').addEventListener('click',()=>mode(false));q('wipeButton').addEventListener('click',()=>mode(true));
q('wipeRange').addEventListener('input',event=>{const v=event.target.value;q('renderWipe').style.clipPath='inset(0 0 0 '+v+'%)';q('divider').style.left=v+'%';});
</script></body></html>'''

buttons=''.join(f'<button type="button" data-version="{v["id"]}" aria-pressed="{str(v["id"]==default["id"]).lower()}">{v["label"]}</button>' for v in versions)
if not current_is_new:
    buttons+='<button type="button" disabled title="Awaiting a new current render">V05 · pending</button>'
archive=''.join(f'<figure><a class="image-link" href="{v["url"]}" target="_blank" rel="noopener"><img src="{v["url"]}" alt="Preserved {v["id"]} aerial reconstruction" loading="lazy"></a><figcaption><strong>{v["label"]}'+(' <span class="badge">Reviewed snapshot</span>' if v['id']=='v04' else '')+f'</strong>{html.escape(v["note"])}<br><a href="{v["camera"]}">Camera record</a> · {v["size_px"][0]} × {v["size_px"][1]}</figcaption></figure>' for v in preserved_versions)
pairs=[('Entrance detail','entrance_detail','businessjournal-entrance-2018.jpg','Historic entrance photograph · published 2018','White fan braces, cylindrical supports, sloping roof and vestibule provide the structural reference. Precise framing and dimensions are not established by the approximate saved camera.'),
       ('Arrival','arrival','machine-design-frontage-2024.png','Protolabs image in Machine Design · published 2024','The reference has winter planting and snow; the current render uses a leaf-on daylight setting, different occupancy and an approximate arrival camera.')]
other=''
for title,name,ref,label,note in pairs:
    if not (ROOT/f'deliverables/stills/{name}.png').exists():
        other+=f'<p>{title}: current still not available at generation.</p>'
        continue
    other+=f'<div class="pair"><h3>{title} <span class="badge">Approximate camera</span></h3><p class="mini">{note}</p><div class="frames"><figure><a href="../../research/images/{ref}" target="_blank" rel="noopener"><img src="../../research/images/{ref}" alt="{label}" loading="lazy"></a><figcaption><strong>{label}</strong>Exact capture date unverified.</figcaption></figure><figure><a href="../iterations/v04/stills/{name}.png" target="_blank" rel="noopener"><img src="../iterations/v04/stills/{name}.png" alt="Reviewed v04 {title.lower()} reconstruction still" loading="lazy"></a><figcaption><strong>Reviewed v04 {title.lower()} still</strong>Approximate saved view; not photographically registered. <a href="../stills/{name}.png">Latest working still (separate from this review)</a></figcaption></figure></div></div>'
page=TEMPLATE.replace('__VERSION_BUTTONS__',buttons).replace('__ARCHIVE__',archive).replace('__V04_NOTE__',html.escape(default['note'])).replace('__OTHER_VIEWS__',other).replace('__VERSIONS_JSON__',json.dumps(versions).replace('</','<\\/'))
page=page.replace('__DEFAULT_URL__',default['url']).replace('__DEFAULT_CAMERA__',default['camera']).replace('__DEFAULT_CAPTION__',default['label']+' reconstruction').replace('__COMPARE_TITLE__','Official aerial / '+default['label'])
(DEST/'index.html').write_text(page)
print('Built',DEST/'index.html')
print('Preserved',len(preserved_versions),'iterations; latest v05 present:',current_is_new)
