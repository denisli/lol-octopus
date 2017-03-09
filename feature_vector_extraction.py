import json

BLUE_TEAM_ID = 100
PURPLE_TEAM_ID = 200

def get_feature_vectors(match_detail, time_interval):
  '''
  Parameters:
  match_detail : JSON-object
      This JSON-object contains a timeline object. The timeline object then
      contains a list of frame objects and frameInterval value for the number
      of milliseconds between frames. The frame objects then contains a list
      of event objects. The event object contains information relevant to the
      features fetched by this method. The frame objects also contain a map
      from participant ID to a participantFrame object which has the stats for
      the player at a that frame's timestamp.
  time_interval : long
      minimum number of seconds between when the feature vectors are fetched

  Returns
  -------
  feature_vectors : List[List[int]]
      list of feature vectors, where each feature is an int value.
      Each feature vector contains the following features:
      0. time in milliseconds during which the feature vector was retrieved
      **Note the features below need to be added twice per team**
      1. amount of gold on team
      2. amount of cs on the team
      3. number of turrets killed
      4. number of inhibitors killed
      5. number of dragons killed
      6. number of barons killed
      7. number of kills on the team
      8. number of assists on the team
      9. number of deaths on the team
  '''
  # TODO: this is a really long list of feature vectors... we should cut it
  # short in the beginning and then extend to it

  feature_vectors = []
  # timestamp for the vector - also a feature
  feature_vector_timestamp = 0
  # features we care about
  feature_values = \
  { 
    BLUE_TEAM_ID: {
      'gold': 500,
      'cs': 0,
      'turrets_killed': 0,
      'inhibitors_killed': 0,
      'dragons_killed': 0,
      'barons_killed': 0,
      'kills': 0,
      'assists': 0,
      'deaths': 0
    },
    PURPLE_TEAM_ID: {
      'gold': 500,
      'cs': 0,
      'turrets_killed': 0,
      'inhibitors_killed': 0,
      'dragons_killed': 0,
      'barons_killed': 0,
      'kills': 0,
      'assists': 0,
      'deaths': 0
    }
  }

  # get the participants in this game and get the mapping from participant ID
  # to team ID
  participant_ids = []
  participant_id_to_team_id = {}
  if not 'participants' in match_detail: return[] # ignore match if there are no participants
  for participant in match_detail['participants']:
    participant_id, team_id = participant['participantId'], participant['teamId']
    participant_ids.append(participant_id)
    participant_id_to_team_id[participant_id] = team_id

  timeline = match_detail['timeline']
  frames = timeline['frames']
  frame_index = 0
  # loop through each frame
  while frame_index < len(frames):
    frame = frames[frame_index]
    frame_timestamp = frame['timestamp']

    if frame_timestamp > feature_vector_timestamp:
      # store the feature vector we have just finished creating
      feature_vector = _get_feature_vector(feature_vector_timestamp, feature_values)
      feature_vectors.append(feature_vector)
      # populate a new feature vector
      while feature_vector_timestamp < frame_timestamp:
        feature_vector_timestamp += time_interval
      continue # move on to next frame

    # first process players stat's information for the feature vector

    # go through each player to compute the total amount of gold for each
    # team
    participant_frames = frame['participantFrames']
    # remember to set the gold back to 0 so that we do not add over previous
    # frames' gold
    feature_values[BLUE_TEAM_ID]['gold'] = 0
    feature_values[PURPLE_TEAM_ID]['gold'] = 0
    for participant_id in participant_ids:
      participant_frame = participant_frames[str(participant_id)]
      participant_gold = participant_frame['totalGold']
      team_id = participant_id_to_team_id[participant_id]
      feature_values[team_id]['gold'] += participant_gold
    
    events = frame.get('events', [])
    event_index = 0
    # loop through each event in the frame
    while event_index < len(events):
      event = events[event_index]
      event_timestamp = event['timestamp']
      # if we have processed all events for the time interval...
      if event_timestamp > feature_vector_timestamp:
        # store the feature vector we have just finished creating
        feature_vector = _get_feature_vector(feature_vector_timestamp, feature_values)
        feature_vectors.append(feature_vector)
        # populate a new feature vector
        while feature_vector_timestamp < event_timestamp:
          feature_vector_timestamp += time_interval
        continue # try to process this same event again
      # process the event
      if event['eventType'] == 'CHAMPION_KILL':
        killer_id = event['killerId']
        # make sure that the killer is a champion (in case of executions)
        if killer_id in participant_id_to_team_id:
          killer_team = participant_id_to_team_id[killer_id]
          feature_values[killer_team]['kills'] += 1
          feature_values[killer_team]['assists'] += len(event.get('assistingParticipantIds', []))
        victim_team = participant_id_to_team_id[event['victimId']]
        feature_values[victim_team]['deaths'] += 1
        pass 
      elif event['eventType'] == 'BUILDING_KILL':
        killer_team = event['teamId']
        feature_name = _get_associated_feature_name_for_building_type(event['buildingType'])
        if feature_name != None:
          feature_values[killer_team][feature_name] += 1
        pass
      elif event['eventType'] == 'ELITE_MONSTER_KILL':
        killer_id = event['killerId']
        if killer_id != 0: # ignore if a minion somehow killed?
          killer_team = participant_id_to_team_id[killer_id]
          feature_name = _get_associated_feature_name_for_monster_type(event['monsterType'])
          if feature_name != None:
            feature_values[killer_team][feature_name] += 1
          pass
      event_index += 1
    # # processed all events in frame so move on to next
    frame_index += 1
  return feature_vectors

def get_classification(match_detail):
  # blue team winning classifies as 0, purple team winning classifies at 1
  return 0 if match_detail['teams'][0]['winner'] else 1

TIMESTAMP_NORMALIZER = 12.0e5
GOLD_NORMALIZER = 4.0e5
TURRETS_KILLED_NORMALIZER = 20
INHIBITORS_KILLED_NORMALIZER = 20
DRAGONS_KILLED_NORMALIZER = 20
BARONS_KILLED_NORMALIZER = 10
KILLS_NORMALIZER = 200
ASSISTS_NORMALIZER = 1e3
DEATHS_NORMALIZER = 200

def unnormalize_time(time):
  return (time * TIMESTAMP_NORMALIZER) + TIMESTAMP_NORMALIZER

def _get_feature_vector(feature_vector_timestamp, feature_values):
  blue_feature_values, purple_feature_values = feature_values[BLUE_TEAM_ID], feature_values[PURPLE_TEAM_ID]
  return [_normalize(feature_vector_timestamp, TIMESTAMP_NORMALIZER), \
  _normalize(blue_feature_values['gold'], GOLD_NORMALIZER), _normalize(purple_feature_values['gold'], GOLD_NORMALIZER), \
  _normalize(blue_feature_values['turrets_killed'], TURRETS_KILLED_NORMALIZER), _normalize(purple_feature_values['turrets_killed'], TURRETS_KILLED_NORMALIZER), \
  _normalize(blue_feature_values['inhibitors_killed'], INHIBITORS_KILLED_NORMALIZER), _normalize(purple_feature_values['inhibitors_killed'], INHIBITORS_KILLED_NORMALIZER), \
  _normalize(blue_feature_values['dragons_killed'], DRAGONS_KILLED_NORMALIZER), _normalize(purple_feature_values['dragons_killed'], DRAGONS_KILLED_NORMALIZER), \
  _normalize(blue_feature_values['barons_killed'], BARONS_KILLED_NORMALIZER), _normalize(purple_feature_values['barons_killed'], BARONS_KILLED_NORMALIZER), \
  _normalize(blue_feature_values['kills'], KILLS_NORMALIZER), _normalize(purple_feature_values['kills'], KILLS_NORMALIZER), \
  _normalize(blue_feature_values['assists'], ASSISTS_NORMALIZER), _normalize(purple_feature_values['assists'], ASSISTS_NORMALIZER), \
  _normalize(blue_feature_values['deaths'], DEATHS_NORMALIZER), _normalize(purple_feature_values['deaths'], DEATHS_NORMALIZER)]

def unnormalize_feature_vector(feature_vector):
  [time, \
    blue_gold, purple_gold, \
    blue_turrets_killed, purple_turrets_killed, \
    blue_inhibitors_killed, purple_inhibitors_killed, \
    blue_dragons_killed, purple_dragons_killed, \
    blue_barons_killed, purple_barons_killed, \
    blue_kills, purple_kills, \
    blue_assists, purple_assists, \
    blue_deaths, purple_deaths] = feature_vector
  return [_unnormalize(time, TIMESTAMP_NORMALIZER), \
    _unnormalize(blue_gold, GOLD_NORMALIZER), _unnormalize(purple_gold, GOLD_NORMALIZER), \
    _unnormalize(blue_turrets_killed, TURRETS_KILLED_NORMALIZER), _unnormalize(purple_turrets_killed, TURRETS_KILLED_NORMALIZER), \
    _unnormalize(blue_inhibitors_killed, INHIBITORS_KILLED_NORMALIZER), _unnormalize(purple_inhibitors_killed, INHIBITORS_KILLED_NORMALIZER), \
    _unnormalize(blue_dragons_killed, DRAGONS_KILLED_NORMALIZER), _unnormalize(purple_dragons_killed, DRAGONS_KILLED_NORMALIZER), \
    _unnormalize(blue_barons_killed, BARONS_KILLED_NORMALIZER), _unnormalize(purple_barons_killed, BARONS_KILLED_NORMALIZER), \
    _unnormalize(blue_kills, KILLS_NORMALIZER), _unnormalize(purple_kills, KILLS_NORMALIZER), \
    _unnormalize(blue_assists, ASSISTS_NORMALIZER), _unnormalize(purple_assists, ASSISTS_NORMALIZER), \
    _unnormalize(blue_deaths, DEATHS_NORMALIZER), _unnormalize(purple_deaths, DEATHS_NORMALIZER)]

def normalize_feature_vector(feature_vector):
  [time, \
    blue_gold, purple_gold, \
    blue_turrets_killed, purple_turrets_killed, \
    blue_inhibitors_killed, purple_inhibitors_killed, \
    blue_dragons_killed, purple_dragons_killed, \
    blue_barons_killed, purple_barons_killed, \
    blue_kills, purple_kills, \
    blue_assists, purple_assists, \
    blue_deaths, purple_deaths] = feature_vector
  return [_normalize(time, TIMESTAMP_NORMALIZER), \
    _normalize(blue_gold, GOLD_NORMALIZER), _normalize(purple_gold, GOLD_NORMALIZER), \
    _normalize(blue_turrets_killed, TURRETS_KILLED_NORMALIZER), _normalize(purple_turrets_killed, TURRETS_KILLED_NORMALIZER), \
    _normalize(blue_inhibitors_killed, INHIBITORS_KILLED_NORMALIZER), _normalize(purple_inhibitors_killed, INHIBITORS_KILLED_NORMALIZER), \
    _normalize(blue_dragons_killed, DRAGONS_KILLED_NORMALIZER), _normalize(purple_dragons_killed, DRAGONS_KILLED_NORMALIZER), \
    _normalize(blue_barons_killed, BARONS_KILLED_NORMALIZER), _normalize(purple_barons_killed, BARONS_KILLED_NORMALIZER), \
    _normalize(blue_kills, KILLS_NORMALIZER), _normalize(purple_kills, KILLS_NORMALIZER), \
    _normalize(blue_assists, ASSISTS_NORMALIZER), _normalize(purple_assists, ASSISTS_NORMALIZER), \
    _normalize(blue_deaths, DEATHS_NORMALIZER), _normalize(purple_deaths, DEATHS_NORMALIZER)]

def _normalize(value, normalizer):
  return float(value - normalizer) / normalizer

def _unnormalize(value, normalizer):
  return value * normalizer + normalizer

def _get_associated_feature_name_for_building_type(building_type):
  if building_type == 'TOWER_BUILDING':
    return 'turrets_killed'
  elif building_type == 'INHIBITOR_BUILDING':
    return 'inhibitors_killed'
  else:
    return None

def _get_associated_feature_name_for_monster_type(monster_type):
  if monster_type == 'DRAGON':
    return 'dragons_killed'
  elif monster_type == 'BARON_NASHOR':
    return 'barons_killed'
  else:
    return None