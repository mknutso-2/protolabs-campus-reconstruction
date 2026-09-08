"""Optional NLCD research reproduction; scene builds use the two tracked JSONs.

Run with --raster /path/nlcd-2025-window.tif to avoid network. Rasterio, NumPy,
SciPy and Shapely are required only here. One bounded native30m WCS request is
made when --raster is absent. Categorical resampling is nearest-neighbor only.
"""
from pathlib import Path
import argparse
import hashlib
import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode

SOURCE_SHA256 = '8cc746e3ef6317320543e7afe77af0540cfb608851395d87fa86be386ce2cc46'
ORIGIN = [447671.8750643735, 4984591.8364606025]
PARAMS = {'service':'WCS','version':'1.0.0','request':'GetCoverage',
 'coverage':'mrlc_Land-Cover-Native_conus_year_data:Land-Cover-Native_conus_year_data',
 'crs':'EPSG:5070','response_crs':'EPSG:5070','bbox':'179235,2444745,188535,2454075',
 'width':'310','height':'311','format':'GeoTIFF','time':'2025-01-01T00:00:00.000Z',
 'interpolation':'nearest neighbor'}
URL = 'https://dmsdata.cr.usgs.gov/geoserver/mrlc_Land-Cover-Native_conus_year_data/wcs?'+urlencode(PARAMS)
EXCLUSIONS = [
 {'bbox_xy_m':[-150,1110,110,1320], 'reason':'Spring2026 aerial review: open grass at northern marsh/field margin; conservative exclusion, not measured boundary.'},
 {'bbox_xy_m':[-980,450,-740,610], 'reason':'Spring2026 aerial review: mixed residential road/lawns; conservative exclusion.'}]


def derive(raster, root, output):
    import numpy as np
    import rasterio
    from rasterio.warp import reproject, Resampling
    from rasterio.transform import from_origin
    from scipy.ndimage import binary_erosion, label
    from shapely.geometry import Point, Polygon, box
    from shapely.ops import unary_union
    raw = raster.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != SOURCE_SHA256:
        raise ValueError('Raster differs from reviewed source; review before replacing pinned data: '+actual)
    classes = np.zeros((300,300), dtype=np.uint8)
    with rasterio.open(raster) as src:
        if src.count != 1 or src.crs.to_epsg() != 5070 or src.shape != (311,310):
            raise ValueError('Unexpected source raster layout')
        reproject(src.read(1), classes, src_transform=src.transform, src_crs=src.crs,
                  dst_transform=from_origin(ORIGIN[0]-4500, ORIGIN[1]+4500,30,30),
                  dst_crs='EPSG:26915', resampling=Resampling.nearest)
    if np.any((classes==0)|(classes==250)):
        raise ValueError('Missing class samples in bounded target')
    evidence = json.loads((root/'research/distant-woodland.json').read_text())
    belts = [p for p in evidence['polygons'] if p['scene_eligible']]
    protected = unary_union([Polygon(p['polygon_xy_m']).buffer(30) for p in belts] +
        [box(-180,-170,240,220).buffer(30), box(-170,60,230,405).buffer(30)] +
        [Polygon(p['polygon_xy_m']) for p in evidence['polygons'] if not p['scene_eligible']])
    j,i = np.mgrid[0:300,0:300]
    x,y = -4485+i*30,4485-j*30
    forest = np.isin(classes,[41,42,43])
    excluded = np.array([protected.contains(Point(xx,yy)) for xx,yy in zip(x.flat,y.flat)]).reshape(classes.shape)
    angle = np.degrees(np.arctan2(y+41.42428315068638,x-122.2179957382899))
    distance = np.hypot(x-122.2179957382899,y+41.42428315068638)
    outside = (np.hypot(x,y)>700)&(~excluded)
    cone = (angle>=101.56)&(angle<=171.38)&(distance<=4500)
    selected = binary_erosion(forest,structure=np.ones((3,3)))&outside&cone
    for exclusion in EXCLUSIONS:
        a,b,c,d = exclusion['bbox_xy_m']
        selected &= ~((x>=a)&(x<=c)&(y>=b)&(y<=d))
    components,count = label(selected)  # four-neighbor components; stable row-major labels
    cells = [{'row':int(row),'column':int(col),'class':int(classes[row,col]),
              'x':int(x[row,col]),'y':int(y[row,col]),'patch':int(components[row,col])}
             for row,col in zip(*np.where(selected))]
    if len(cells)!=347 or count!=36:
        raise ValueError('Reviewed selection changed; expected347cells/36patches')
    source = {'provider':'USGS EROS / MRLC Annual NLCD Collection1.2,2025',
      'official_services_url':'https://www.mrlc.gov/data-services-page',
      'official_product_url':'https://www.usgs.gov/centers/eros/science/annual-national-land-cover-database',
      'legend_url':'https://www.mrlc.gov/data/legends/national-land-cover-database-class-legend-and-description',
      'request_url':URL,'request_parameters':PARAMS,'raster_sha256':SOURCE_SHA256,
      'raster_bytes':len(raw),'reviewed_download_utc':'2026-09-07T21:40:08.963762+00:00',
      'product_year':2025,'date_limit':'Annual slice2025 is not an individual image acquisition date.',
      'native_crs':'EPSG:5070 NAD83 CONUS Albers','native_spacing_m':30,
      'access_constraints':'Official WCS metadata: fees NONE, access constraints NONE.',
      'describe_coverage_sha256':'4dececb0732be0e94e33b4ec850efdb35ff6db2420de5793f8a979fe7e13ac5e'}
    grid = {'description':'Dated categorical land cover; forest class is not measured height, closed canopy or a tree census.',
      'source':source,'horizontal_crs':'EPSG:26915','origin_utm_m':ORIGIN,
      'bounds_local_xy_m':[-4500,-4500,4500,4500],'pixel_size_m':30,
      'row_order':'north to south','column_order':'west to east','pixel_centers_start_xy_m':[-4485,4485],
      'width':300,'height':300,'resampling':'Nearest neighbor; no class smoothing or bilinear interpolation.',
      'forest_classes':[41,42,43],'excluded_woody_wetland_class':90,'classes':classes.tolist()}
    output.mkdir(parents=True,exist_ok=True)
    grid_path = output/'nlcd_landcover_grid.json'
    grid_path.write_text(json.dumps(grid,separators=(',',':'))+'\n')
    selection = {'description':'Reviewed conservative distant forest interiors. Positions are30m class-cell centers, not surveyed trees.',
      'grid':'research/nlcd_landcover_grid.json','grid_sha256':hashlib.sha256(grid_path.read_bytes()).hexdigest(),
      'manual_belts_sha256':hashlib.sha256((root/'research/distant-woodland.json').read_bytes()).hexdigest(),
      'method':'Keep only41/42/43, require all8neighbor pixels also forest; exclude<=700m origin radius, measured rectangles and8eligible belt30m buffers, excluded wood05 and reviewed mixed-pixel boxes. Select reference-camera horizontal rays101.56..171.38degrees and distance<=4500m. Four-neighbor patch labels, row-major deterministic order.',
      'manual_exclusions':EXCLUSIONS,'protected_grid_rectangles_xy_m':[[-180,-170,240,220],[-170,60,230,405]],
      'protected_belt_ids':[p['id'] for p in belts],'belt_buffer_m':30,'origin_exclusion_radius_m':700,
      'forest_classes':[41,42,43],'cell_size_m':30,'cell_count':len(cells),'patch_count':int(count),
      'geometry_limits':{'footprint_inset_m':.5,'inferred_height_range_m':[12,18],
        'inferred_group_width_range_m':[26,28],'representation':'Unresolved multiple-crown group, not individual trees.',
        'scope':'Reference-camera background only; no general all-direction landcover completion.'},
      'cells':cells}
    (output/'nlcd_context_selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    return {'cells':len(cells),'patches':int(count),'grid_sha256':selection['grid_sha256']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--raster',type=Path,help='Use existing source TIFF; no network')
    parser.add_argument('--cache',type=Path,default=Path('/tmp/protolabs-nlcd'))
    parser.add_argument('--output',type=Path,help='Defaults to root/research')
    args=parser.parse_args()
    raster=args.raster
    if raster is None:
        args.cache.mkdir(parents=True,exist_ok=True)
        raster=args.cache/'nlcd-2025-window.tif'
        with urlopen(Request(URL,headers={'User-Agent':'Protolabs-campus-research/1.0'}),timeout=90) as response:
            data=response.read(4000001)
        if len(data)>4000000 or data[:4] not in (b'II*\x00',b'MM\x00*'):
            raise ValueError('Unexpected bounded TIFF response')
        raster.write_bytes(data)
    print(json.dumps(derive(raster,args.root,args.output or args.root/'research'),indent=2))


if __name__=='__main__':main()
