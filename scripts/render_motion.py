"""Saved smooth exterior camera path; sample before final. Supports CPU Cycles and Eevee."""
import bpy,math,sys,argparse,json
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--sample',action='store_true');p.add_argument('--engine',choices=['cycles','eevee'],default='cycles');p.add_argument('--width',type=int,default=1920);p.add_argument('--samples',type=int,default=32);p.add_argument('--seconds',type=int,default=12);p.add_argument('--frame',type=int,default=0);p.add_argument('--start',type=int,default=1);p.add_argument('--end',type=int,default=0)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);root=Path(__file__).resolve().parents[1];s=bpy.context.scene
s.render.engine='CYCLES' if a.engine=='cycles' else 'BLENDER_EEVEE_NEXT'
if a.engine=='cycles':s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.04;s.cycles.use_animated_seed=False;s.cycles.seed=5540
else:s.eevee.taa_render_samples=a.samples;s.eevee.use_raytracing=True
s.render.resolution_x=a.width;s.render.resolution_y=round(a.width*9/16);s.render.resolution_percentage=100;s.render.fps=24
s.render.use_motion_blur=True;s.render.motion_blur_shutter=.35
s.frame_start=a.start;s.frame_end=a.end or (48 if a.sample else 24*a.seconds)
cam=bpy.data.objects['reference_aerial'];cam.animation_data_clear();cam.data.animation_data_clear();s.camera=cam
# Single continuous southeast arc, slow approach; no invented interior access.
keyframes=[]
for f in range(1,24*a.seconds+1):
 t=(f-1)/(24*a.seconds-1);u=t*t*(3-2*t);theta=math.radians(-56+43*u);radius=115-33*u;target=Vector((55,16,3.5));pos=Vector((55+radius*math.cos(theta),16+radius*math.sin(theta),29-20*u))
 cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.lens=32+4*u
 cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f);cam.data.keyframe_insert(data_path='lens',frame=f)
 if f in [1,48,24*a.seconds]:keyframes.append({'frame':f,'position':list(pos),'target':list(target),'lens':cam.data.lens})
for action in bpy.data.actions:
 for fc in action.fcurves:
  for kp in fc.keyframe_points:kp.interpolation='LINEAR'
out=root/'deliverables'/('motion-sample' if a.sample else 'cinematic');out.mkdir(parents=True,exist_ok=True)
(out/'path.json').write_text(json.dumps({'fps':24,'width':s.render.resolution_x,'height':s.render.resolution_y,'frames':s.frame_end,'keyframes':keyframes},indent=2))
s.render.image_settings.file_format='PNG';s.render.filepath=str(out/'frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'scene/protolabs-motion.blend'))
if a.frame:s.frame_set(a.frame);s.render.filepath=str(out/f'frame_{a.frame:04}.png');bpy.ops.render.render(write_still=True)
else:bpy.ops.render.render(animation=True)
