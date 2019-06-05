#Imports
################################################################################
import geopandas

#Import training data
###############################################################################
points = geopandas.read_file('data/rootdata/trainingPoints.shp')

#Import boundary
###############################################################################
boundary = geopandas.read_file('data/rootdata/boundary.shp')



print(boundary['geometry'])
