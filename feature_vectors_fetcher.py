import requests
import time
import json

import feature_vector_extraction

from riot_games_api_key import API_KEY
from riot_games_api_params import *

def get_feature_vectors_and_classification_for_matches(players, num_matches, time_interval):
  '''
  Returns a list of feature vectors and classification pairs. Each pair
  corresponds to information from a single match.
  '''
  feature_vectors_and_classification_tuples = []
  match_count = 0
  for player in players:
    # get match references associated with the player
    match_list_request_url = _get_match_list_request_url(str(player))
    match_list = requests.get(match_list_request_url).json()
    time.sleep(1.25) # sleep enough to not exceed rate limit
    if not 'matches' in match_list: continue
    match_references = match_list['matches']
    ranked_match_reference = _find_ranked_match(match_references)

    # if there are no matches, then move on to the next player
    if ranked_match_reference == None: continue
    # get a single match detail from the list of references
    match_request_url = _get_match_request_url(str(ranked_match_reference['matchId']))
    match_detail = requests.get(match_request_url).json()
    if 'teams' not in match_detail: continue # skip if there is no team information
    time.sleep(1.25) # sleep enough to not exceed rate limit

    # get the feature vectors and classification
    feature_vectors = feature_vector_extraction.get_feature_vectors(match_detail, time_interval)
    classification = feature_vector_extraction.get_classification(match_detail)
    feature_vectors_and_classification_tuples.append( (feature_vectors, classification, match_detail['matchDuration']) )

    match_count += 1
    print 'Finished processing match', match_count

    # stop once we have enough matches
    if len(feature_vectors_and_classification_tuples) >= num_matches:
      return feature_vectors_and_classification_tuples
  print 'There were not enough matches. Oh well.'
  return feature_vectors_and_classification_tuples

def _find_ranked_match(match_references):
  for match_reference in match_references:
    if match_reference['queue'] == 'RANKED_SOLO_5x5' or match_reference['queue'] == 'TEAM_BUILDER_RANKED_SOLO':
      return match_reference
  return None

def _get_match_list_request_url(summoner_id):
  end_time = time.time() * 1e3 
  begin_time = end_time - 432000 * 1e3
  request_url = 'https://global.api.pvp.net/api/lol/%s/v2.2/matchlist/by-summoner/%s' % (REGION, summoner_id)
  parameters = '?beginTime=%d&endTime=%d&api_key=%s' % (begin_time, end_time, API_KEY)
  return request_url + parameters

def _get_match_request_url(match_id):
  request_url = 'https://global.api.pvp.net//api/lol/%s/v2.2/match/%s' % (REGION, match_id)
  parameters = '?includeTimeline=True&api_key=%s' % API_KEY
  return request_url + parameters

if __name__ == '__main__':
  with open('player_ids.json') as json_data:
    players = json.load(json_data)
    feature_vectors_and_classification_for_matches = get_feature_vectors_and_classification_for_matches(players, 4, 30000)
    for feature_vectors_and_classification in feature_vectors_and_classification_for_matches:
      print feature_vectors_and_classification