import numpy as py
import pandas as pd
import json
import pickle
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import classification_report

class LogisticRegression:
    def __init__(self, learnrate, iteration):
        self.learnrate = learnrate
        self.iteration = iteration
    def sigmoid(self, z):
        p = 1 / (1 + py.exp(-z))
        return p
    def fit(self, X, y):
        self.m, self.n = X.shape
        self.w = py.zeros(self.n)
        self.b = 0
        for _ in range(self.iteration):
            z = py.dot(X, self.w) + self.b
            y_pred = self.sigmoid(z)
            # lossfunction
            dw = (1 / self.m) * py.dot(X.T, (y_pred - y))
            db = (1 / self.m) * sum(y_pred - y)
            # reduce w and b
            self.w -= self.learnrate * dw
            self.b -= self.learnrate * db
    def predict_prob(self, X):
            z = py.dot(X, self.w) + self.b
            return self.sigmoid(z)
    def predict(self, X):
        prob = self.predict_prob(X)
        return [1 if i > 0.5 else 0 for i in prob]
