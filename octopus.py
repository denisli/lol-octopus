from sklearn.neural_network import MLPClassifier
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn import svm
import numpy as np
import json
import feature_vector_extraction

class Octopus(object):
  def __init__(self):
    self.clf = MLPClassifier(max_iter=1000, hidden_layer_sizes=(200,), random_state=1) #MLPClassifier(hidden_layer_sizes=(10,2), alpha=1e-5, max_iter = 10000, batch_size=1000, random_state=1)
  def train(self, feature_vectors_batch, classifications_batch):
    self.clf.fit(feature_vectors_batch, classifications_batch)
  def predict_proba(self, feature_vector):
    return self.clf.predict_proba(feature_vector)
  def classify(self, feature_vector):
    proba = self.predict_proba(feature_vector)
    return 0 if proba[0][0] > 0.5 else 1