import requests
import time
import json

from riot_games_api_key import API_KEY
from riot_games_api_params import *

def get_players(initial_set, size):
  '''
  Parameters
  -------
  initial_set : Set[int]
      set of initial player ids from which we walk from to get our players
  size : int
      total number of players we want to get back
  Returns
  -------
  players : Set[int]
      set of player ids where the set is the specified size
  '''
  # copy the initial set to work off of it
  players = set(initial_set) # assume that size >> initial_set size

  # initialize stack of players
  player_stack = []
  for player in initial_set:
    player_stack.append(player)
  
  # until we run out of players keep searching for players to add
  num_requests = 0
  while player_stack:
    player = player_stack.pop()
    # look at the the recent games this player has played against to get
    # involved players
    recent_games_request_url = _get_recent_games_request_url(str(player))
    res = requests.get(recent_games_request_url)
    recent_games_dto = res.json()
    num_requests += 1
    print 'Made request', num_requests, ', currently have this many players', len(players)
    time.sleep(1.25) # sleep at a rate that allows us to not be rate limited

    if not 'games' in recent_games_dto: continue # skip if there are no games...?
    for game_dto in recent_games_dto['games']:
      if not _care_about_game(game_dto): continue # skip games we don't care about
      # otherwise, we add the players to involved
      for player_dto in game_dto['fellowPlayers']:
        involved_player = player_dto['summonerId']
        if not involved_player in players:
          players.add(involved_player)
          player_stack.append(involved_player)
          if len(players) >= size: return list(players)
  print 'Failed to find other players. Stopping early with', len(players), 'num players'
  return list(players) # apparently there aren't enough connected players

def _care_about_game(game_dto):
  # check that the game was created in the past 3 days
  if game_dto['createDate'] < time.time() * 1e3 - 259200 * 1e3: return False
  # check that it is classic
  if game_dto['gameMode'] != 'CLASSIC': return False
  # check that it is a matched game
  if game_dto['gameType'] != 'MATCHED_GAME': return False
  # check that it is ranked solo 5x5
  if game_dto['subType'] != GAME_SUB_TYPE: return False
  # check that it has a field for 'fellowPlayers'
  if not 'fellowPlayers' in game_dto: return False
  # everything is good at this point!
  return True

def _get_recent_games_request_url(summoner_id):
  request_url = 'https://global.api.pvp.net/api/lol/%s/v1.3/game/by-summoner/%s/recent' % (REGION, summoner_id)
  parameters = '?api_key=%s' % API_KEY
  return request_url + parameters

if __name__ == '__main__':
  # branching off with
  # http://www.lolking.net/summoner/na/44947248/dlordtard#matches
  initial_set = set([44947248])
  players = get_players(initial_set, 1e5)
  with open('player_ids.json', 'w') as fp:
    json.dump(players, fp)