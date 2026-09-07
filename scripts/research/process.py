#!/usr/bin/env python3
"""Reproduce measured terrain and roof constraints from bounded public raw files.
Example: python process.py --raw-dir data/research/raw --output-dir data/research/derived
No Blender dependency. Processing reads LAZ in 1-million-point chunks.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import laspy
from pyproj import Transformer
from scipy.stats import binned_statistic_2d
from scipy.ndimage import distance_transform_edt,gaussian_filter,binary_closing,binary_fill_holes,label
from rasterio.features import shapes
from rasterio.transform import Affine
from shapely.geometry import shape,mapping
ORIGIN_LONLAT=(-93.664082,45.0128453)
VERTICAL_DATUM=303.6
TILES=['4475_49845','4475_49840']

def write(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')

def origin_and_vectors(raw,out):
    transformer=Transformer.from_crs(4326,26915,always_xy=True);origin=transformer.transform(*ORIGIN_LONLAT)
    def local(pair):
        a,b=transformer.transform(*pair);return [round(a-origin[0],3),round(b-origin[1],3)]
    osm=json.loads((raw/'osm_buildings.json').read_text());hq=next(e for e in osm['elements'] if e['id']==663955213)
    write(out/'hq_footprint_local.json',{'source':'OpenStreetMap way663955213','note':'OSM address5840 conflicts with authoritative5540. Lidar is preferred for measured roof projection; OSM roof trace is offset by several metres.','origin_lonlat':ORIGIN_LONLAT,'origin_utm26915':origin,'axes':'x east,y north,metres','vertices':[local([g['lon'],g['lat']]) for g in hq['geometry']]})
    parcels=json.loads((raw/'parcels_1.json').read_text());owned=[]
    for feature in parcels['features']:
        if feature['properties']['OWNER_NM'].strip()!='PROTO LABS INC':continue
        feature['properties']['area_acres']=round(feature['properties']['PARCEL_AREA']/43560,2)
        feature['properties']['local_coordinates_xy_m']=[local(g) for g in feature['geometry']['coordinates'][0]];owned.append(feature)
    if not owned:raise ValueError('Expected headquarters owner not found in live county parcels; inspect current records before accepting changed boundaries.')
    write(out/'campus_parcels.geojson',{'type':'FeatureCollection','features':owned})
    return np.array(origin)

def read_bounded_points(raw,origin):
    ground=[[],[],[]];roofs=[[],[],[]];metadata=[]
    for tile in TILES:
        path=raw/f'USGS_LPC_MN_CentralMissRiver_B22_{tile}.laz'
        with laspy.open(path) as reader:
            metadata.append({'filename':path.name,'point_count':reader.header.point_count,'crs_wkt':reader.header.parse_crs().to_wkt(),'bounds_min':reader.header.mins.tolist(),'bounds_max':reader.header.maxs.tolist()})
            for points in reader.chunk_iterator(1_000_000):
                x=np.asarray(points.x)-origin[0];y=np.asarray(points.y)-origin[1];z=np.asarray(points.z);c=np.asarray(points.classification)
                valid=(c==2)&(x>=-182.5)&(x<=242.5)&(y>=-172.5)&(y<=222.5)
                for dest,values in zip(ground,(x,y,z)):dest.append(values[valid])
                if tile=='4475_49845':
                    valid=(x>-5)&(x<111)&(y>-9)&(y<71)
                    for dest,values in zip(roofs,(x,y,z)):dest.append(values[valid])
    return [np.concatenate(p) for p in ground],[np.concatenate(p) for p in roofs],metadata

def terrain_constraints(ground,origin,metadata):
    x,y,z=ground;xx=np.arange(-180,240.001,5.);yy=np.arange(-170,220.001,5.)
    grid,*_=binned_statistic_2d(x,y,z,statistic='median',bins=[np.r_[xx-2.5,xx[-1]+2.5],np.r_[yy-2.5,yy[-1]+2.5]])
    missing=np.isnan(grid);nearest=distance_transform_edt(missing,return_distances=False,return_indices=True);filled=grid[tuple(nearest)]
    smooth=gaussian_filter(filled,sigma=.65,mode='nearest')
    return {'description':'Ground-class 2 only USGS 2022 lidar. 5m median bins, nearest fill, Gaussian sigma 0.65 cells. Building footprints filled from nearby ground, not roofs.','horizontal_crs':'EPSG6344 NAD83(2011) UTM15N, local origin numeric same as EPSG26915 aerial','origin_utm_m':origin.tolist(),'vertical_datum':'NAVD88 GEOID18 metres','reference_navd88_m':VERTICAL_DATUM,'units':'metres','extent':[-180,-170,240,220],'spacing':5,'x':xx.tolist(),'y':yy.tolist(),'z':np.round(smooth.T-VERTICAL_DATUM,3).tolist(),'z_layout':'z[y_index][x_index]; x east,y north,relative NAVD88-303.6','missing_ground_return_bins':missing.T.tolist(),'source_tiles':sorted(m['filename'] for m in metadata),'point_count_ground_in_extent':len(z)}

def roof_constraints(roofs):
    x,y,z=roofs;step=.25;xx=np.arange(-5,111+step,step);yy=np.arange(-9,71+step,step)
    h,*_=binned_statistic_2d(x,y,z,statistic='median',bins=[xx,yy]);h=h.T;layers={}
    masks=[('total_roof_projection',h>307.8),('main_brick_roof',(h>310.05)&(h<310.8)),('ribbon_roof',(h>311)&(h<314)),('upper_plant_room',(h>314)&(h<314.4)),('north_tower',(h>314.6)&(h<315.3))]
    for name,mask in masks:
        mask=binary_fill_holes(binary_closing(mask,iterations=2));components,_=label(mask);counts=np.bincount(components.ravel());counts[0]=0;mask=components==counts.argmax()
        polygons=[shape(g) for g,value in shapes(mask.astype('uint8'),mask=mask,transform=Affine(step,0,-5,0,step,-9)) if value==1]
        poly=max(polygons,key=lambda p:p.area).simplify(.45,preserve_topology=True)
        layers[name]={'geometry':mapping(poly),'area_m2':round(poly.area,2),'method':'0.25m median lidar raster threshold; morphology closed and holes filled, largest component; simplified 0.45 m. Roof projection, not surveyed wall footprint.'}
    for name,bounds in [('ribbon_north',(61,67.5,29,48)),('ribbon_south',(66,74,5,23)),('white_wing',(80,90,32,50))]:
        a,b,d,e=bounds;mask=(x>a)&(x<b)&(y>d)&(y<e)&(z>308)&(z<314)
        A=np.column_stack([x[mask],y[mask],np.ones(mask.sum())]);zz=z[mask];coef=np.linalg.lstsq(A,zz,rcond=None)[0];error=zz-A@coef
        for _ in range(3):
            good=abs(error)<.25;coef=np.linalg.lstsq(A[good],zz[good],rcond=None)[0];error=zz-A@coef
        layers[name+'_plane']={'equation':'z NAVD88 = a*x+b*y+c; subtract 303.6 for scene z','a':float(coef[0]),'b':float(coef[1]),'c':float(coef[2]),'rms_m':float(np.std(error[abs(error)<.25])),'sample_bounds_xy':bounds,'source':'2022 lidar'}
    return layers

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--raw-dir',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    origin=origin_and_vectors(args.raw_dir,args.output_dir);print('Reading bounded lidar chunks',flush=True)
    ground,roofs,metadata=read_bounded_points(args.raw_dir,origin);print('Deriving terrain and roof constraints',flush=True)
    terrain=terrain_constraints(ground,origin,metadata);roof=roof_constraints(roofs)
    write(args.output_dir/'terrain_grid.json',terrain);write(args.output_dir/'lidar_roof_constraints.json',roof)
    write(args.output_dir/'processing_receipt.json',{'source_snapshot':'2026-09-07','origin_utm_m':origin.tolist(),'reference_navd88_m':VERTICAL_DATUM,'grid_dimensions':[len(terrain['x']),len(terrain['y'])],'ground_point_count':len(ground[0]),'roof_window_point_count':len(roofs[0]),'raw_lidar':metadata,'limitations':['Potential submeter NAD83 versus NAD83(2011) coordinate reconciliation uncertainty.','Missing-ground cells, including building interiors and narrow western edge, use nearest-ground fill before smoothing.','2022 lidar does not prove current facade divisions, signage or interior detail.']})
    print('Saved',args.output_dir/'terrain_grid.json','and lidar_roof_constraints.json')
if __name__=='__main__':main()
