#Imports
################################################################################
import geopandas

#Import training data
###############################################################################
points = geopandas.read_file('data/rootdata/trainingPoints.shp')
print(points.crs)
points = points.to_crs({'init': 'epsg:26916'})
print(points.crs)
points.to_file('data/rootdata/trainingPoints.shp')

#Import boundary
###############################################################################
boundary = geopandas.read_file('data/rootdata/boundary.shp')
print(boundary.crs)
boundary = boundary.to_crs({'init': 'epsg:26916'})
print(boundary.crs)
boundary.to_file('data/rootdata/boundary.shp')



print(boundary['geometry'])
