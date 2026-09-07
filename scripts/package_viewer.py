"""Prepare locally cached references, Blender glTF and stills for browser preview."""
from pathlib import Path
import shutil,json,subprocess,hashlib,argparse,tempfile
from PIL import Image
from prepare_viewer_materials import prepare_viewer_materials,verify_optimized_materials
root=Path(__file__).resolve().parents[1];pub=root/'viewer/public'
p=argparse.ArgumentParser();p.add_argument('--require-film',action='store_true');args=p.parse_args()
master_hash=hashlib.sha256((root/'scene/protolabs-campus.blend').read_bytes()).hexdigest()
metadata=json.loads((root/'scene/viewer-export.json').read_text())
if metadata['master_sha256']!=master_hash:raise RuntimeError('Browser export is stale. Run scripts/export_viewer.py with the current master.')
if metadata.get('viewer_glb_sha256')!=hashlib.sha256((root/'scene/protolabs-campus-viewer.glb').read_bytes()).hexdigest():raise RuntimeError('Browser GLB differs from its export receipt.')
cameras=json.loads((root/'scene/cameras.json').read_text())
for name in cameras:
 src=root/'deliverables/stills'/f'{name}.png';receipt=json.loads(src.with_suffix('.json').read_text())
 if receipt['master_sha256']!=master_hash or receipt['image_sha256']!=hashlib.sha256(src.read_bytes()).hexdigest():raise RuntimeError(f'Stale fixed-view render: {name}')
film=root/'deliverables/flythrough.mp4'
if args.require_film and not film.is_file():raise RuntimeError('Final viewer requires the encoded flythrough')
for n in ['renders','models','references']:(pub/n).mkdir(parents=True,exist_ok=True)
for src,dst in [('scene/cameras.json','models/cameras.json'),('scene/materials.json','models/materials.json'),('research/terrain_grid.json','models/terrain.json')]:shutil.copyfile(root/src,pub/dst)
for name in cameras:
 src=root/'deliverables/stills'/f'{name}.png'
 Image.open(src).convert('RGB').save(pub/'renders'/f'{name}.jpg',quality=94)
refs={'protolabs-official-hq-drone.jpg':'hq.jpg','businessjournal-entrance-2018.jpg':'entrance.jpg','machine-design-frontage-2024.png':'arrival.png'}
for src,dst in refs.items():
 path=root/'research/images'/src
 if path.exists():shutil.copyfile(path,pub/'references'/dst)
 else:print('Reference pending:',src)
film=root/'deliverables/flythrough.mp4'
if film.exists():shutil.copyfile(film,pub/'renders/flythrough.mp4')
else:(pub/'renders/flythrough.mp4').unlink(missing_ok=True)

with tempfile.TemporaryDirectory(prefix='campus-viewer-materials-') as temporary:
 prepared=Path(temporary)/'campus-materials.glb'
 joined=Path(temporary)/'campus-joined.glb'
 report=prepare_viewer_materials(root/'scene/protolabs-campus-viewer.glb',root/'scene/materials.json',prepared)
 subprocess.run(['npx','gltf-transform','optimize',str(prepared),str(joined),'--compress','false','--simplify','false','--palette','false','--texture-compress','false'],cwd=root/'viewer',check=True)
 compression=subprocess.run(['node',str(root/'scripts/compress_viewer_lossless.mjs'),str(joined),str(pub/'models/campus.glb')],cwd=root/'viewer',check=True,capture_output=True,text=True)
 report['position_compression']=json.loads(compression.stdout.strip().splitlines()[-1])
 report.update(verify_optimized_materials(pub/'models/campus.glb',report))
 report['master_sha256']=master_hash
 (root/'scene/viewer-package.json').write_text(json.dumps(report,indent=2)+'\n')
