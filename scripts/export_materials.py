"""Export PBR fallback colors for node-based procedural materials unsupported by glTF."""
import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
colors={}
for m in bpy.data.materials:
 if m.name.startswith(('CampusVeg_','Generic_')):continue
 colors[m.name]={'linearColor':list(m.diffuse_color[:3])}
(root/'scene/materials.json').write_text(json.dumps(colors,indent=2))
