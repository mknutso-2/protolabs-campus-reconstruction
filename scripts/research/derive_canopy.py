#!/usr/bin/env python3
"""Infer sparse north-context canopy envelopes from an existing bounded USGS LAZ.

Requires numpy, scipy, laspy[lazrs]. No network access. Output positions are
canopy-envelope peaks, not surveyed trunks or tree-species identification.
Example:
 python derive_canopy.py --tile /absolute/path/to/USGS_LPC_MN_CentralMissRiver_B22_4475_49845.laz --output-dir /absolute/path/to/research
"""
from pathlib import Path
import argparse, datetime, hashlib, json
import numpy as np
import laspy
from scipy.interpolate import RegularGridInterpolator
from scipy.stats import binned_statistic_2d
from scipy.ndimage import distance_transform_edt, gaussian_filter, maximum_filter, label

ORIGIN=np.array([447671.8750643735,4984591.8364606025])
DATUM=303.6
SOURCE_URL='https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/MN_CentralMissRiver_B22/MN_CentralMissRiver_4_B22/LAZ/USGS_LPC_MN_CentralMissRiver_B22_4475_49845.laz'
SOURCE_SHA256='772f6ee72e6ba327d653a3a9a10f42e867884f0d748cbc8d1b7f2b54dc699436'
AERIAL_NORTH_LIMIT=218.70774547755718

def percentiles(a):
 return {str(q):round(float(np.percentile(a,q)),3) for q in (10,25,50,75,90,95,99)} if len(a) else {}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tile',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
 p.add_argument('--chunk-size',type=int,default=1000000);a=p.parse_args()
 if a.chunk_size<1000 or a.chunk_size>1000000:p.error('chunk-size must be 1000..1000000')
 digest=hashlib.sha256()
 with a.tile.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):digest.update(b)
 if digest.hexdigest()!=SOURCE_SHA256:
  raise ValueError('Tile SHA256 differs from the bounded source recorded in scripts/research/sources.json')
 a.output_dir.mkdir(parents=True,exist_ok=True)
 # Requested north extent fits only this cached tile; no unsupported extension to y450.
 bounds=(-170.,60.,230.,405.)
 gparts=[];vparts=[];counts={'ground_retained_stride8':0,'unclassified_retained':0}
 with laspy.open(a.tile) as r:
  mins=r.header.mins.copy();maxs=r.header.maxs.copy();pointcount=r.header.point_count
  coverage=[float(mins[0]-ORIGIN[0]),float(mins[1]-ORIGIN[1]),float(maxs[0]-ORIGIN[0]),float(maxs[1]-ORIGIN[1])]
  if coverage[0]>bounds[0] or coverage[1]>bounds[1] or coverage[2]<bounds[2] or coverage[3]<bounds[3]:
   raise ValueError('Provided tile does not cover the documented bounded analysis extent')
  for d in r.chunk_iterator(a.chunk_size):
   x=np.asarray(d.x)-ORIGIN[0];y=np.asarray(d.y)-ORIGIN[1];z=np.asarray(d.z);c=np.asarray(d.classification)
   inbounds=(x>=bounds[0])&(x<=bounds[2])&(y>=bounds[1])&(y<=bounds[3])
   gi=np.flatnonzero(inbounds&(c==2))[::8];vi=np.flatnonzero(inbounds&(c==1))
   for inds,dest,key in [(gi,gparts,'ground_retained_stride8'),(vi,vparts,'unclassified_retained')]:
    dest.append(np.column_stack((x[inds],y[inds],z[inds])).astype('float32'));counts[key]+=len(inds)
 ground=np.concatenate(gparts);elevated=np.concatenate(vparts);del gparts,vparts
 gx=np.arange(-170,230.001,5.);gy=np.arange(60,405.001,5.)
 g,*_=binned_statistic_2d(ground[:,0],ground[:,1],ground[:,2],statistic='median',bins=(np.r_[gx-2.5,gx[-1]+2.5],np.r_[gy-2.5,gy[-1]+2.5]))
 missing=np.isnan(g);inds=distance_transform_edt(missing,return_distances=False,return_indices=True)
 g=gaussian_filter(g[tuple(inds)],.65,mode='nearest');interp=RegularGridInterpolator((gx,gy),g,bounds_error=True)
 ground_json={'description':'North-context class2 ground, every eighth selected ground return retained per 1M-point read chunk; 5m median bins, nearest fill, Gaussian sigma0.65 cells. No extrapolation outside output extent; missing bins explicitly marked. Pond surface/missing-ground interpolation is not bathymetry.','horizontal_crs':'EPSG6344 NAD83(2011) UTM15N; same numeric origin as EPSG26915 aerial, submeter datum uncertainty','origin_utm_m':ORIGIN.tolist(),'vertical_datum':'NAVD88 GEOID18 metres','reference_navd88_m':DATUM,'spacing':5,'extent':list(bounds),'x':gx.tolist(),'y':gy.tolist(),'z':np.round(g.T-DATUM,3).tolist(),'z_layout':'z[y_index][x_index]; x east, y north','missing_ground_return_bins':missing.T.tolist(),'source_tile':a.tile.name,'sampled_ground_points':counts['ground_retained_stride8']}
 (a.output_dir/'north_context_ground_grid.json').write_text(json.dumps(ground_json,separators=(',',':'))+'\n')
 x,y,z=elevated.T;h=z-interp(elevated[:,:2]);m=(y>=70)&(y<400)&(x<230)&(h>=3)&(h<=35)
 x,y,z,h=x[m],y[m],z[m],h[m]
 xe=np.arange(-170,231,1.);ye=np.arange(70,401,1.)
 heights,*_=binned_statistic_2d(x,y,h,statistic=lambda v:np.percentile(v,95),bins=(xe,ye))
 returns,*_=binned_statistic_2d(x,y,h,statistic='count',bins=(xe,ye))
 accepted=(returns>=2)&(heights>=3.5)
 # Require a spatially connected elevated envelope; reject isolated poles/stray returns.
 patches,npatches=label(accepted,np.ones((3,3),int));sizes=np.bincount(patches.ravel());accepted&=sizes[patches]>=12
 clean=np.where(accepted,heights,0.)
 # Smooth only to choose broad peaks. Measurements use original local cell percentiles.
 smooth=gaussian_filter(clean,.7)
 peaks=(smooth==maximum_filter(smooth,size=9,mode='constant'))&(smooth>=4)&accepted
 candidates=sorted(zip(*np.where(peaks)),key=lambda ij:smooth[ij],reverse=True)
 chosen=[]
 for ix,iy in candidates:
  px,py=float(xe[ix]+.5),float(ye[iy]+.5)
  if any((px-r['position'][0])**2+(py-r['position'][1])**2<max(5.,min(r['crown_diameter_m']*.65,8.))**2 for r in chosen):continue
  xlo,xhi=max(0,ix-4),min(clean.shape[0],ix+5);ylo,yhi=max(0,iy-4),min(clean.shape[1],iy+5)
  patch=clean[xlo:xhi,ylo:yhi];vals=patch[patch>0]
  if len(vals)<12:continue
  spread=float(np.percentile(vals,90)-np.percentile(vals,10))
  if spread<.8:continue  # Reject locally flat plateaus, including likely small roof surfaces.
  canopy=float(np.percentile(vals,95));groundz=float(interp([[px,py]])[0]-DATUM)
  area=float(len(vals));diameter=float(np.clip(2*np.sqrt(area/np.pi),4,12))
  chosen.append({'position':[px,py],'ground_z':round(groundz,3),'canopy_height':round(canopy,3),'top_z':round(groundz+canopy,3),'crown_diameter_m':round(diameter,2),'local_canopy_cells_1m':len(vals),'local_canopy_height_p90_minus_p10_m':round(spread,2),'aerial_context':'within cached Spring2026 image' if py<=218.7 else 'beyond cached aerial extent; lidar envelope inference only'})
 chosen.sort(key=lambda r:(r['position'][1],r['position'][0]))
 for index,row in enumerate(chosen,1):
  row['candidate_id']=f'north-canopy-{index:03d}'
  within_aerial=row['position'][1]<=AERIAL_NORTH_LIMIT
  row['aerial_context']='within cached Spring2026 image' if within_aerial else 'beyond cached aerial extent; lidar envelope inference only'
  # These tiny isolated envelopes have no image cross-check. They may be small
  # trees, poles or other objects; omit them from automatic tree placement.
  row['scene_eligible']=not (not within_aerial and row['canopy_height']<7 and row['local_canopy_cells_1m']<20)
  row['review_status']=('small isolated unverified object; omitted from scene' if not row['scene_eligible'] else
    'vegetation pattern consistent with 2026 aerial; trunk and species unverified' if within_aerial else
    'lidar envelope only; object identity unverified')
 out={'description':'Sparse inferred canopy envelope peaks for distant scene context; not surveyed tree locations. Do not add a uniform forest band over pond/open grass.','source':{'url':SOURCE_URL,'filename':a.tile.name,'sha256':digest.hexdigest(),'file_bytes':a.tile.stat().st_size,'point_count':pointcount,'campaign_dates':'2022-04-25 through 2022-06-02; individual tile flight date not determined','published':'2023-09-14','cached_acquisition_date':'2026-09-07','tile_bounds_local_xy_m':coverage,'classes_used':{'ground':2,'canopy_envelope':1}},'generated_date':datetime.date.today().isoformat(),'origin_utm_m':ORIGIN.tolist(),'vertical_datum':'NAVD88 GEOID18 metres','reference_navd88_m':DATUM,'candidate_extent_xy_m':[-170,70,230,400],'ground_grid_file':'north_context_ground_grid.json','method':{'ground':'Class2 stride8 retained per chunk, 5m median/nearest-fill/0.65cell Gaussian; see separate grid.','canopy':'Class1 above ground3..35m, 1m-cell p95 with at least2 returns, connected envelope at least12cells. Gaussian0.7cell local peaks in9x9m window; reject local9x9 patch with p90-p10<0.8m; 5..8m peak suppression. Height=local9x9m p95 of accepted cell envelopes, crown diameter from occupied local9x9m area bounded4..12m.','placement':'XY locates envelope peak, not a measured trunk. Use asset world height equal canopy_height and base equal ground_z; crown diameter is an approximation.'},'limitations':['Only cached tile used; x<-171.875 and y>408.154 are unavailable, so no unsupported grid to y450.','Class1 is unclassified elevated returns, not verified vegetation; flat-patch and area filters reject many poles/roofs but cannot certify every candidate.','Existing aerial was inspected qualitatively through y218.7; northern candidates have no aerial visual cross-check.','Leaf-off/partial-leaf campaign and occlusion may underrepresent canopy; inferred crown shapes/species are not measured.','Candidate centers may not be actual trunk locations; scene-tree scaling remains an interpretation.','Ground missing bins near pond are interpolated, not bathymetry; no ownership inference for context trees.'],'validation':{'aerial_north_limit_local_y_m':AERIAL_NORTH_LIMIT,'candidates_within_aerial':sum(r['position'][1]<=AERIAL_NORTH_LIMIT for r in chosen),'scene_eligible_count':sum(r['scene_eligible'] for r in chosen),'excluded_candidate_ids':[r['candidate_id'] for r in chosen if not r['scene_eligible']],'exclusion_rule':'Beyond cached aerial, height below7m and fewer than20 accepted1m canopy cells in local9x9m window; cautious omission of ambiguous small objects, not positive pole identification.','osm_building_overlap':'No north-analysis overlap in cached osm_buildings.json; OSM incompleteness means this does not certify absence of buildings.','read_chunk_size':a.chunk_size},'point_counts':counts,'candidate_count':len(chosen),'candidate_height_percentiles_m':percentiles([r['canopy_height'] for r in chosen]),'rows':chosen}
 (a.output_dir/'north_context_canopy_constraints.json').write_text(json.dumps(out,indent=2)+'\n')
 np.savez_compressed(a.output_dir/'canopy_diagnostic_cache.npz',x=xe[:-1]+.5,y=ye[:-1]+.5,height=clean,ground_x=gx,ground_y=gy,ground=g-DATUM)
 print(json.dumps({'candidate_count':len(chosen),'height_percentiles_m':out['candidate_height_percentiles_m'],'source_bounds':coverage,'point_counts':counts,'files':['north_context_canopy_constraints.json','north_context_ground_grid.json']},indent=2))

if __name__=='__main__':main()
