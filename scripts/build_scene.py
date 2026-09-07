"""Generate editable Protolabs reconstruction. Blender 4.2 LTS; metres, X east/Y north.
All assets deterministic. Geometry labels record evidence classes; see research ledger.
"""
import bpy, math, random, json, sys, argparse
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from font_asset import load_blender_font
PROJECT_FONT = load_blender_font(ROOT)
args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
p = argparse.ArgumentParser(); p.add_argument('--render', default=''); p.add_argument('--width', type=int, default=1440); p.add_argument('--samples',type=int,default=40); p.add_argument('--export',action='store_true'); p.add_argument('--no-trees',action='store_true')
opt = p.parse_args(args)
random.seed(5540)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for b in bpy.data.materials: bpy.data.materials.remove(b)
COL={}
def collection(name):
 c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); COL[name]=c; return c
for n in ['Architecture | photo + GIS','Roof structure | photo interpreted','Site | aerial trace','Vegetation | inferred species','Details | photo interpreted','Context | approximate','Cameras']: collection(n)
active='Architecture | photo + GIS'
def finish(o,name,mat=None):
 o.name=name
 for c in list(o.users_collection): c.objects.unlink(o)
 COL[active].objects.link(o)
 if mat:o.data.materials.append(mat)
 o['evidence']='Photo interpreted; dimensions approximate except GIS plan constraints'
 return o

def mat(name,col,rough=.5,metal=0,noise=0,scale=10):
 col=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in col)
 m=bpy.data.materials.new(name); m.diffuse_color=(*col,1); m.use_nodes=True
 n=m.node_tree.nodes; l=m.node_tree.links; bs=n.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*col,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
 if noise:
  tc=n.new('ShaderNodeTexCoord'); tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=scale; tex.inputs['Detail'].default_value=3
  l.new(tc.outputs['Object'],tex.inputs['Vector']); ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.15; ramp.color_ramp.elements[1].position=.82
  ramp.color_ramp.elements[0].color=(*(v*(1-noise) for v in col),1); ramp.color_ramp.elements[1].color=(*(min(1,v*(1+noise)) for v in col),1)
  l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color'])
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.2;bump.inputs['Distance'].default_value=.015 if scale>10 else .05;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
 return m
brick=mat('Warm umber precast / photo colour',(.217,.157,.14),.84,noise=.19,scale=36)
brick_alt=mat('Muted burgundy precast',(.248,.185,.165),.8,noise=.14,scale=36)
brick_light=mat('Light brown panel bands',(.255,.196,.171),.79,noise=.12,scale=36)
white=mat('Ivory coated aluminum',(.74,.77,.76),.32,.28,noise=.045,scale=3)
steel=mat('White structural steel',(.69,.74,.75),.3,.55)
roofmetal=mat('Silver standing seam roof',(.64,.72,.76),.34,.58,noise=.06,scale=28)
frame=mat('Anodized blue grey mullions',(.13,.32,.40),.28,.7)
glass=mat('Blue reflective insulated glazing',(.065,.165,.235),.13,.72)
bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=.12;bs.inputs['IOR'].default_value=1.45
interior=mat('Unspecified dark interior depth',(.025,.033,.037),.8)
roof=mat('Charcoal aggregate membrane',(.155,.158,.151),.91,noise=.38,scale=38)
asphalt=mat('Weathered asphalt / metric noise',(.145,.152,.147),.93,noise=.27,scale=3)
concrete=mat('Concrete curbs & walks',(.49,.495,.46),.83,noise=.12,scale=45)
paint=mat('Faded parking paint',(.61,.60,.41),.84,noise=.2,scale=70)
grass=mat('Mown summer grass',(.17,.235,.057),.93,noise=.38,scale=9)
meadow=mat('Prairie meadow',(.24,.275,.105),.95,noise=.35,scale=1.2)
gravel=mat('Landscape river rock',(.40,.40,.355),.87,noise=.6,scale=30)
dark=mat('Dark bronze columns and sign',(.038,.067,.069),.42,.4)
blue=mat('Protolabs blue identity',(.015,.34,.52),.34,.22)
red=mat('Hydrant red',(.38,.028,.024),.42,.3)
black=mat('Rubber & grilles',(.016,.021,.021),.85)
water=mat('Wetland pond',(.06,.09,.074),.2,.25,noise=.14,scale=.4)

def cube(name,loc,size,ma,bevel=0):
 sx,sy,sz=[v/2 for v in size];v=[(x*sx,y*sy,z*sz) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 o=mesh(name,v,[tuple(reversed(face)) for face in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]],ma);o.location=loc
 if bevel:
  m=o.modifiers.new('Light-catching edge','BEVEL');m.width=bevel;m.segments=2
  o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def mesh(name,verts,faces,ma):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(name,d);COL[active].objects.link(o);o.data.materials.append(ma);return o

def polygon(name,pts,z,ma,depth=0):
 if depth:
  v=[(x,y,z) for x,y in pts]+[(x,y,z+depth) for x,y in pts];n=len(pts);f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 else:v=[(x,y,z) for x,y in pts];f=[tuple(range(len(pts)))]
 return mesh(name,v,f,ma)

def beam(name,a,b,r,ma,verts=10):
 a,b=Vector(a),Vector(b);d=b-a;v=[]
 for z in [-d.length/2,d.length/2]:
  v.extend([(r*math.cos(i*2*math.pi/verts),r*math.sin(i*2*math.pi/verts),z) for i in range(verts)])
 f=[tuple(range(verts-1,-1,-1)),tuple(range(verts,2*verts))]+[(i,(i+1)%verts,(i+1)%verts+verts,i+verts) for i in range(verts)]
 o=mesh(name,v,f,ma);o.location=(a+b)/2;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o

def line(name,pts,rad,ma):
 cv=bpy.data.curves.new(name,'CURVE');cv.dimensions='3D';cv.resolution_u=1;cv.bevel_depth=rad;cv.bevel_resolution=1;s=cv.splines.new('POLY');s.points.add(len(pts)-1)
 for p,c in zip(s.points,pts):p.co=(*c,1)
 o=bpy.data.objects.new(name,cv);COL[active].objects.link(o);o.data.materials.append(ma);return o

def text(name,txt,loc,size,ma,rotation=(math.pi/2,0,0),align='CENTER'):
 cv=bpy.data.curves.new(name,'FONT');cv.body=txt;cv.size=size;cv.align_x=align;cv.extrude=.014;cv.bevel_depth=.003
 cv.font=PROJECT_FONT
 o=bpy.data.objects.new(name,cv);COL[active].objects.link(o);o.location=loc;o.rotation_euler=rotation;o.data.materials.append(ma);return o

def glazing(name,a,b,z0,z1,spacing=1.45,lower=True):
 a,b=Vector((*a,0)),Vector((*b,0));t=(b-a).normalized();out=Vector((t.y,-t.x,0));length=(b-a).length
 # recessed backing is a neutral depth cue, not an invented accurate interior
 back=[a-out*.6,b-out*.6];mesh(name+' interior shadow',[(q.x,q.y,z) for q,z in [(back[0],z0),(back[1],z0),(back[1],z1),(back[0],z1)]],[(0,1,2,3)],interior)
 n=max(1,round(length/spacing))
 for i in range(n):
  left=a+t*(length*i/n)+out*.015;right=a+t*(length*(i+1)/n)+out*.015
  mesh(name+f' pane {i:02}',[(q.x,q.y,z) for q,z in [(left,z0),(right,z0),(right,z1),(left,z1)]],[(0,1,2,3)],glass)
 for i in range(n+1):
  c=a+t*(length*i/n)+out*.05;beam(name+' vertical mullion',(c.x,c.y,z0),(c.x,c.y,z1),.045,frame,4)
 for z in [z0,z1,z1-.72]+([z0+.62] if lower else []):
  beam(name+' transom',(a.x+out.x*.055,a.y+out.y*.055,z),(b.x+out.x*.055,b.y+out.y*.055,z),.044,frame,4)

def wall_edge(name,a,b,z0,z1,ma,thick=.22):
 a,b=Vector((*a,0)),Vector((*b,0));d=b-a;o=cube(name,((a.x+b.x)/2,(a.y+b.y)/2,(z0+z1)/2),(d.length,thick,z1-z0),ma,.018);o.rotation_euler.z=math.atan2(d.y,d.x);return o

terrain=json.loads((ROOT/'research/terrain_grid.json').read_text())
tx=terrain['x'];ty=terrain['y'];tz=terrain['z']
def ground(x,y):
 fx=max(0,min(len(tx)-1.001,(x-tx[0])/(tx[1]-tx[0])));fy=max(0,min(len(ty)-1.001,(y-ty[0])/(ty[1]-ty[0])));ix=int(fx);iy=int(fy);u=fx-ix;v=fy-iy
 return (tz[iy][ix]*(1-u)+tz[iy][ix+1]*u)*(1-v)+(tz[iy+1][ix]*(1-u)+tz[iy+1][ix+1]*u)*v

def terrain_polygon(name,pts,offset,ma):
 from mathutils.geometry import tessellate_polygon
 import bmesh
 points=[Vector((x,y,0)) for x,y in pts];tris=tessellate_polygon([points]);v=[];f=[]
 for tri in tris:
  base=len(v);v.extend(tuple(points[q]) if isinstance(q,int) else tuple(q) for q in tri);f.append((base,base+1,base+2))
 o=mesh(name,v,f,ma);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001)
 bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=24,use_grid_fill=True)
 for ve in bm.verts:ve.co.z=ground(ve.co.x,ve.co.y)+offset
 bm.to_mesh(o.data);bm.free();return o

# GIS-constrained main footprint and photo-interpreted elevations.
H=6.55
cube('Main block occupied volume',(28,23.25,1.15),(55.8,46.5,10.9),brick)
# Forward face built with depth around dark narrow windows.
for i in range(18):
 x=1.25+i*3.08
 cube('Portrait window reveal',(x,-.13,2.6),(1.22,.36,2.72),interior,.025)
 cube('Portrait blue glazing',(x,-.325,2.64),(1.03,.045,2.48),glass)
 for xx in [x-.57,x+.57]:cube('Recessed jamb',(xx,-.365,2.6),(.06,.07,2.66),frame)
 for zz in [1.26,3.20,3.95]:cube('Window transom',(x,-.365,zz),(1.2,.08,.075),white)
 cube('Projecting pale sill',(x,-.405,1.23),(1.28,.33,.08),concrete,.018)
 # Broad alternate cast panel bands above and between windows.
 cube('Subtle precast upper bands',(x,.0,5.34),(1.36,.035,2.28),brick_light if i%2 else brick_alt)
for x in [j*3.08 for j in range(19)]:cube('Vertical precast panel joint',(x,-.025,3.35),(.018,.035,6.7),interior)
for z in [1.05,4.22,5.91]:cube('Horizontal facade joint',(28,-.045,z),(56,.023,.019),interior)
cube('Brick parapet',(28,23.3,H),(56.6,47.1,.46),brick_alt,.025)
cube('Main roof aggregate',(28,23.3,H+.245),(55.9,46.4,.07),roof)
for a,b in [((-.4,-.4),(56.4,-.4)),((-.4,47),(56.4,47)),((-.4,-.4),(-.4,47)),((56.4,-.4),(56.4,47))]:wall_edge('Metal parapet coping',a,b,H+.43,H+.51,white,.15)
# West service stair and north service additions derived from the stepped GIS outline.
cube('West frontage projecting stair',(-2.2,3.2,3.65),(4.3,7.2,7.3),brick_alt,.025)
cube('North service addition',(22,51,3.5),(24,9,7),brick)
cube('North stair overrun',(20,56.8,3.6),(19,4.3,7.2),brick_alt)
for i in range(11):
 y=4+i*3.7;glazing('West facade',(-.86,y+1.22),(-.86,y),1.2,3.8,1.3,False)

# Correct GIS outline to lidar roof extent; wall thickness/parapet offset remains inferred.
for ob in list(COL['Architecture | photo + GIS'].objects):
 ob.location.x+=3.4;ob.location.y+=1.1
# Lower-level west windows follow falling terrain, visible in aerial shadow facade.
for i in range(11):
 y=5+i*3.75;glazing('West lower-level glazing',(2.51,y+1.65),(2.51,y),-3.5,-1.0,1.65,False)

# Central connector below sculptural roof, open reception court.
connector=[(55.9,0),(72.5,8.5),(76.5,11.3),(76.5,24.15),(65.65,50.03),(56,47)]
connector_obj=polygon('Central low connector',connector,-4.5,interior,7.75)
# The photo-visible opaque south return continues the precast treatment;
# dark backing is retained behind glazing, rather than applied to the exposed wall.
connector_obj.data.materials.append(brick)
connector_obj.data.materials.append(roof)
connector_obj.data.polygons[2].material_index=1
connector_obj.data.polygons[1].material_index=2
# Replace visible facade with opaque shadow-backed glazing surfaces forward of volume.
glazing('Angled atrium', (72.8,7.9),(76.85,10.0),.20,4.85,1.15)
glazing('Atrium east',(76.88,10),(76.88,24.12),.20,3.4,1.4)
wall_edge('Atrium white fascia',(73,7.8),(76.95,9.83),3.4,4.72,white,.4)
wall_edge('Atrium east fascia',(76.9,9.9),(76.9,24.4),3.4,4.72,white,.4)
# White NE office wing, rotated 27.7 degrees in plan.
wing=[(76.66,24.16),(104.65,38.86),(92.16,63.50),(65.65,50.03)]
polygon('NE wing enclosed volume',wing,-4.5,interior,7.45)
polygon('NE aggregate flat roof',wing,4.56,roof,.15)
for i in range(4):
 a,b=wing[i],wing[(i+1)%4]
 wall_edge('White metal fascia',a,b,3.25,4.83,white,.35)
 wall_edge('Pale base plinth',a,b,-4.5,.15,white,.3)
 glazing('NE continuous window ribbon',a,b,.15,3.25,1.48,False)
 d=Vector(b)-Vector(a); n=max(1,round(d.length/6.7))
 for j in range(n+1):
  pos=Vector(a)+d*j/n; cube('Full height white pier',(pos.x,pos.y,1.70),(.29,.29,3.1),white,.02)
 for j in range(1,round(d.length/.95)):
  pos=Vector(a)+d*j/round(d.length/.95);cube('Fascia panel seam',(pos.x,pos.y,4.05),(.014,.014,1.5),frame)
# Front vestibule and lower horizontal logo canopy.
cube('Long lower logo canopy',(62,-.8,4.50),(27.0,4.5,1.20),white,.025)
cube('Under canopy dark soffit',(62,-.8,3.875),(26.8,4.3,.09),dark)
for x in [44,61.7]:glazing('Lower reception doors',(x-1.15,-.48),(x+1.15,-.48),.04,4.23,1.15,False)
# East-facing glass vestibule under the low half of the truss.
cube('Vestibule interior',(74.0,4.5,2.1),(4.3,4.6,4.2),interior)
for a,b in [((76.23,2.0),(76.23,7.0)),((76.23,7.0),(71.75,7.0)),((71.75,2.0),(76.23,2.0))]:
 glazing('Main vestibule',a,b,.05,4.02,1.0)
 wall_edge('Vestibule white fascia',a,b,4.02,4.60,white,.22)
text('Street number','5540',(76.39,4.5,4.23),.31,blue,(math.pi/2,0,math.pi/2))
for y in [4.24,4.74]:beam('Door pull handle',(76.35,y,1.0),(76.35,y,1.7),.021,steel)
text('Current fascia wordmark','PROTOLABS',(60.0,-3.07,4.38),.62,blue)
# Geometric hexagon corporate mark, custom rebuilt from reference.
def logo(cx,y,cz,s):
 pts=[(cx+s*math.cos(math.pi/6+i*math.pi/3),y,cz+s*math.sin(math.pi/6+i*math.pi/3)) for i in range(7)]
 line('Hexagonal Protolabs outline',pts,.055*s,blue)
 for dz in [-.21,.21]:line('Mark inner bars',[(cx-.36*s,y,cz+dz*s-.18*s),(cx+.36*s,y,cz+dz*s+.18*s)],.09*s,blue)
logo(55.6,-3.09,4.61,.53)

# Slab joints and small wall lights visible at the frontage.
for x in [8+i*6.2 for i in range(8)]:
 cube('Wall light backing',(x,.69,5.99),(.20,.12,.27),dark,.025)
 cube('Wall light lens',(x,.61,5.96),(.14,.06,.10),white,.025)
for x in range(44,73,3):line('Entry sidewalk expansion joint',[(x,-6,ground(x,-6)+.18),(x,-3,ground(x,-3)+.18)],.01,dark)
# Main approach looks northwest: rotate frontage extension to point east/southeast.
# Canopy stretches west from vestibule along original south face; vestibule closes connector corner.
active='Roof structure | photo interpreted'
# Roof planes fit to 2022 lidar (NAVD88), local z datum = 303.6m.
# A bent ribbon: high edge follows x60.75 then turns southeast to the cantilever tip.
roof_constraints=json.loads((ROOT/'research/lidar_roof_constraints.json').read_text())
def rz(x,y):
 q=roof_constraints['ribbon_north_plane' if y>=27.5 else 'ribbon_south_plane'];return q['a']*x+q['b']*y+q['c']-303.6
high=[(78.25,-7.5),(60.75,27.5),(60.75,53.75)]
low=[(78.45,9.0),(69.0,27.5),(69.0,51.4)]
verts=[(x,y,rz(x,y)) for pair in zip(high,low) for x,y in pair]
ro=mesh('Measured canted ribbon roof',verts,[(0,1,3,2),(2,3,5,4)],roofmetal)
ro['evidence']='Plane fitted to USGS 2022 lidar; rms 0.034m south / 0.015m north within fit sample bounds'
so=ro.modifiers.new('Metal roof thickness','SOLIDIFY');so.thickness=.15
for edge in [high,low]:line('Roof edge flashing',[(x,y,rz(x,y)) for x,y in edge],.105,white)
for seg in range(2):
 length=(Vector(high[seg+1])-Vector(high[seg])).length
 for j in range(int(length/.61)+1):
  t=j/max(1,int(length/.61));a=Vector(high[seg]).lerp(Vector(high[seg+1]),t);b=Vector(low[seg]).lerp(Vector(low[seg+1]),t)
  beam('Metric standing seam',(a.x,a.y,rz(a.x,a.y)+.06),(b.x,b.y,rz(b.x,b.y)+.06),.018,white,4)
# Cantilever leading edge, high point south and low point north, as in entrance photograph.
A=Vector((78.25,-7.5,rz(78.25,-7.5)-.16));B=Vector((78.45,9,rz(78.45,9)-.16))
beam('Roof leading edge',A,B,.12,steel,4)
beam('Truss lower chord',A-Vector((0,0,.9)),B-Vector((0,0,.72)),.08,steel,4)
for i in range(9):
 t=i/8;q=A.lerp(B,t);lower=q-Vector((0,0,.90-.18*t));beam('Truss vertical web',q,lower,.04,steel,6)
 if i<8:beam('Triangular truss diagonal',lower,A.lerp(B,(i+1)/8),.04,steel,6)
for yy,ts in [(-1.5,[.02,.20,.40,.70]),(7.8,[.67,.85,.99])]:
 x=78.4;beam('Dark cylindrical entrance column',(x,yy,.10),(x,yy,3.85),.255,dark,20)
 for t in ts:beam('Fan brace',(x,yy,3.84),A.lerp(B,t)-Vector((0,0,.82)),.073,steel,8)
beam('Column lower tie',(78.4,-1.5,3.84),(78.4,7.8,3.84),.08,steel,8)
# Recessed triangular clerestory lies behind the open truss in plan.
tri=[(75.65,0,5.1),(75.65,0,rz(75.65,0)-.3),(75.65,9,rz(75.65,9)-.3),(75.65,9,5.1)]
mesh('Recessed triangular clerestory',tri,[(0,1,2,3)],glass)
for y in [i*1.1 for i in range(9)]:beam('Clerestory vertical mullion',(75.66,y,5.1),(75.66,y,rz(75.65,y)-.3),.039,frame,4)
for z in [6,7,8]:
 ymax=min(9,(351.9638173150447-.5212809745025934*75.65-303.6-z-.3)/.2571791859818191)
 if ymax>0:beam('Clerestory transom',(75.68,0,z),(75.68,ymax,z),.039,frame,4)

active='Details | photo interpreted'
# Photo/aerial placed plant screens and rooftop mechanical assemblies.
for x,y,sx,sy,z,hh in [(17.5,25.5,15,15,6.85,3.8),(83,42,12,3.8,4.65,1.65),(58,44.5,6,10,6.85,4.45)]:
 cube('Roof plant white screen',(x,y,z+hh/2),(sx,sy,hh),white,.035)
 for j in range(round(sx/.55)):
  cube('Plant screen panel joints',(x-sx/2+j*.55,y-sy/2-.025,z+hh/2),(.014,.025,hh-.04),frame)
for x,y in [(35,16),(42,15),(38,21),(58,51),(70,26),(69,30)]:
 z=6.85 if x<55 else 4.67
 cube('Mechanical unit base',(x,y,z+.50),(4.2,2.15,1),white,.07)
 for xx in [x-1.05,x+1.05]:
  beam('Circular condenser fan',(xx,y,z+1),(xx,y,z+1.10),.67,black,20)
  for j in range(7):beam('Fan louvre',(xx-.6,y-.5+j*.17,z+1.13),(xx+.6,y-.5+j*.17,z+1.13),.021,steel,4)
for pts in [[(20,17,6.99),(20,10,6.99),(34,10,6.99),(34,15,6.99)],[(15,29,6.99),(38,29,6.99),(38,23,6.99)]]:line('Mechanical conduit runs',pts,.12,steel)
# Sidewalk/stone entry landscape, polygon follows angled building edge.
active='Site | aerial trace'
polygon('Facade landscape river stones',[(-3,-2),(42,-2),(42,-6.3),(61,-6.3),(61,-4),(74,-4),(78,8),(80,24),(108,38),(108,42),(76,27),(73,12),(55,1),(-3,1)],.05,gravel,.11)
polygon('Entry concrete apron',[(42,-7),(65,-7),(75,-2),(78,9),(76,12),(70,6),(65,-.7),(60,-.7),(60,-4),(43,-4)],.06,concrete,.10)
# Lidar terrain under traced current pavement and islands.
verts=[(x,y,tz[j][i]-.12) for j,y in enumerate(ty) for i,x in enumerate(tx)]
faces=[]
for j in range(len(ty)-1):
 for i in range(len(tx)-1):
  a=j*len(tx)+i;faces.append((a,a+1,a+1+len(tx),a+len(tx)))
mesh('Measured rolling ground',verts,faces,meadow)
north_ground=json.loads((ROOT/'research/north_context_ground_grid.json').read_text())
nx,ny,nz=north_ground['x'],north_ground['y'],north_ground['z']
rows=[j for j,y in enumerate(ny) if y>=ty[-1]]
v=[];f=[]
for j in rows:
 for i,x in enumerate(nx):
  blend=min(1,max(0,(ny[j]-ty[-1])/10))
  v.append((x,ny[j],ground(x,ty[-1])*(1-blend)+nz[j][i]*blend))
for j in range(len(rows)-1):
 for i in range(len(nx)-1):
  a=j*len(nx)+i;f.append((a,a+1,a+len(nx)+1,a+len(nx)))
mesh('North context ground | lidar',v,f,meadow)
# Keep the support sheet below both measured near terrain and the continuous
# regional DEM. The visible regional relief is created by distant_context.
regional_grid=json.loads((ROOT/'research/regional_context_ground_grid.json').read_text())
surround_z=min(min(row) for row in tz+nz+regional_grid['z'])-.5
polygon('Distant ground surround',[(-4500,-4500),(4500,-4500),(4500,4500),(-4500,4500)],surround_z,meadow)
layout=json.loads((ROOT/'research/site-layout.json').read_text());extent=layout['extent']
def pixel(pt):return (extent['xmin']+pt[0]/3000*(extent['xmax']-extent['xmin'])-447671.8750643735,extent['ymax']-pt[1]/2500*(extent['ymax']-extent['ymin'])-4984591.8364606025)
for poly in layout['polygons']:
 ma={'asphalt':asphalt,'asphalt_road':asphalt,'grass':grass,'water':water,'landscape_rock':gravel}[poly['material']]
 pts=[pixel(pt) for pt in poly['points_px']];off=.02 if ma==asphalt else .11
 terrain_polygon(poly['id'],pts,off,ma)
 if ma in [grass,gravel]:line(poly['id']+' concrete curb',[(x,y,ground(x,y)+.13) for x,y in pts+[pts[0]]],.11,concrete)
# Parking stripe geometry follows observed aisle directions, elevations and bay rhythm.
for row in layout['parking_rows']:
 a,b=[Vector(pixel(q)) for q in row['car_centerline_px']];n=row['estimated_bays'];step=(b-a)/max(1,n-1);hd=Vector((row['vehicle_heading_image'][0],-row['vehicle_heading_image'][1])).normalized();depth=row['bay_depth_px']*(extent['xmax']-extent['xmin'])/3000
 for i in range(n+1):
  center=a+step*(i-.5);u=center-hd*depth/2;v=center+hd*depth/2
  pts=[]
  for k in range(5):q=u.lerp(v,k/4);pts.append((q.x,q.y,ground(q.x,q.y)+.038))
  line('Traced parking stripe',pts,.033,paint)
# Modeled generic parked vehicles are scenery; occupancy is an aerial impression.
try:
 from vehicles import create_vehicle_asset
 vehicles=[create_vehicle_asset('Generic parked vehicle '+str(i),color=c,variant='suv' if i%3==0 else 'sedan') for i,c in enumerate([(.2,.25,.29),(.65,.67,.66),(.10,.12,.13),(.35,.075,.04),(.85,.84,.81)])]
 for o in vehicles:
  for c in list(o.users_collection):c.objects.unlink(o)
  COL[active].objects.link(o);o.hide_render=True;o.hide_viewport=True
 for row in layout['parking_rows']:
  a,b=[Vector(pixel(q)) for q in row['car_centerline_px']];n=row['estimated_bays'];hd=Vector((row['vehicle_heading_image'][0],-row['vehicle_heading_image'][1])).normalized()
  for j in range(n):
   if random.random()>row['suggested_aerial_occupancy_fraction']*.45:continue
   pos=a.lerp(b,j/max(1,n-1));
   # The official matched aerial shows an empty arrival court. Vehicles remain
   # generic context dressing in distant lots, never claimed current occupancy.
   if -5 < pos.x < 180 and -60 < pos.y < 67:continue
   src=vehicles[random.randrange(len(vehicles))];o=bpy.data.objects.new('Parked generic vehicle',src.data);COL[active].objects.link(o);o.location=(pos.x,pos.y,ground(pos.x,pos.y)+.06);o.rotation_euler.z=math.atan2(-hd.x,hd.y)
except ImportError:print('Vehicle assets pending')
# Terrain-conform initial facade paving.
for ob in list(COL[active].objects):
 if ob.type=='MESH' and ob.name.startswith(('Facade landscape','Entry concrete')):
  for v in ob.data.vertices:v.co.z+=ground(v.co.x,v.co.y)

# Monument sign at driveway/road, flagpole in stone island.
active='Details | photo interpreted'
prior_details=set(COL[active].objects)
cube('Monument sign base',(56,-33,.10),(6.5,1.1,.22),gravel,.06)
cube('Dark monument sign',(56,-33,1.5),(5.8,.27,2.75),dark,.05)
text('Monument brand','PROTOLABS',(56.1,-33.16,1.89),.52,blue)
text('Monument tagline','Manufacturing. Accelerated.',(56.15,-33.16,1.45),.20,white)
text('Monument address','5540 Pioneer Creek Drive',(56,-33.17,.61),.265,white)
line('Blue monument rule',[(53.1,-33.18,.98),(58.9,-33.18,.98)],.032,blue)
logo(53.68,-33.17,2.12,.40)
beam('Flagpole',(62,-18,.12),(62,-18,12.85),.058,steel,16)
# US flag, static cloth geometry; posed by inference (not event/current flag condition).
verts=[];faces=[]
for j in range(9):
 for i in range(17):
  u=i/16;v=j/8;verts.append((62+u*2.6,-18+.23*math.sin(u*7+v*1.2)*u,12.75-v*1.38-.16*u))
for j in range(8):
 for i in range(16):a=j*17+i;faces.append((a,a+1,a+18,a+17))
fl=mesh('US flag cloth',verts,faces,red);fl.data.materials.append(white);fl.data.materials.append(blue)
for f in fl.data.polygons:
 j=f.index//16;i=f.index%16;f.material_index=2 if j<4 and i<7 else (1 if j%2 else 0)
beam('Red hydrant',(61,-18,.1),(61,-18,.74),.14,red,12);beam('Hydrant cross arm',(60.75,-18,.5),(61.25,-18,.5),.095,red,10)
# Photo sign triangulated to 2026 orthophoto; flagpole top isolated in lidar.
for ob in set(COL[active].objects)-prior_details:
 isflag=ob.name.startswith(('Flagpole','US flag','Red hydrant','Hydrant'))
 dx,dy=(22.2,12.2) if isflag else (38.39,5.19)
 if ob.type in ['MESH','CURVE','FONT']:
  ob.location.x+=dx;ob.location.y+=dy
  ob.location.z+=ground(84.2,-5.8) if isflag else ground(94.39,-27.81)

for x,y in [(84,-28),(112,15),(152,51),(-38,32),(-41,-14)]:
 beam('Parking light pole',(x,y,0),(x,y,8.7),.105,dark,12);cube('Pole concrete footing',(x,y,.40),(.55,.55,.8),concrete,.08)
 for d in [-1,1]:cube('LED luminaire',(x+d*.6,y,8.68),(1.0,.45,.11),dark,.055)
# Accessible sign posts and paint hatching near lobby.
for i in range(5):
 x=38+i*3.5;beam('Accessible bay signpost',(x,-1.1,.1),(x,-1.1,1.9),.022,steel,8);cube('Accessible parking sign',(x,-1.14,1.74),(.22,.035,.30),blue,.015)
for i in range(10):line('Accessible access aisle hatch',[(54+i*.4,-10,.05),(52+i*.4,-5.3,.05)],.038,paint)

# Terrain features and context evidence class.
active='Context | approximate'
# Adjacent massing provides context only, not asserted operational campus membership.
for x,y,sx,sy,h in [(-143,-5,73,47,7),(0,-110,77,57,7.1),(87,-104,39,31,6),(134,-112,38,37,6.3)]:
 cube('Adjacent building context',(x,y,ground(x,y)+h/2),(sx,sy,h),brick_light,.06);cube('Context aggregate roof',(x,y,ground(x,y)+h+.07),(sx,sy,.2),roof)

# Vegetation module creates real leaf meshes, reused at inferred planting points.
active='Vegetation | inferred species'
if not opt.no_trees:
 try:
  from vegetation import create_tree_asset, create_shrub_asset
  # Assets are created in current collection; relocate through finish for explicit provenance.
  assets=[create_tree_asset('Maple canopy '+str(i),seed=900+i,height=12.0+i,crown=7.0+i*.35,variant=['broad','upright','spreading'][i]) for i in range(3)]
  for o in assets:
   for c in list(o.users_collection):c.objects.unlink(o)
   COL[active].objects.link(o);o.hide_render=True;o.hide_viewport=True
  canopy=json.loads((ROOT/'research/north_context_canopy_constraints.json').read_text())
  measured=[row for row in canopy['rows'] if row.get('scene_eligible',True)]
  from campus_trees import add_campus_trees
  campus_report=add_campus_trees(ROOT,COL[active],assets,ground,pixel,measured)
  bpy.context.scene['Campus tree report']=json.dumps(campus_report)
  bounds=[]
  for src in assets:
   low=[min(v.co[k] for v in src.data.vertices) for k in range(3)];high=[max(v.co[k] for v in src.data.vertices) for k in range(3)];bounds.append((low,high))
  for j,row in enumerate(measured):
   src=assets[j%3];low,high=bounds[j%3];h=row['canopy_height'];width=row['crown_diameter_m'];vertical=h/(high[2]-low[2]);horizontal=width/max(high[0]-low[0],high[1]-low[1]);x,y=row['position']
   o=bpy.data.objects.new('North canopy envelope '+row.get('candidate_id',str(j+1)),src.data);COL[active].objects.link(o);o.location=(x,y,row['ground_z']-low[2]*vertical);o.scale=(horizontal,horizontal,vertical);o.rotation_euler.z=random.random()*6.283
   o['evidence']='Lidar envelope peak; trunk, species and crown shape inferred';o['canopy_height_m']=h;o['canopy_top_local_z']=row['top_z']
  shrub=create_shrub_asset('Landscape shrub asset',seed=444,height=1.0,width=1.4)
  for c in list(shrub.users_collection):c.objects.unlink(shrub)
  COL[active].objects.link(shrub);shrub.hide_render=True;shrub.hide_viewport=True
  for j in range(29):
   if j<14:x,y=2+j*3.7,-1.7
   else:x,y=79+(j-14)*1.7,25+(j-14)*.88
   o=bpy.data.objects.new('Foundation shrub',shrub.data);COL[active].objects.link(o);o.location=(x,y,ground(x,y)+.13);o.rotation_euler.z=random.random()*6.28
 except ImportError:print('Vegetation module pending; no placeholder trees substituted')

# Distant wooded belts are separate inferred context, never a substitute for
# the measured immediate pond terrain and canopy envelopes.
if not opt.no_trees:
 from distant_context import add_distant_context
 distant_report=add_distant_context(ROOT,COL['Context | approximate'],assets)
 bpy.context.scene['Distant context report']=json.dumps(distant_report)

# Base world is replaced below by the licensed reference-oriented low-sun sky.
world=bpy.data.worlds.new('Physical daylight') if not bpy.data.worlds else bpy.data.worlds[0];bpy.context.scene.world=world;world.use_nodes=True
n=world.node_tree.nodes;n.clear();sky=n.new('ShaderNodeTexSky');sky.sky_type='NISHITA';sky.sun_elevation=math.radians(32);sky.sun_rotation=math.radians(135);sky.altitude=.3;sky.air_density=1;sky.dust_density=.55;sky.sun_disc=True
bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.3;out=n.new('ShaderNodeOutputWorld');world.node_tree.links.new(sky.outputs[0],bg.inputs[0]);world.node_tree.links.new(bg.outputs[0],out.inputs[0])
active='Cameras'
# Camera transforms are approximation to photo viewpoint, never claimed calibrated.
cameras={
 'reference_aerial':{'position':[166,-108,31],'target':[50,19,3.6],'lens':50,'reference':'protolabs-official-hq-exterior-2024.jpg'},
 'entrance_detail':{'position':[81,-27,3.2],'target':[64,1,6.4],'lens':30,'reference':'businessjournal-entrance-2018.jpg'},
 'arrival':{'position':[80,-69,3.1],'target':[54,7,5.6],'lens':36,'reference':'machine-design-frontage-2024.png'},
 'campus_overview':{'position':[208,-179,164],'target':[42,34,0],'lens':46,'reference':'aerial_2026.jpg'}
}
fit=json.loads((ROOT/'research/reference_drone_camera_fit.json').read_text())
cameras['reference_aerial'].update(position=fit['position'],target=fit['target_100m_forward'],lens=fit['lens_mm'],reference=fit['reference_image'],fit_rms_pixels=fit['rms_pixel_weighted'])
cameras['entrance_detail'].update(position=[94,-7,1.75],target=[75,3.5,5.5],lens=28)
cameras['arrival'].update(position=[115,-39,2.0],target=[72,13,4.4],lens=27)
for name,cfg in cameras.items():
 bpy.ops.object.camera_add(location=cfg['position']);c=finish(bpy.context.object,name);c.rotation_euler=(Vector(cfg['target'])-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=cfg['lens'];c.data.sensor_fit='HORIZONTAL';c.data.sensor_width=36;
 if name=='reference_aerial':c.rotation_euler=fit['rotation_euler_xyz_radians']
 c.data.clip_end=4500;c.data.clip_start=.1;c['reference']=cfg['reference'];cfg['rotation_euler']=list(c.rotation_euler)
scene=bpy.context.scene;scene.camera=bpy.data.objects['reference_aerial'];scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=opt.samples;scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.035;scene.cycles.max_bounces=6;scene.cycles.transparent_max_bounces=6;scene.render.threads_mode='FIXED';scene.render.threads=6
scene.render.resolution_x=opt.width;scene.render.resolution_y=round(opt.width*2/3);scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.35;scene.view_settings.gamma=1.05
scene.render.fps=24;scene.frame_end=288
(ROOT/'scene').mkdir(exist_ok=True);(ROOT/'deliverables').mkdir(exist_ok=True)
(ROOT/'scene/cameras.json').write_text(json.dumps(cameras,indent=2)+'\n')
scene['Fidelity status']='Reference-led exterior reconstruction; measured constraints plus photo-interpreted details. See accuracy report for inspection status and limitations.'
scene['Origin UTM EPSG26915']=[447671.8750643735,4984591.8364606025]
from visual_finish import apply_visual_finish
apply_visual_finish()
from frontage_finish import apply_frontage_finish
apply_frontage_finish()
from monument_finish import apply_monument_finish
apply_monument_finish(ROOT)
from water_finish import apply_water_finish
scene['Water surface report']=json.dumps(apply_water_finish(ROOT))
from parking_finish import apply_parking_finish
scene['Parking correction report']=json.dumps(apply_parking_finish(ROOT))
from material_quality import apply_material_quality
apply_material_quality(ROOT)
exec(compile((ROOT/'scripts/export_materials.py').read_text(),str(ROOT/'scripts/export_materials.py'),'exec'))
# Pack reference-independent asset textures and fonts into editable master.
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene/protolabs-campus.blend'))
if opt.export:
 bpy.ops.export_scene.gltf(filepath=str(ROOT/'scene/protolabs-campus.glb'),export_format='GLB',use_visible=True,export_cameras=False,export_lights=False,export_yup=True,export_apply=True)
if opt.render:
 scene.camera=bpy.data.objects[opt.render];scene.render.filepath=str(ROOT/'deliverables'/f'{opt.render}.png');bpy.ops.render.render(write_still=True)
if opt.export:exec(compile((ROOT/'scripts/export_viewer.py').read_text(),str(ROOT/'scripts/export_viewer.py'),'exec'))
print('SCENE_READY',len(bpy.data.objects))
