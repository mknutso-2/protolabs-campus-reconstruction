"""Prepare locally cached references, Blender glTF and stills for browser preview."""
from pathlib import Path
import shutil,json,subprocess
from PIL import Image
root=Path(__file__).resolve().parents[1];pub=root/'viewer/public'
for n in ['renders','models','references']:(pub/n).mkdir(parents=True,exist_ok=True)
for src,dst in [('scene/cameras.json','models/cameras.json'),('scene/materials.json','models/materials.json'),('research/terrain_grid.json','models/terrain.json')]:shutil.copyfile(root/src,pub/dst)
cameras=json.loads((root/'scene/cameras.json').read_text())
for name in cameras:
 src=root/'deliverables/stills'/f'{name}.png'
 if not src.exists():src=root/'deliverables'/f'{name}.png'
 if src.exists():Image.open(src).convert('RGB').save(pub/'renders'/f'{name}.jpg',quality=94)
 else:print('Still pending:',name)
refs={'protolabs-official-hq-drone.jpg':'hq.jpg','businessjournal-entrance-2018.jpg':'entrance.jpg','machine-design-frontage-2024.png':'arrival.png'}
for src,dst in refs.items():
 path=root/'research/images'/src
 if path.exists():shutil.copyfile(path,pub/'references'/dst)
 else:print('Reference pending:',src)
film=root/'deliverables/flythrough.mp4'
if film.exists():shutil.copyfile(film,pub/'renders/flythrough.mp4')

subprocess.run(['npx','gltf-transform','optimize','../scene/protolabs-campus.glb','public/models/campus.glb','--compress','meshopt','--simplify','false','--palette','false','--texture-compress','false'],cwd=root/'viewer',check=True)
