#This file reads all our feature sets and assembles 
#a feature set.

#Imports
import rasterio
import gdal
import numpy as np
import os
import shutil
import subprocess


#This function returns a dict. with point values and location
def return_points():
  #Get all the files to run
  filenames = os.listdir('data/individuals')

  #Run for each file
  point_data = {}  
  for filename in filenames:
    #Open the input raster
    raster = rasterio.open('data/individuals/' + filename)
    array = raster.read(1)

    #Get the index for the min value (the datapoint)
    flat_index = np.argmin(array)
    index = np.unravel_index(flat_index, array.shape)
    
    #Write the data to the dictionary
    key = os.path.splitext(filename)[0]
    point_data[key] = {'index': index, 'value': array[index]}

  return point_data


#This function returns a dict. with buffer arrays
def return_buffers():
  #Get all the files to run
  filenames = os.listdir('data/buffers')

  #Run for each file
  buffers = {}  
  for filename in filenames:
    #Open the input raster
    raster = rasterio.open('data/buffers/' + filename)
    array = raster.read(1)
    
    #Write the data to the dictionary
    key = os.path.splitext(filename)[0]
    buffers[key] = array

  return buffers


def return_topo():
  
  #Define stack
  arrays = list()
  labels = list()

  #Import Elevation
  ##########################
  elev_raster = rasterio.open('data/topo/elev.tif')
  elev = elev_raster.read(1)
  arrays.append(elev)
  labels.append('Elevation')

  #Import Multi-Neighborhood curvatures
  ##########################
  curvlist = os.listdir('data/topo/curvatures')
  for instance in curvlist:
    curve_raster = rasterio.open('data/topo/curvatures/' + instance)
    curve = curve_raster.read(1)
    arrays.append(curve)
    labels.append(os.path.splitext(instance)[0])

  return arrays #, labels


def template(feature_set):

  #Get template data
  raster_shape = feature_set[0].shape
  raster = gdal.Open('data/topo/elev.tif')
  geotrans = raster.GetGeoTransform()
  proj = raster.GetProjection()

  return raster_shape, geotrans, proj

def cleanup():
  if os.path.isfile('data/rootdata/boundary.shp'):
    subprocess.call('rm data/rootdata/boundary.*', shell=True)
  if os.path.isfile('data/rootdata/buffered_boundary.shp'):
    subprocess.call('rm data/rootdata/buffered_boundary.*', shell=True)
  #if os.path.isfile('data/topo/elev.tif'):
    #subprocess.call('rm data/topo/elev.tif', shell=True)
  #if os.path.isdir('data/topo/curvatures/'):
    #shutil.rmtree('data/topo/curvatures')
    #subprocess.call('mkdir data/topo/curvatures/', shell=True)
  if os.path.isdir('data/buffers/'):
    shutil.rmtree('data/buffers/')
    subprocess.call('mkdir data/buffers/', shell=True)
  if os.path.isdir('data/individuals/'):
    shutil.rmtree('data/individuals/')
    subprocess.call('mkdir data/individuals/', shell=True)


