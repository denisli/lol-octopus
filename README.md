# LoL Octopus

An application that calculates the probability of a team winning in a classic League of Legends match.

![Screenshot](/octopus_screenshot.png)

# Heroku Application

Heroku link: [https://lol-octopus.herokuapp.com/](https://lol-octopus.herokuapp.com/)

Note that the first access to the application [will take some loading time](http://stackoverflow.com/questions/2606190/why-are-my-basic-heroku-apps-taking-two-seconds-to-load).

# How to use this?

As you can see in the Heroku application, there are fields to fill in. Fill in all of information from a currently running game, and then click the button below to see how likely each team is going to win.

# How this works?

The data used by the Octopus was retrieved using the [Riot Games API](https://developer.riotgames.com/api/methods)

The Octopus was pre-trained with match data. For each match, a set of feature vectors derived from it. Each of those feature vectors should classify to the outcome of the match. Training the Octopus was thus as simple as passing the information to a neural network implementation from scikit-learn.

5,000 matches were used for the pre-training of the Octopus. It seems to have a fairly accurate prediction rate. When asked to predict the outcome of the match 3/4 into it, it could correctly predict the final outcome >80% of the time.

The Octopus does not do any training outside of its pre-training. Indeed, most of the files in this repository are simply scripts to get data and train the octopus using the data.

Since the API did not have a method to get random matches, I roughly followed the approach mentioned [here](https://developer.riotgames.com/discussion/community-discussion/show/3EOwmWrz). Admittedly, the matches might not very random.

# Tech

- [Riot Games API](https://developer.riotgames.com/api/methods) for training/testing data retrieval
- [scikit-learn](http://scikit-learn.org/stable/) for probability calculation
- [Flask](http://flask.pocoo.org/) for web server
- [HTML/CSS/JavaScript](https://www.w3.org/wiki/The_web_standards_model_-_HTML_CSS_and_JavaScript) for client-side
- [Heroku](https://www.heroku.com/) for deployment

# Notes

If you want to run the code, the code is missing riot_games_api_key.py. That file only has a variable API_KEY which I set equal to my API key string. I have not included this file for the obvious reason that I do not want to and should not be sharing my API key.
