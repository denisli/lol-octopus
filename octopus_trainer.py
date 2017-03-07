import requests
import os
import time
import bisect
import json
import cPickle as pickle
import feature_vector_extraction
import matches_fetcher
import octopus

import numpy as np

from riot_games_api_key import API_KEY
from riot_games_api_params import *

def train_octopus(octopus, match_informations):
  '''
  This method works as long as the first two elements of the tuple at feature
  vectors and classification. There can be more than two elements in the tuple
  '''
  # batch together all of the feature vectors and classifications
  feature_vector_batch = reduce(lambda batch, \
    match_id: batch + match_informations[match_id]['feature_vectors'],
    match_informations, [])
  classification_batch = reduce(lambda batch, \
    match_id: batch + [ match_informations[match_id]['classification'], ] * \
      len(match_informations[match_id]['feature_vectors']),
    match_informations, [])

  # train the octopus with those batches
  octopus.train(np.array(feature_vector_batch), np.array(classification_batch))

def test_octopus(octopus, match_informations):
  '''
  Gets the classification rate of the octopus. The octopus' classification is
  what it thinks the outcome will be 3/4 into the match.
  '''
  # go through each match and find the prediction that the octopus makes at
  # 3/4 of the game
  correctly_classified = 0
  total_classified = 0
  for match_id, match_information in match_informations.iteritems():
    feature_vectors, classification, duration = match_information['feature_vectors'], match_information['classification'], match_information['duration']
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
  print 'Created new octopus'
  my_octopus = octopus.Octopus()

  # # train
  with open('match_informations.json') as match_informations_json_data:
    match_informations = json.load(match_informations_json_data)
    print 'Finished loading match information'
    train_octopus(my_octopus, match_informations)
    print 'Finished training octopus'
  
  # store the trained octopus
  pickle_filename = 'octopus3.pkl'
  with open(pickle_filename, 'wb') as octopus_pkl:
    pickle.dump(my_octopus, octopus_pkl)
    print 'Stored octopus in', pickle_filename

  # test
  print 'Testing the octopus'
  with open('player_ids.json') as player_ids_json_data:
    players = json.load(player_ids_json_data)

    # testing parameters
    num_testing_matches = 101
    time_interval = 30000
    testing_players = players[len(players)/2:]

    # test
    match_informations = matches_fetcher.get_information_for_matches(testing_players, num_testing_matches, time_interval)
    rate = test_octopus(my_octopus, match_informations)
    print rate