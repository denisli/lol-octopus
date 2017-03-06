from flask import Flask
from flask import request
from flask import jsonify

import cPickle as pickle
import json
import numpy as np

import feature_vector_extraction

with open('octopus.pkl', 'rb') as octopus_pkl:
  octopus = pickle.load(octopus_pkl)

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
  return app.send_static_file('index.html')

@app.route('/predict', methods=['GET',])
def predict():
  time = int(request.args.get('time'))
  blue_gold = int(request.args.get('blueGold'))
  purple_gold = int(request.args.get('purpleGold'))
  blue_turrets_killed = int(request.args.get('blueTurretsKilled'))
  purple_turrets_killed = int(request.args.get('purpleTurretsKilled'))
  blue_inhibitors_killed = int(request.args.get('blueInhibitorsKilled'))
  purple_inhibitors_killed = int(request.args.get('purpleInhibitorsKilled'))
  blue_dragons_killed = int(request.args.get('blueDragonsKilled'))
  purple_dragons_killed = int(request.args.get('purpleDragonsKilled'))
  blue_barons_killed = int(request.args.get('blueBaronsKilled'))
  purple_barons_killed = int(request.args.get('purpleBaronsKilled'))
  blue_kills = int(request.args.get('blueKills'))
  purple_kills = int(request.args.get('purpleKills'))
  blue_assists = int(request.args.get('blueAssists'))
  purple_assists = int(request.args.get('purpleAssists'))
  blue_deaths = int(request.args.get('blueDeaths'))
  purple_deaths = int(request.args.get('purpleDeaths'))

  feature_vector = [time, \
    blue_gold, purple_gold, \
    blue_turrets_killed, purple_turrets_killed, \
    blue_inhibitors_killed, purple_inhibitors_killed, \
    blue_dragons_killed, purple_dragons_killed, \
    blue_barons_killed, purple_barons_killed, \
    blue_kills, purple_kills, \
    blue_assists, purple_assists, \
    blue_deaths, purple_deaths]

  normalized_feature_vector = feature_vector_extraction.normalize_feature_vector(feature_vector)
  
  proba = octopus.predict_proba(np.array(normalized_feature_vector).reshape((1, -1)))
  return jsonify(blueWinProbability=proba[0][0], purpleWinProbability=proba[0][1])

if __name__ == '__main__':
	app.run()
