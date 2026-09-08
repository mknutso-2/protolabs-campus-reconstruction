#!/usr/bin/env python3
"""Bounded canopy-envelope constraints around the existing 2026 campus tree traces.

Uses the two already-recorded USGS 2022 LAZ tiles. No network access. Centers are
2026 visual crown/trunk traces, not surveyed trunks; class 1 is unclassified.
"""
from pathlib import Path
import argparse,datetime,hashlib,json
import numpy as np
import laspy
from scipy.spatial import cKDTree
from scipy.ndimage import label
from shapely.geometry import Polygon,Point
from shapely import contains_xy
from shapely.ops import unary_union
from pyproj import Transformer

ORIGIN=np.array([447671.8750643735,4984591.8364606025]);DATUM=303.6

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--tile-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 p.add_argument('--layout',type=Path,default=Path(__file__).resolve().parents[2]/'research/site-layout.json')
 p.add_argument('--osm-buildings',type=Path,required=True)
 p.add_argument('--cache',type=Path,help='Optional disposable local point cache for repeated diagnostics')
 a=p.parse_args();root=Path(__file__).resolve().parents[2]
 layout=json.loads(a.layout.read_text());e=layout['extent'];scale=(e['xmax']-e['xmin'])/3000
 centers=np.array([[e['xmin']+t['center_px'][0]*scale-ORIGIN[0],e['ymax']-t['center_px'][1]/2500*(e['ymax']-e['ymin'])-ORIGIN[1]] for t in layout['trees']])
 center_tree=cKDTree(centers);maxradius=8.;bounds=[centers[:,0].min()-maxradius,centers[:,1].min()-maxradius,centers[:,0].max()+maxradius,centers[:,1].max()+maxradius]
 manifest=json.loads((root/'scripts/research/sources.json').read_text());sources=[s for s in manifest['sources'] if s['id'].startswith('usgs-lidar-')]
 evidence=[]
 for source in sources:
  path=a.tile_dir/source['filename'];sha=digest(path)
  if sha!=source['sha256']:raise ValueError('Cached source checksum mismatch: '+path.name)
  with laspy.open(path) as r:
   coverage=[float(r.header.mins[0]-ORIGIN[0]),float(r.header.mins[1]-ORIGIN[1]),float(r.header.maxs[0]-ORIGIN[0]),float(r.header.maxs[1]-ORIGIN[1])]
   evidence.append({'filename':path.name,'url':source['url'],'sha256':sha,'bytes':path.stat().st_size,'point_count':r.header.point_count,'coverage_local_xy':coverage,'source_date':source['source_date'],'published_date':source.get('published_date')})
 cache_signature=hashlib.sha256(json.dumps({'layout':digest(a.layout),'sources':[s['sha256'] for s in evidence],'maxradius':maxradius},sort_keys=True).encode()).hexdigest()
 loaded=False
 if a.cache and a.cache.exists():
  cache=np.load(a.cache)
  if str(cache['signature'])==cache_signature:
   points=cache['points'];loaded=True
 if not loaded:
  parts=[]
  for source in evidence:
   with laspy.open(a.tile_dir/source['filename']) as r:
    for d in r.chunk_iterator(1000000):
     x=np.asarray(d.x)-ORIGIN[0];y=np.asarray(d.y)-ORIGIN[1];z=np.asarray(d.z);c=np.asarray(d.classification)
     good=(x>=bounds[0])&(x<=bounds[2])&(y>=bounds[1])&(y<=bounds[3])&np.isin(c,[1,2,6])
     ix=np.flatnonzero(good)
     if not len(ix):continue
     near=center_tree.query(np.column_stack((x[ix],y[ix])),distance_upper_bound=maxradius)[0]<=maxradius
     ix=ix[near];parts.append(np.column_stack((x[ix],y[ix],z[ix],c[ix])).astype('float32'))
   print('READ',source['filename'],flush=True)
  points=np.concatenate(parts)
  if a.cache:
   a.cache.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(a.cache,signature=np.array(cache_signature),points=points)
 # Exclude all cached building plan surfaces with a 1m margin. This is an
 # intentionally conservative canopy/roof separator; overhanging foliage can be lost.
 transform=Transformer.from_crs(4326,26915,always_xy=True);polygons=[]
 for element in json.loads(a.osm_buildings.read_text()).get('elements',[]):
  if element.get('tags',{}).get('building') and len(element.get('geometry',[]))>=4:
   coords=[transform.transform(q['lon'],q['lat']) for q in element['geometry']];polygon=Polygon([(x-ORIGIN[0],y-ORIGIN[1]) for x,y in coords])
   if polygon.is_valid:polygons.append(polygon)
 building_union=unary_union(polygons);mask=building_union.buffer(1.0)
 ground=points[points[:,3]==2,:3];elevated=points[points[:,3]==1,:3];roof=points[points[:,3]==6,:3]
 gt=cKDTree(ground[:,:2]);et=cKDTree(elevated[:,:2]);rt=cKDTree(roof[:,:2]) if len(roof) else None
 results=[]
 for index,(trace,center) in enumerate(zip(layout['trees'],centers)):
  x,y=center;radius=float(np.clip(trace['crown_radius_px']*scale+1.5,3.,6.))
  g=ground[gt.query_ball_point(center,4.)];r=elevated[et.query_ball_point(center,radius)]
  # Fit local ground slope from actual class2 returns, with one robust outlier pass.
  reasons=[];ground_ok=len(g)>=20
  if ground_ok:
   A=np.column_stack((g[:,0]-x,g[:,1]-y,np.ones(len(g))));coef=np.linalg.lstsq(A,g[:,2],rcond=None)[0]
   residual=g[:,2]-A@coef;mad=float(np.median(np.abs(residual-np.median(residual))));keep=np.abs(residual-np.median(residual))<=max(.15,3*1.4826*mad)
   if keep.sum()>=20:coef=np.linalg.lstsq(A[keep],g[keep,2],rcond=None)[0]
   else:keep=np.ones(len(g),dtype=bool)
   ground_nav=float(coef[2]);rmse=float(np.sqrt(np.mean((g[keep,2]-A[keep]@coef)**2)))
   ground_ok=rmse<=.4 and np.hypot(*coef[:2])<=.7
  else:coef=np.array([0,0,float(np.median(g[:,2])) if len(g) else 303.6]);ground_nav=float(coef[2]);rmse=None
  if not ground_ok:reasons.append('insufficient_or_rough_local_ground')
  inside=contains_xy(mask,r[:,0],r[:,1]) if len(r) else np.zeros(0,bool)
  excluded_roof_plan=int(inside.sum());r=r[~inside]
  heights=r[:,2]-(coef[2]+coef[0]*(r[:,0]-x)+coef[1]*(r[:,1]-y)) if len(r) else np.array([])
  valid=(heights>=2)&(heights<=30);r=r[valid];heights=heights[valid]
  # A 1m cell envelope reduces bias from varying return density. Broad connected
  # support rejects isolated lamps/poles; class1 still cannot prove vegetation.
  ij=np.floor(r[:,:2]-center+8).astype(int) if len(r) else np.empty((0,2),int)
  cells=np.full((16,16),np.nan);counts=np.zeros((16,16),int)
  for key in np.unique(ij,axis=0):
   hit=np.all(ij==key,axis=1);xx,yy=key
   if 0<=xx<16 and 0<=yy<16:
    counts[xx,yy]=int(hit.sum())
    if counts[xx,yy]>=3:cells[xx,yy]=np.percentile(heights[hit],95)
  patches,_=label(np.isfinite(cells),np.ones((3,3),int));sizes=np.bincount(patches.ravel());large=np.isfinite(cells)&(sizes[patches]>=6)
  vals=cells[large];cellxy=np.column_stack(np.where(large))-.5-7+center
  count=len(vals);spread=float(np.percentile(vals,90)-np.percentile(vals,10)) if count else None
  nearcenter=float(np.min(np.linalg.norm(cellxy-center,axis=1))) if count else None
  diameter=float(2*np.sqrt(count/np.pi)) if count else None
  # Flat broad plateaus near known roofs are not accepted automatically.
  flat=spread is not None and spread<.55
  building_distance=float(building_union.distance(Point(x,y))) if polygons else None
  roof_count=len(rt.query_ball_point(center,radius)) if rt else 0
  if count<6:reasons.append('insufficient_connected_canopy_support')
  if nearcenter is None or nearcenter>3:reasons.append('canopy_support_offset_from_uncertain_trace')
  if flat:reasons.append('flat_elevated_envelope_possible_roof_or_trimmed_shrub')
  if building_distance is not None and building_distance<1.0:reasons.append('trace_inside_or_on_building_plan')
  # Rectangular source coverage must include the query circle; union permits the
  # shared boundary between the two cached north/south tiles.
  coverage_union=unary_union([Polygon([(q['coverage_local_xy'][0],q['coverage_local_xy'][1]),(q['coverage_local_xy'][2],q['coverage_local_xy'][1]),(q['coverage_local_xy'][2],q['coverage_local_xy'][3]),(q['coverage_local_xy'][0],q['coverage_local_xy'][3])]) for q in evidence])
  complete=coverage_union.buffer(.03).covers(Point(x,y).buffer(radius))
  if not complete:reasons.append('query_circle_outside_cached_lidar_coverage')
  eligible=not reasons
  h95=float(np.percentile(vals,95)) if count else None
  confidence='medium' if eligible else 'low_ineligible'
  if eligible and count>=15 and len(g)>=100 and (building_distance is None or building_distance>radius+1) and nearcenter<=1.5:confidence='higher_relative_confidence'
  if eligible and excluded_roof_plan:confidence='medium_roof_margin_excluded'
  row={'tree_array_index':index,'tree_id':trace['id'],'center_px':trace['center_px'],'position':np.round(center,3).tolist(),
   'trace_crown_radius_m':round(trace['crown_radius_px']*scale,3),'query_radius_m':round(radius,3),'scene_eligible':eligible,'confidence':confidence,
   'ground_navd88_m':round(ground_nav,3) if ground_ok else None,'ground_z':round(ground_nav-DATUM,3) if ground_ok else None,
   'canopy_height_m':round(h95,3) if eligible else None,'top_z':round(ground_nav-DATUM+h95,3) if eligible else None,
   'observed_connected_envelope_diameter_m':round(diameter,3) if count else None,
   'observed_height_p95_cell_envelope_m':round(h95,3) if h95 is not None else None,
   'observed_height_p95_points_m':round(float(np.percentile(heights,95)),3) if len(heights) else None,
   'observed_height_p99_cell_envelope_m':round(float(np.percentile(vals,99)),3) if count else None,
   'support':{'local_ground_returns':len(g),'ground_plane_rmse_m':round(rmse,3) if rmse is not None else None,'accepted_elevated_returns':len(r),'connected_canopy_cells_1m':count,'cell_height_p90_minus_p10_m':round(spread,3) if spread is not None else None,'nearest_supported_cell_to_trace_m':round(nearcenter,3) if nearcenter is not None else None,'class1_returns_excluded_by_roof_plan':excluded_roof_plan,'nearby_class6_building_returns':roof_count,'distance_to_cached_building_plan_m':round(building_distance,3) if building_distance is not None else None,'full_query_coverage':bool(complete)},
   'ineligibility_reasons':reasons,'risks':['2026 trace and 2022 lidar may describe different growth/removal/leaf state; do not claim current surveyed height.','Trace center uncertainty is typically 2–5m; measured envelope can span neighboring crowns or miss an offset top.','Class1 is unclassified; broad support and roof masks reduce but cannot eliminate non-vegetation objects.']}
  results.append(row)
 payload={'description':'Conservative local canopy envelopes for the 92 existing campus tree traces; not a trunk inventory or 2026 height survey.',
  'generated_date':datetime.date.today().isoformat(),'origin_utm_m':ORIGIN.tolist(),'horizontal_alignment':'2022 lidar NAD83(2011)/UTM15N EPSG6344 numerically aligned with 2026 aerial NAD83/UTM15N EPSG26915; submeter datum uncertainty retained.',
  'vertical_datum':'NAVD88 GEOID18 metres','reference_navd88_m':DATUM,'sources':evidence,
  'layout_file':'research/site-layout.json','layout_sha256':digest(a.layout),'building_mask_source':'cached OpenStreetMap building outlines, 1m buffer; incomplete/approximate and may suppress overhanging canopy','building_mask_sha256':digest(a.osm_buildings),
  'method':{'ground':'All class2 returns within4m; local plane least squares with one MAD outlier pass; >=20 points, RMSE<=0.4m and grade<=0.7 required.',
   'canopy':'Query radius=clamp(aerial traced crown radius+1.5m,3,6m); class1 heights2..30m above local ground plane; exclude cached building footprints buffered1m; 1m-cell p95 with>=3returns; connected support>=6cells; reject flat envelope spread<0.55m and offset>3m. Recommended height=p95 of supported cell envelopes, not maximum.',
   'eligibility':'Reject insufficient ground, insufficient/offset/flat canopy, trace on building, or partial tile coverage. Higher relative confidence needs >=15 cells, >=100 ground points, trace within1.5m of support and no nearby building mask.',
   'integration':'Match tree_array_index AND tree_id/center against layout. Eligible: scale actual mesh bottom-to-top to canopy_height_m and base to ground_z. This local query is not a full crown-width measurement: observed_connected_envelope_diameter_m can be query-truncated; retain separately documented inferred/2026-traced width. Ineligible: do not invent a measured height. Keep separate north-context canopy deduplication.'},
  'summary':{'tree_count':len(results),'eligible':sum(r['scene_eligible'] for r in results),'higher_relative_confidence':sum(r['confidence']=='higher_relative_confidence' for r in results),'retained_near_trace_points':len(points)},'rows':results}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(payload,indent=2)+'\n')
 print(json.dumps(payload['summary'],indent=2))
 for r in results:
  if -75<r['position'][1]<8 and -30<r['position'][0]<110:print(json.dumps({k:r[k] for k in ['tree_array_index','tree_id','position','canopy_height_m','ground_z','top_z','confidence','ineligibility_reasons']}))

if __name__=='__main__':main()
