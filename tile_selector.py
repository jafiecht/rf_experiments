import geopandas as gpd
import pandas as pd
import shapely
import json
import matplotlib.pyplot as plt
import requests
import subprocess
import os

def getDEM():

  #Load boundary, buffer, then reproject
  #################################################################
  boundary = gpd.read_file('data/rootdata/boundary.shp')
  buffered = boundary.copy()
  buffered['geometry'] = buffered['geometry'].buffer(125)
  buffered['geometry'] = buffered['geometry'].envelope
  buffered.to_file('data/rootdata/buffered_boundary.shp')
  buffered = buffered.to_crs({'init': 'epsg:4326'})

  #Import the tile extent file, then convert to a geodataframe
  #################################################################
  extents = pd.read_csv('data/rootdata/boundaries.csv', sep=",", header=None, names=['path', 'geometry'])
  extents['geometry'] = extents['geometry'].apply(json.loads)
  extents['geometry'] = extents['geometry'].apply(shapely.geometry.Polygon)
  extents = gpd.GeoDataFrame(extents, geometry='geometry') 
  extents.crs = {'init': 'epsg:4326'}
  
  #Find the tiles that intersect the buffered boundary
  #################################################################
  extents['intersects'] = extents['geometry'].intersects(buffered['geometry'][0])
  paths = extents.loc[(extents['intersects']==True)]['path'].tolist()
  if len(paths) == 0:
    return 'No elevation data available for field'
  
  #Read those files in
  #################################################################
  filenames = list()
  for path in paths:
    tile = requests.get(path, allow_redirects=True)
    if tile.status_code != 200:
      return 'Elevation data for field irretrievable'
    filename = path.rsplit('/', 1)[1]
    filenames.append('data/topo/' + filename)
    outfile = open('data/topo/' + filename, 'wb')
    outfile.write(tile.content)
    outfile.close()

  #Process the downloaded tiles
  #################################################################
  #Merge the tiles, then remove them
  if os.path.isfile('data/topo/merged.tif'):
    subprocess.call('rm data/topo/merged.tif', shell=True)
  command = 'gdal_merge.py -q -o data/topo/merged.tif -of GTiff'
  for filename in filenames:
    command = command + ' ' + filename
  subprocess.call(command, shell=True)
  for filename in filenames:
    subprocess.call('rm ' + filename, shell=True)

  #Convert to UTM 16 and remove the merged file
  if os.path.isfile('data/topo/utm.tif'):
    subprocess.call('rm data/topo/utm.tif', shell=True)
  subprocess.call('gdalwarp -q -t_srs EPSG:26916 data/topo/merged.tif data/topo/utm.tif', shell=True)
  subprocess.call('rm data/topo/merged.tif', shell=True)

  #Clip the raster to the buffered boundary and remove the unclipped raster and buffer
  if os.path.isfile('data/topo/elev.tif'):
    subprocess.call('rm data/topo/elev.tif', shell=True)
  #subprocess.call('gdalwarp -q -tr 3 3 -cutline data/rootdata/buffered_boundary.shp -crop_to_cutline data/topo/utm.tif data/topo/elev.tif', shell=True)
  subprocess.call('gdalwarp -q -cutline data/rootdata/buffered_boundary.shp -crop_to_cutline data/topo/utm.tif data/topo/elev.tif', shell=True)
  subprocess.call('rm data/topo/utm.tif', shell=True)

  return 'OK'  
