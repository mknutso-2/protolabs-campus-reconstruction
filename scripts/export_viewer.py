"""Export a lighter browser GLB while preserving the editable master and rendered foliage.
Invoke through Blender with the master already open. Never saves changes to the master.
"""
import bpy, random, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def bounds(data):
    return ([min(v.co[i] for v in data.vertices) for i in range(3)],
            [max(v.co[i] for v in data.vertices) for i in range(3)])

def distant_proxy(data, template):
    """Fit an existing closed crown proxy to the original local footprint/height.

    Object transforms, belt positions and inferred dimensions do not change.
    The textured full/2000-card trees remain in the master and full GLB.
    """
    low, high=bounds(data);proxy=template.copy()
    proxy.name=data.name+' browser distant opaque crown'
    source_low, source_high=bounds(proxy)
    for vertex in proxy.vertices:
        for axis in range(3):
            u=(vertex.co[axis]-source_low[axis])/(source_high[axis]-source_low[axis])
            vertex.co[axis]=low[axis]+u*(high[axis]-low[axis])
    proxy.update()
    actual_low,actual_high=bounds(proxy)
    error=max(abs(a-b) for a,b in zip(low+high,actual_low+actual_high))
    if error>1e-5:raise ValueError('Distant browser proxy changed its assigned bounds')
    proxy['browser_representation']='Opaque inferred crown proxy; browser only'
    return proxy

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

originals={};lods={};before=after=0;preserved_context_instances=0
proxy_templates=[bpy.data.meshes.get(f'Distant inferred canopy group {i}') for i in range(3)]
proxies={};proxy_instances=0;proxy_before=proxy_after=0
preserved_solid_distant=sum(o.name.startswith('Distant woodland ') and o.get('representation')=='inferred_crown_cluster' for o in bpy.data.objects)
preserved_nlcd_groups=sum(int(o.get('inferred_crown_group_count',0)) for o in bpy.data.objects)
try:
    for obj in bpy.data.objects:
        if obj.type!='MESH' or not any(m and m.name.startswith('CampusVeg_') for m in obj.data.materials):continue
        data=obj.data
        if obj.name.startswith('Distant woodland '):
            if any(template is None for template in proxy_templates):
                raise ValueError('Existing distant crown templates are required for browser proxies')
            if data.name not in proxies:
                index=int(hashlib.sha256(data.name.encode()).hexdigest()[:8],16)%3
                proxies[data.name]=distant_proxy(data,proxy_templates[index])
            replacement=proxies[data.name]
            if not obj.hide_render:
                old_count=sum(len(f.vertices)-2 for f in data.polygons)
                new_count=sum(len(f.vertices)-2 for f in replacement.polygons)
                before+=old_count;after+=new_count
                proxy_before+=old_count;proxy_after+=new_count;proxy_instances+=1
            originals[obj.name]=data;obj.data=replacement
            continue
        # Preserve other marked card LODs, if present. Named Distant woodland
        # objects above use the separate browser-only opaque representation.
        if data.get('context_leaf_cards'):
            if not obj.hide_render:
                triangles=sum(len(f.vertices)-2 for f in data.polygons)
                before+=triangles;after+=triangles;preserved_context_instances+=1
            continue
        if data.name not in lods:lods[data.name]=reduced_leaves(data)
        if not obj.hide_render:
            before+=sum(len(f.vertices)-2 for f in data.polygons)
            after+=sum(len(f.vertices)-2 for f in lods[data.name].polygons)
        originals[obj.name]=data;obj.data=lods[data.name]
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'scene/protolabs-campus-viewer.glb'),export_format='GLB',use_visible=True,export_cameras=False,export_lights=False,export_yup=True,export_apply=True)
    metadata={'viewer_glb_sha256':hashlib.sha256((ROOT/'scene/protolabs-campus-viewer.glb').read_bytes()).hexdigest(),'master_sha256':hashlib.sha256((ROOT/'scene/protolabs-campus.blend').read_bytes()).hexdigest(),'foliage_retention':.30,'preserved_context_lod_instances':preserved_context_instances,'visible_vegetation_triangles_before':before,'visible_vegetation_triangles_after':after,'distant_browser_proxies':{'instances':proxy_instances,'unique_meshes':len(proxies),'triangles_before':proxy_before,'triangles_after':proxy_after,'triangles_per_proxy':sorted({sum(len(f.vertices)-2 for f in p.polygons) for p in proxies.values()}),'source':'Existing original closed Distant inferred canopy group meshes fitted to each source mesh local bounds','object_transforms_and_local_bounds_preserved':True,'existing_solid_distant_groups_preserved':preserved_solid_distant,'existing_nlcd_groups_preserved':preserved_nlcd_groups},'scope':'Campus/north full tree templates retain 30% of leaf cards. Only Distant woodland leaf-card objects use opaque crown proxies fitted to their original local footprint and height; inferred belt layout and existing remote/NLCD groups remain unchanged. Rendered stills, full GLB and master retain their complete source geometry.'}
    (ROOT/'scene/viewer-export.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps(metadata))
finally:
    for name,data in originals.items():bpy.data.objects[name].data=data
    for data in [*lods.values(),*proxies.values()]:
        if data.users==0:bpy.data.meshes.remove(data)
