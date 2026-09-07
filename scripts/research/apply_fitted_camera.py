"""Run inside Blender after creating scene, passing fit JSON path."""
import bpy,json,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
j=json.loads(Path(args[0] if args else 'reference_drone_camera_fit.json').read_text())
cam=bpy.data.objects.get('ReferenceDroneMatched')
if cam is None:
 data=bpy.data.cameras.new('ReferenceDroneMatched');cam=bpy.data.objects.new('ReferenceDroneMatched',data);bpy.context.collection.objects.link(cam)
cam.location=j['position'];cam.rotation_mode='XYZ';cam.rotation_euler=j['rotation_euler_xyz_radians'];cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=j['sensor_width_mm'];cam.data.lens=j['lens_mm'];cam.data.shift_x=j['shift_x'];cam.data.shift_y=j['shift_y']
bpy.context.scene.camera=cam;bpy.context.scene.render.resolution_x=j['reference_size'][0];bpy.context.scene.render.resolution_y=j['reference_size'][1];bpy.context.scene.render.resolution_percentage=100
print('Applied fitted reference camera; no scene model transforms changed')
