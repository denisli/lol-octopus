import requests
import time
import json
import random

import feature_vector_extraction

from riot_games_api_key import API_KEY
from riot_games_api_params import *

def get_information_for_matches(players, num_matches, time_interval, match_informations={}):
  '''
  Gets information for matches played by the given list of players.

  In general, we aim to get a single match for each player only, but this is
  not strictly enforced.

  Returns
  -------
  match_informations : Map[int, Map[string, object]]
      mapping from the match id to its information
      The information is another map from the data name to the actual data.
      These data include (name -> value):
      'feature_vectors' -> List[List[float]]
          each value in the list corresponds to a feature vector (which is a
          list of floats)
      'classification' -> int
          0 if blue team wins and 1 if purple team wins
      'timestamp' -> int
          time in milliseconds since epoch
      'duration' -> int
          length in milliseconds of the match
  '''
  match_count = 0
  for player in players:
    # get match references associated with the player
    match_list_request_url = _get_match_list_request_url(str(player))
    match_list = requests.get(match_list_request_url).json()
    time.sleep(1.25) # sleep enough to not exceed rate limit
    if not 'matches' in match_list: continue
    match_references = match_list['matches']
    ranked_match_reference = _find_ranked_match(match_references, match_informations)

    # if there are no matches, then move on to the next player
    if ranked_match_reference == None: continue
    # get a single match detail from the list of references
    match_request_url = _get_match_request_url(str(ranked_match_reference['matchId']))
    match_detail = requests.get(match_request_url).json()
    if 'teams' not in match_detail: continue # skip if there is no team information
    time.sleep(1.25) # sleep enough to not exceed rate limit

    # store information
    feature_vectors = feature_vector_extraction.get_feature_vectors(match_detail, time_interval)
    classification = feature_vector_extraction.get_classification(match_detail)
    match_informations[match_detail['matchId']] = {
      'feature_vectors': feature_vectors,
      'classification': classification,
      'timestamp': ranked_match_reference['timestamp'],
      'duration': match_detail['matchDuration']
    }

    match_count += 1
    print 'Finished processing match', match_count

    # stop once we have enough matches
    if len(match_informations) >= num_matches:
      return match_informations
  print 'There were not enough matches. Oh well. Returning '
  return match_informations

def _find_ranked_match(match_references, match_informations):
  '''
  Finds and returns a ranked match from a list of match references that we
  have not already found.
  '''
  for match_reference in match_references:
    # it is a ranked match
    if match_reference['queue'] == 'RANKED_SOLO_5x5' or match_reference['queue'] == 'TEAM_BUILDER_RANKED_SOLO':
      # only return the match if it was not stored in the match informations
      if not match_reference['matchId'] in match_informations: return match_reference
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
  num_matches = 10000
  time_interval = 30000
  with open('player_ids.json') as json_data:
    players = json.load(json_data)
    players = players[:len(players)/2] # first half is used for training
    # shuffle the players
    random.shuffle(players)
    # get the information from the players
    match_informations = get_information_for_matches(players, num_matches, time_interval)
    # store this information to a json
    with open('match_informations.json', 'w') as fp:
      json.dump(match_informations, fp)