#!/usr/bin/env python3
"""Download the geographic inputs of the historical generators into <repo>/data (or $HEX_DATA).

Sources (all free):
  Natural Earth 10m vectors as GeoJSON, pinned to release v5.1.2 of github.com/nvkelso/natural-earth-vector
  NOAA ETOPO 2022 relief, exported per scenario bounding box from the NCEI image service (float32 GeoTIFF, metres)
  Koppen-Geiger 0.5 degree climate classes (Kottek et al. 2006, 1976-2000 period) from koeppen-geiger.vu-wien.ac.at

Files that already exist are skipped; delete one to refetch it.  Run tools/extract_game_xml.py afterwards for the
type-name lists the generators read from the installed game.
"""
import io, os, sys, time, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('HEX_DATA', os.path.join(os.path.dirname(HERE), 'data'))

NE_TAG = 'v5.1.2'
NE_FILES = ['ne_10m_land', 'ne_10m_lakes', 'ne_10m_lakes_europe', 'ne_10m_rivers_lake_centerlines', 'ne_10m_rivers_europe',
            'ne_10m_admin_0_countries', 'ne_10m_admin_0_disputed_areas', 'ne_10m_admin_1_states_provinces']
NE_URL = f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{NE_TAG}/geojson/{{}}.geojson'

# name -> (lon_min, lat_min, lon_max, lat_max, width_px, height_px); the generators hard-code the same geometry
ETOPO = {
    'etopo_ru.tif': (17.0, 37.0, 108.0, 72.0, 1820, 700),   # 0.05 deg
    'etopo_ca.tif': (-18.45, 27.55, -13.25, 29.50, 1040, 390),   # 0.005 deg: the Canary Islands need the full 15 arc-second detail
    'etopo_hi.tif': (-160.45, 18.75, -154.65, 22.40, 1160, 730),   # 0.005 deg: the Hawaiian Islands
    'etopo_cn.tif': (84.0, 17.0, 136.0, 52.0, 1040, 700),   # 0.05 deg: China 1928
    'etopo_es.tif': (-10.5, 34.0, 5.0, 44.5, 1550, 1050),   # 0.01 deg: Iberia, the Balearics and northern Morocco (Spain 1936)
}
ETOPO_URL = ('https://gis.ngdc.noaa.gov/arcgis/rest/services/DEM_mosaics/DEM_all/ImageServer/exportImage'
             '?bbox={},{},{},{}&bboxSR=4326&size={},{}&imageSR=4326&format=tiff&pixelType=F32'
             '&interpolation=RSP_BilinearInterpolation&f=image')

KOPPEN_URL = 'http://koeppen-geiger.vu-wien.ac.at/data/Koeppen-Geiger-ASCII.zip'


def fetch(url, dest, tries=3):
    if os.path.exists(dest):
        print('  have', os.path.relpath(dest, DATA)); return
    print('  get ', os.path.relpath(dest, DATA), '<-', url[:100])
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'civ5-custom-mods'}), timeout=300) as r:
                body = r.read()
            break
        except Exception as e:
            if i == tries - 1: raise
            print('   retry after', e); time.sleep(5)
    tmp = dest + '.part'
    with open(tmp, 'wb') as f: f.write(body)
    os.replace(tmp, dest)


def main():
    os.makedirs(os.path.join(DATA, 'koppen'), exist_ok=True)
    print('Natural Earth', NE_TAG)
    for name in NE_FILES: fetch(NE_URL.format(name), os.path.join(DATA, name + '.geojson'))
    print('ETOPO 2022')
    for name, (x0, y0, x1, y1, w, h) in ETOPO.items(): fetch(ETOPO_URL.format(x0, y0, x1, y1, w, h), os.path.join(DATA, name))
    print('Koppen-Geiger')
    kg = os.path.join(DATA, 'koppen', 'Koeppen-Geiger-ASCII.txt')
    if os.path.exists(kg): print('  have koppen/Koeppen-Geiger-ASCII.txt')
    else:
        z = os.path.join(DATA, 'koppen', 'Koeppen-Geiger-ASCII.zip'); fetch(KOPPEN_URL, z)
        zipfile.ZipFile(z).extract('Koeppen-Geiger-ASCII.txt', os.path.join(DATA, 'koppen')); os.remove(z)
    # sanity: the ETOPO exports must have exactly the pixel grid the generators index into
    try:
        import numpy as np
        from PIL import Image
        for name, (*_, w, h) in ETOPO.items():
            a = np.array(Image.open(os.path.join(DATA, name)))
            assert a.shape == (h, w) and a.dtype == np.float32, (name, a.shape, a.dtype)
            print(f'  {name}: {a.shape[1]}x{a.shape[0]} float32, {a.min():.0f}..{a.max():.0f} m')
    except ImportError:
        print('  (numpy/Pillow missing, ETOPO exports not checked)')
    print('done:', DATA)


if __name__ == '__main__':
    main()
