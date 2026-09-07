"""Saved smooth exterior camera path; sample before final. Supports CPU Cycles and Eevee."""
import bpy
import math
import sys
import argparse
import json
import hashlib
import subprocess
import time
import os
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'scripts'))
from frame_integrity import inspect_png

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--sample', action='store_true')
p.add_argument('--engine', choices=['cycles', 'eevee'], default='cycles')
p.add_argument('--width', type=int, default=1920)
p.add_argument('--samples', type=int, default=32)
p.add_argument('--seconds', type=int, default=12)
p.add_argument('--frame', type=int, default=0)
p.add_argument('--start', type=int, default=1)
p.add_argument('--end', type=int, default=0)
p.add_argument('--skip-existing', action='store_true', help='Resume only complete CRC-verified PNGs with the same master, settings and full camera path')
p.add_argument('--output-dir', type=Path, help='Optional frame/manifest directory; defaults to deliverables/motion-sample or deliverables/cinematic')
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
if a.seconds < 1 or a.samples < 1 or a.width < 2:
    p.error('--seconds and --samples must be positive; --width must be at least 2')
total_frames = 24 * a.seconds
end = a.end or (min(48, total_frames) if a.sample else total_frames)
if a.frame < 0 or a.frame > total_frames or not 1 <= a.start <= end <= total_frames:
    p.error('Frame selection must lie within the generated camera path')
s = bpy.context.scene
s.render.engine = 'CYCLES' if a.engine == 'cycles' else 'BLENDER_EEVEE_NEXT'
if a.engine == 'cycles':
    s.cycles.samples = a.samples
    s.cycles.use_denoising = True
    s.cycles.adaptive_threshold = .04
    s.cycles.use_animated_seed = False
    s.cycles.seed = 5540
else:
    s.eevee.taa_render_samples = a.samples
    s.eevee.use_raytracing = True
s.render.resolution_x = a.width
s.render.resolution_y = round(a.width * 9 / 16)
s.render.resolution_percentage = 100
s.render.fps = 24
s.render.use_persistent_data = True
s.render.use_motion_blur = True
s.render.motion_blur_shutter = .35
s.render.image_settings.file_format = 'PNG'
s.frame_start = a.start
s.frame_end = end
cam = bpy.data.objects['reference_aerial']
cam.animation_data_clear()
cam.data.animation_data_clear()
s.camera = cam
# Single continuous southeast arc, slow approach; no invented interior access.
# Preserve the camera equations and the fixed Cycles seed when resuming.
keyframes = []
path_frames = []
for f in range(1, total_frames + 1):
    t = (f - 1) / (total_frames - 1)
    u = t * t * (3 - 2 * t)
    theta = math.radians(-56 + 43 * u)
    radius = 115 - 33 * u
    target = Vector((55, 16, 3.5))
    pos = Vector((55 + radius * math.cos(theta), 16 + radius * math.sin(theta), 29 - 20 * u))
    cam.location = pos
    cam.rotation_euler = (target - pos).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 32 + 4 * u
    cam.keyframe_insert(data_path='location', frame=f)
    cam.keyframe_insert(data_path='rotation_euler', frame=f)
    cam.data.keyframe_insert(data_path='lens', frame=f)
    # Record the actual Blender property values of EVERY generated frame, not
    # just three display keyframes. Euler XYZ + location + scale fully specify
    # the generated local transform; parent/constraints are covered by master hash.
    path_frames.append({'frame': f, 'location': list(cam.location),
                        'rotation_euler': list(cam.rotation_euler),
                        'scale': list(cam.scale), 'lens_mm': float(cam.data.lens)})
    if f in (1, 48, total_frames):
        keyframes.append({'frame': f, 'position': list(pos), 'target': list(target), 'lens': cam.data.lens})
for action in bpy.data.actions:
    for fc in action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
path_payload = {'schema': 'blender_camera_local_properties_v1', 'camera': cam.name,
                'rotation_mode': cam.rotation_mode, 'interpolation': 'LINEAR', 'frames': path_frames}
path_hash = hashlib.sha256(json.dumps(path_payload, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
out = a.output_dir.expanduser().resolve() if a.output_dir else root / 'deliverables' / ('motion-sample' if a.sample else 'cinematic')
out.mkdir(parents=True, exist_ok=True)
try:
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
except (OSError, subprocess.CalledProcessError):
    revision = None
master = root / 'scene/protolabs-campus.blend'
metadata = {'fps': 24, 'fps_base': s.render.fps_base, 'width': s.render.resolution_x,
    'height': s.render.resolution_y, 'frames': s.frame_end,
    'render_start': a.frame or s.frame_start, 'render_end': a.frame or s.frame_end,
    'path_seconds': a.seconds, 'total_path_frames': total_frames, 'engine': a.engine,
    'samples': a.samples, 'motion_blur_shutter': .35, 'source_revision': revision,
    'master_sha256': hashlib.sha256(master.read_bytes()).hexdigest(), 'keyframes': keyframes,
    'camera_path_sha256': path_hash, 'camera_path_hash_schema': path_payload['schema'],
    'camera_path_frame_count': len(path_frames), 'blender_version': bpy.app.version_string,
    'sampling_seed': 5540 if a.engine == 'cycles' else None,
    'animated_seed': False if a.engine == 'cycles' else None,
    'denoising': True if a.engine == 'cycles' else None,
    'adaptive_threshold': .04 if a.engine == 'cycles' else None,
    'png_color_mode': s.render.image_settings.color_mode,
    'png_color_depth': s.render.image_settings.color_depth,
    'png_compression': s.render.image_settings.compression}
previous_path = out / 'path.json'
if a.skip_existing and any(out.glob('frame_*.png')):
    if not previous_path.exists():
        raise RuntimeError('Cannot resume frames without a matching path manifest')
    try:
        previous = json.loads(previous_path.read_text())
    except (OSError, ValueError) as error:
        raise RuntimeError('Cannot resume frames with an unreadable path manifest') from error
    if not isinstance(previous, dict):
        raise RuntimeError('Cannot resume frames with a non-object path manifest')
    for key in ('fps', 'fps_base', 'width', 'height', 'path_seconds', 'engine', 'samples',
                'motion_blur_shutter', 'master_sha256', 'camera_path_sha256',
                'camera_path_hash_schema', 'camera_path_frame_count', 'blender_version',
                'sampling_seed', 'animated_seed', 'denoising', 'adaptive_threshold',
                'png_color_mode', 'png_color_depth', 'png_compression'):
        if key not in previous or previous[key] != metadata[key]:
            raise RuntimeError('Cannot resume frames from different settings, master or camera path: ' + key)


def write_json_atomic(path, value):
    temporary = path.with_name(path.name + '.' + str(os.getpid()) + '.tmp')
    try:
        temporary.write_text(json.dumps(value, indent=2) + '\n')
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


write_json_atomic(previous_path, metadata)
rendered = []
skipped = []


def record_progress(scene):
    if scene.frame_current not in rendered: rendered.append(scene.frame_current)
    write_json_atomic(out / 'render-progress.json', {
        'frame': scene.frame_current, 'render_start': metadata['render_start'],
        'render_end': metadata['render_end'],
        'status': 'complete' if scene.frame_current >= metadata['render_end'] else 'rendering',
        'updated_unix': time.time(), 'master_sha256': metadata['master_sha256'],
        'camera_path_sha256': path_hash, 'rendered_this_run': rendered, 'skipped_this_run': skipped})


bpy.app.handlers.render_write.append(record_progress)
s.render.filepath = str(out / 'frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(root / 'scene/protolabs-motion.blend'))
try:
    if a.skip_existing:
        requested = [a.frame] if a.frame else range(s.frame_start, s.frame_end + 1)
        for frame_number in requested:
            dest = out / f'frame_{frame_number:04}.png'
            check = inspect_png(dest, (s.render.resolution_x, s.render.resolution_y)) if dest.exists() else None
            if check and check['valid']:
                print('RESUME_SKIP', frame_number, flush=True)
                skipped.append(frame_number)
                continue
            if check: print('RESUME_INVALID', frame_number, check['reason'], flush=True)
            s.frame_set(frame_number)
            s.render.filepath = str(dest)
            bpy.ops.render.render(write_still=True)
            completed = inspect_png(dest, (s.render.resolution_x, s.render.resolution_y))
            if not completed['valid']:
                raise RuntimeError('Rendered frame failed PNG integrity validation: ' + completed['reason'])
        write_json_atomic(out / 'render-progress.json', {
            'frame': metadata['render_end'], 'render_start': metadata['render_start'],
            'render_end': metadata['render_end'], 'status': 'complete',
            'updated_unix': time.time(), 'master_sha256': metadata['master_sha256'],
            'camera_path_sha256': path_hash, 'rendered_this_run': rendered, 'skipped_this_run': skipped})
    elif a.frame:
        s.frame_set(a.frame)
        s.render.filepath = str(out / f'frame_{a.frame:04}.png')
        bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)
finally:
    bpy.app.handlers.render_write.remove(record_progress)
