#This file makes predictions for ll desired experimental cases

#Imports
import stack
import export_functions
import metrics
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import RandomForestRegressor
import time

def predict():
  overall_start = time.time() 
 
  #Retrieve feature data and raster template
  #############################################################
  topo_data = stack.return_topo()
  point_data = stack.return_points()
  buffer_data = stack.return_buffers()
  raster_shape, geotrans, proj = stack.template(topo_data)

  #Make predictions
  #############################################################
  print('\n - Making Predictions')

  start = time.time()
  print('\n   RF w/ combined dataset')
  predictions = map_predictions(point_data, topo_data, buffer_data, True, True, True)
  export_functions.output_tif(predictions, raster_shape, geotrans, proj, 'RFCombined.tif')
  print('   Process time: ', time.time() - start)

  start = time.time()
  print('\n   RF w/ topo only')
  predictions = map_predictions(point_data, topo_data, buffer_data, True, True, False)
  export_functions.output_tif(predictions, raster_shape, geotrans, proj, 'RFTopo.tif')
  print('   Process time: ', time.time() - start)

  start = time.time()
  print('\n   RF w/ spatial postion only')
  predictions = map_predictions(point_data, topo_data, buffer_data, True, False, True)
  export_functions.output_tif(predictions, raster_shape, geotrans, proj, 'RFSpatial.tif')
  print('   Process time: ', time.time() - start)

  print('\n   ET w/ combined dataset')
  predictions = map_predictions(point_data, topo_data, buffer_data, False, True, True)
  export_functions.output_tif(predictions, raster_shape, geotrans, proj, 'ETCombined.tif')
  print('   Process time: ', time.time() - start)

  start = time.time()
  print('\n   ET w/ topo only')
  predictions = map_predictions(point_data, topo_data, buffer_data, False, True, False)
  export_functions.output_tif(predictions, raster_shape, geotrans, proj, 'ETTopo.tif')
  print('   Process time: ', time.time() - start)

  start = time.time()
  print('\n   ET w/ spatial postion only')
  predictions = map_predictions(point_data, topo_data, buffer_data, False, False, True)
  export_functions.output_tif(predictions, raster_shape, geotrans, proj, 'ETSpatial.tif')
  print('   Process time: ', time.time() - start)

  print('   Overall: ', time.time() - overall_start)
  

def map_predictions(point_data, topo, buffers, useRF, includeTopo, includeBuffers):
  
  #Define iterables
  #############################################################
  points = list(point_data.keys())
  training_buffers = points
  
  #Assemble the training set
  #############################################################
  training_set = list()
  for training_point in points:
    obs = list()

    if includeTopo:
      for feature in topo:
        obs.append(feature[point_data[training_point]['index']])

    if includeBuffers:
      for buffer_feature in training_buffers:
        obs.append(buffers[buffer_feature][point_data[training_point]['index']])

    obs.append(point_data[training_point]['value'])
    training_set.append(obs)

  print('      Length of feature set: ', len(training_set[0]))
  
  #Assemble the prediction set
  #############################################################
  feature_set = []

  if includeTopo:
    feature_set.extend(topo)

  if includeBuffers:
    for buffer_feature in training_buffers:
      feature_set.append(buffers[buffer_feature])

  print('      Length of feature set: ', len(feature_set))

  #Transform feature_set into 1-d lists
  #############################################################
  raster_shape = feature_set[0].shape
  stack = np.zeros(shape=((raster_shape[0]*raster_shape[1]), len(feature_set)))
  index = 0
  #Loop through all 3 dimensions
  for i in range(raster_shape[0]):
    for j in range(raster_shape[1]):
      for feature_index in range(len(feature_set)):
        #Assign values to the 2-d stack from the 3-d array set
        stack[index, feature_index] = feature_set[feature_index][i,j]
      index += 1

  #Generate Predictions
  #############################################################
  predictions = train_predict(training_set, stack.tolist(), useRF) 
  return predictions    

###############################################################
def train_predict(training_set, prediction_set, useRF):


  #Split the datasets into feature and value sets
  training_values = [row[-1] for row in training_set]
  training_features = [row[0:-1] for row in training_set]

  #Define the regressor parameters
  if useRF:
    print('      Random Forest')
    forest = RandomForestRegressor(max_depth=4, n_estimators=2000, min_samples_leaf=4, max_features=.5)
  
  else: 
    print('      Extra Trees')
    forest = ExtraTreesRegressor(max_depth=4, n_estimators=4000, min_samples_leaf=4, max_features=.5)

  #Fit the forest to the training data
  forest.fit(training_features, training_values)

  #Retrieve the feature importances
  #importances = pd.DataFrame(forest.feature_importances_, index = layers, columns = ['importance']).sort_values('importance', ascending=False)
  #print(importances.to_string())

  #Feed in the raw dataset feature to predict continous values
  predictions = forest.predict(prediction_set).tolist()

  return predictions

predict()
