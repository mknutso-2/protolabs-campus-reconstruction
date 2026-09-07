"""Render saved master camera views. blender -b scene.blend -P scripts/render_views.py -- --views all"""
import bpy,sys,argparse,json,hashlib,datetime,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--views',default='all');p.add_argument('--width',type=int,default=1920);p.add_argument('--samples',type=int,default=96);p.add_argument('--out',default='deliverables/stills')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[1];out=root/a.out;out.mkdir(parents=True,exist_ok=True);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.025;s.render.resolution_x=a.width;s.render.resolution_y=round(a.width*2/3);s.render.resolution_percentage=100
cameras=json.loads((root/'scene/cameras.json').read_text());names=list(cameras) if a.views=='all' else a.views.split(',')
master_hash=hashlib.sha256((root/'scene/protolabs-campus.blend').read_bytes()).hexdigest()
for name in names:
 s.camera=bpy.data.objects[name];s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 receipt={'camera':name,'master_sha256':master_hash,'image_sha256':hashlib.sha256((out/(name+'.png')).read_bytes()).hexdigest(),'width':s.render.resolution_x,'height':s.render.resolution_y,'samples':a.samples,'blender_version':bpy.app.version_string,'rendered_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'camera_matrix_world':[list(row) for row in s.camera.matrix_world],'lens_mm':s.camera.data.lens,'inspection':'pending'}
 tmp=out/(name+'.json.tmp');tmp.write_text(json.dumps(receipt,indent=2)+'\n');os.replace(tmp,out/(name+'.json'))
