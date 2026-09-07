"""Export a lighter browser GLB while preserving the editable master and rendered foliage.
Invoke through Blender with the master already open. Never saves changes to the master.
"""
import bpy, random, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def reduced_leaves(data, fraction=.30):
    rng=random.Random(5540)
    decisions={}
    kept=[]
    for face in data.polygons:
        if face.material_index==0:
            kept.append(face);continue
        # Each original leaf is a pair of triangles sharing its first vertex.
        key=min(face.vertices)
        if key not in decisions:decisions[key]=rng.random()<fraction
        if decisions[key]:kept.append(face)
    ids=sorted({v for face in kept for v in face.vertices});mapping={old:new for new,old in enumerate(ids)}
    lod=bpy.data.meshes.new(data.name+' browser foliage')
    lod.from_pydata([data.vertices[i].co for i in ids],[],[tuple(mapping[i] for i in f.vertices) for f in kept]);lod.update()
    for m in data.materials:lod.materials.append(m)
    for dst,src in zip(lod.polygons,kept):dst.material_index=src.material_index;dst.use_smooth=src.use_smooth
    for uv in data.uv_layers:
        target=lod.uv_layers.new(name=uv.name)
        for dst,src in zip(lod.polygons,kept):
            for dl,sl in zip(dst.loop_indices,src.loop_indices):target.data[dl].uv=uv.data[sl].uv
    return lod

originals={};lods={};before=after=0
try:
    for obj in bpy.data.objects:
        if obj.type!='MESH' or not any(m and m.name.startswith('CampusVeg_') for m in obj.data.materials):continue
        data=obj.data
        if data.name not in lods:lods[data.name]=reduced_leaves(data)
        if not obj.hide_render:
            before+=sum(len(f.vertices)-2 for f in data.polygons)
            after+=sum(len(f.vertices)-2 for f in lods[data.name].polygons)
        originals[obj.name]=data;obj.data=lods[data.name]
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'scene/protolabs-campus-viewer.glb'),export_format='GLB',use_visible=True,export_cameras=False,export_lights=False,export_yup=True,export_apply=True)
    metadata={'viewer_glb_sha256':hashlib.sha256((ROOT/'scene/protolabs-campus-viewer.glb').read_bytes()).hexdigest(),'master_sha256':hashlib.sha256((ROOT/'scene/protolabs-campus.blend').read_bytes()).hexdigest(),'foliage_retention':.30,'visible_vegetation_triangles_before':before,'visible_vegetation_triangles_after':after,'scope':'Reduced foliage only for browser navigation; rendered stills and master retain all leaves.'}
    (ROOT/'scene/viewer-export.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps(metadata))
finally:
    for name,data in originals.items():bpy.data.objects[name].data=data
    for data in lods.values():
        if data.users==0:bpy.data.meshes.remove(data)
