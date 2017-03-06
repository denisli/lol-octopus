import requests
import os
import time
import bisect
import json
import cPickle as pickle
import feature_vector_extraction
import feature_vectors_fetcher
import octopus

import numpy as np

from riot_games_api_key import API_KEY
from riot_games_api_params import *

def train_octopus(octopus, feature_vectors_and_classification_for_matches):
  '''
  This method works as long as the first two elements of the tuple at feature
  vectors and classification. There can be more than two elements in the tuple
  '''
  # batch together all of the feature vectors and classifications
  feature_vector_batch = reduce(lambda batch, \
    feature_vectors_and_classification: batch + feature_vectors_and_classification[0],
    feature_vectors_and_classification_for_matches, [])
  classification_batch = reduce(lambda batch, \
    feature_vectors_and_classification: batch + [ feature_vectors_and_classification[1], ] * \
      len(feature_vectors_and_classification[0]),
    feature_vectors_and_classification_for_matches, [])

  # train the octopus with those batches
  octopus.train(np.array(feature_vector_batch), np.array(classification_batch))

def test_octopus(octopus, feature_vectors_and_classification_for_matches):
  '''
  Gets the classification rate of the octopus. The octopus' classification is
  what it thinks the outcome will be 3/4 into the match.
  '''
  # go through each match and find the prediction that the octopus makes at
  # 3/4 of the game
  correctly_classified = 0
  total_classified = 0
  for (feature_vectors, classification, duration) in feature_vectors_and_classification_for_matches:
    # search for the feature vector at 3/4 time (or the first one after 3/4 time)
    desired_timestamp = (3 * duration * 1000) / 4
    # unnormalize the time in the feature vectors
    feature_vector_timestamps = map(lambda feature_vector: feature_vector_extraction.unnormalize_time(feature_vector[0]),
      feature_vectors)
    # search amongst these timestamps to get the index
    desired_index = bisect.bisect_left(feature_vector_timestamps, desired_timestamp)
    # just in case desired_index is too high, we just ignore this game
    if desired_index >= len(feature_vector_timestamps): continue

    # classify and see whether or not it is correct
    feature_vector = np.array(feature_vectors[desired_index])
    octopus_classification = octopus.classify(feature_vector.reshape((1, -1)))
    if octopus_classification == classification: correctly_classified += 1
    print octopus_classification, classification
    total_classified += 1
  return float(correctly_classified) / total_classified

if __name__ == '__main__':
  pickle_filename = 'octopus.pkl'

  # create octopus from pickle if possible
  if os.path.isfile(pickle_filename):
    with open(pickle_filename, 'rb') as octopus_pkl:
      print 'Creating octopus from pickle'
      my_octopus = pickle.load(octopus_pkl)
  # if there is no pickle file already, then just create a new one
  else:
    print 'Could not find pickle file. Creating new octopus'
    my_octopus = octopus.Octopus()

  with open('player_ids.json') as json_data:
    players = json.load(json_data)

    # parameters
    num_training_matches = 500
    num_testing_matches = 100
    time_interval = 30000
    training_players = players[:len(players)/2]
    testing_players = players[len(players)/2:]

    # train
    feature_vectors_and_classification_for_matches = feature_vectors_fetcher.get_feature_vectors_and_classification_for_matches(training_players, num_training_matches, time_interval)
    train_octopus(my_octopus, feature_vectors_and_classification_for_matches)
    
    with open('octopus.pkl', 'wb') as octopus_pkl:
      pickle.dump(my_octopus, octopus_pkl)
    
    # test
    feature_vectors_and_classification_for_matches = feature_vectors_fetcher.get_feature_vectors_and_classification_for_matches(testing_players, num_testing_matches, time_interval)
    rate = test_octopus(my_octopus, feature_vectors_and_classification_for_matches)
    print rate
