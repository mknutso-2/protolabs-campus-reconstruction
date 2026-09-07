"""Reacquire the bounded official regional DEM; Pillow is needed only for this step.

Normal scene reproduction consumes the committed JSON and requires no network.
A later upstream mosaic may differ; every run records its actual source hash.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from PIL import Image
import argparse,datetime,hashlib,json,math,tempfile

ROOT=Path(__file__).resolve().parents[2]


def download(out):
    service='https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer'
    def fetch(url,limit):
     with urlopen(Request(url,headers={'User-Agent':'Protolabs-campus-reconstruction/1.0'}),timeout=75) as r:
      raw=r.read(limit+1)
     if len(raw)>limit:raise RuntimeError('Bounded download limit exceeded')
     return raw
    metadata=fetch(service+'?f=pjson',1000000);(out/'service-metadata.json').write_bytes(metadata)
    origin=(447671.8750643735,4984591.8364606025)
    bbox=[origin[0]-4525,origin[1]-4525,origin[0]+4525,origin[1]+4525]
    params={'bbox':','.join(map(str,bbox)),'bboxSR':26915,'imageSR':26915,'size':'181,181','format':'tiff','pixelType':'F32','noData':-999999,'interpolation':'RSP_BilinearInterpolation','renderingRule':json.dumps({'rasterFunction':'None'},separators=(',',':')),'f':'json'}
    url=service+'/exportImage?'+urlencode(params)
    raw=fetch(url,1000000);export=json.loads(raw);(out/'export-response.json').write_bytes(raw)
    if 'href' not in export:raise RuntimeError(export)
    image=fetch(export['href'],4000000);(out/'regional-dem.tif').write_bytes(image)
    receipt={'service_url':service,'metadata_url':service+'?f=pjson','request_url':url,'request_parameters':params,'export_response':export,'source_image_sha256':hashlib.sha256(image).hexdigest(),'source_image_bytes':len(image),'service_metadata_sha256':hashlib.sha256(metadata).hexdigest(),'acquired_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'origin_utm_m':origin,'sample_extent_local_xy_m':[-4500,-4500,4500,4500],'sample_spacing_m':50,'sample_count':[181,181],'raw_pixel_bbox_utm_m':bbox}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Downloaded regional float DEM:',len(image),'bytes',flush=True)


def convert(base,root):
    receipt=json.loads((base/'receipt.json').read_text());image=Image.open(base/'regional-dem.tif')
    assert hashlib.sha256((base/'regional-dem.tif').read_bytes()).hexdigest()==receipt['source_image_sha256']
    assert hashlib.sha256((base/'service-metadata.json').read_bytes()).hexdigest()==receipt['service_metadata_sha256']
    assert image.mode=='F' and image.size==(181,181)
    scale=image.tag_v2[33550];tie=image.tag_v2[33922]
    assert abs(scale[0]-50)<1e-8 and abs(scale[1]-50)<1e-8
    bbox=receipt['raw_pixel_bbox_utm_m']
    assert abs(tie[3]-bbox[0])<1e-5 and abs(tie[4]-bbox[3])<1e-5
    values=list(image.getdata());assert all(math.isfinite(v) and 250<v<350 for v in values)
    rows=[values[i*181:(i+1)*181] for i in range(181)]
    z=[[round(v-303.6,4) for v in row] for row in reversed(rows)]
    metadata=json.loads((base/'service-metadata.json').read_text())
    record={'description':'USGS 3DEP bare-earth regional context sampled at50m. Preserve original near5m measured meshes; these data support regional terrain, not local survey or bathymetry.',
     'source':receipt,'service_publication_statement':metadata['description'],'service_copyright':metadata['copyrightText'],
     'horizontal_crs':'EPSG:26915 NAD83 / UTM zone15N','vertical_datum':'NAVD88 metres interpreted from USGS CONUS3DEP convention; this export does not identify per-source vertical datum or geoid realization.',
     'source_acquisition_date':'Not supplied for individual contributing rasters by exportImage; service publication date is not terrain acquisition date.',
     'reference_navd88_m':303.6,'origin_utm_m':receipt['origin_utm_m'],'extent':[-4500,-4500,4500,4500],'spacing':50,
     'x':list(range(-4500,4501,50)),'y':list(range(-4500,4501,50)),'z':z,'z_layout':'z[y_index][x_index], axes both increasing; TIFF north-first rows reversed.',
     'source_elevation_range_m':[min(values),max(values)],'scene_z_range_m':[min(map(min,z)),max(map(max,z))],
     'valid_sample_count':len(values),'nodata_sample_count':0,'conversion_rounding_m':.0001,
     'limits':['50m bilinear service resampling resolves broad relief, not individual berms, drainage, curbs or bank profiles.','Mosaic uses service default ByAttribute Best ascending, First operator; contributing raster selection and acquisition dates are not returned by exportImage.','Water surfaces and wetland interpolation are not bathymetry.','NAD83 vs near-grid NAD83(2011) registration uncertainty remains submeter; no extra manual horizontal shift applied.','Use an outside-only transition at measured mesh boundaries; do not replace or flatten original campus/north grids.','Regional extent is finite9km square; scenery outside it remains unmodeled.']}
    (root/'research/regional_context_ground_grid.json').write_text(json.dumps(record,separators=(',',':'))+'\n')
    print(record['scene_z_range_m'],len(values))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-cache',type=Path,help='Use an existing receipt/metadata/TIFF directory without downloading')
    args=parser.parse_args()
    if args.from_cache:
        convert(args.from_cache,ROOT)
    else:
        with tempfile.TemporaryDirectory(prefix='protolabs-regional-dem-') as directory:
            out=Path(directory);download(out);convert(out,ROOT)


if __name__=='__main__':main()
