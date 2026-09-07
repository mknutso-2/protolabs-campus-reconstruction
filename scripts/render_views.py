"""Render saved master camera views. blender -b scene.blend -P scripts/render_views.py -- --views all"""
import bpy,sys,argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--views',default='all');p.add_argument('--width',type=int,default=1920);p.add_argument('--samples',type=int,default=96);p.add_argument('--out',default='deliverables/stills')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[1];out=root/a.out;out.mkdir(parents=True,exist_ok=True);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.025;s.render.resolution_x=a.width;s.render.resolution_y=round(a.width*2/3);s.render.resolution_percentage=100
cameras=json.loads((root/'scene/cameras.json').read_text());names=list(cameras) if a.views=='all' else a.views.split(',')
for name in names:
 s.camera=bpy.data.objects[name];s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
