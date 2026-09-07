"""Saved smooth exterior camera path; sample before final. Supports CPU Cycles and Eevee."""
import bpy,math,sys,argparse,json,hashlib,subprocess,struct,time
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--sample',action='store_true');p.add_argument('--engine',choices=['cycles','eevee'],default='cycles');p.add_argument('--width',type=int,default=1920);p.add_argument('--samples',type=int,default=32);p.add_argument('--seconds',type=int,default=12);p.add_argument('--frame',type=int,default=0);p.add_argument('--start',type=int,default=1);p.add_argument('--end',type=int,default=0);p.add_argument('--skip-existing',action='store_true',help='Resume valid completed PNG frames without overwriting them')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);root=Path(__file__).resolve().parents[1];s=bpy.context.scene
s.render.engine='CYCLES' if a.engine=='cycles' else 'BLENDER_EEVEE_NEXT'
if a.engine=='cycles':s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.04;s.cycles.use_animated_seed=False;s.cycles.seed=5540
else:s.eevee.taa_render_samples=a.samples;s.eevee.use_raytracing=True
s.render.resolution_x=a.width;s.render.resolution_y=round(a.width*9/16);s.render.resolution_percentage=100;s.render.fps=24
s.render.use_persistent_data=True;s.render.use_motion_blur=True;s.render.motion_blur_shutter=.35
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
try:revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
except (OSError,subprocess.CalledProcessError):revision=None
master=root/'scene/protolabs-campus.blend'
metadata={'fps':24,'width':s.render.resolution_x,'height':s.render.resolution_y,'frames':s.frame_end,'render_start':a.frame or s.frame_start,'render_end':a.frame or s.frame_end,'path_seconds':a.seconds,'total_path_frames':24*a.seconds,'engine':a.engine,'samples':a.samples,'motion_blur_shutter':.35,'source_revision':revision,'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'keyframes':keyframes}
previous_path=out/'path.json'
if a.skip_existing and any(out.glob('frame_*.png')):
 if not previous_path.exists():raise RuntimeError('Cannot resume frames without a matching path manifest')
 previous=json.loads(previous_path.read_text())
 for key in ['fps','width','height','path_seconds','engine','samples','motion_blur_shutter','master_sha256']:
  if previous.get(key)!=metadata[key]:raise RuntimeError('Cannot resume frames from different settings or master: '+key)
previous_path.write_text(json.dumps(metadata,indent=2))
def record_progress(scene):
 (out/'render-progress.json').write_text(json.dumps({'frame':scene.frame_current,'render_start':metadata['render_start'],'render_end':metadata['render_end'],'status':'complete' if scene.frame_current>=metadata['render_end'] else 'rendering','updated_unix':time.time(),'master_sha256':metadata['master_sha256']},indent=2))
bpy.app.handlers.render_write.append(record_progress)

s.render.image_settings.file_format='PNG';s.render.filepath=str(out/'frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'scene/protolabs-motion.blend'))
if a.frame:s.frame_set(a.frame);s.render.filepath=str(out/f'frame_{a.frame:04}.png');bpy.ops.render.render(write_still=True)
elif a.skip_existing:
 for frame_number in range(s.frame_start,s.frame_end+1):
  dest=out/f'frame_{frame_number:04}.png';valid=False
  if dest.exists():
   data=dest.read_bytes()
   valid=len(data)>32 and data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(s.render.resolution_x,s.render.resolution_y) and data[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82'
  if valid:print('RESUME_SKIP',frame_number,flush=True);continue
  s.frame_set(frame_number);s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
else:bpy.ops.render.render(animation=True)
