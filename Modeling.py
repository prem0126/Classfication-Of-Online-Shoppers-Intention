#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 19:26:02 2022

@author: premkumar
"""

import numpy as np
import tensorflow as tf
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
import pandas as pd


features = {'numerical' : ['Administrative',
                            'Informational',
                            'ProductRelated',
                            'total_pages_viewed',
                            'Administrative_Duration',
                            'Informational_Duration',
                            'ProductRelated_Duration',
                            'Administrative_%',
                            'Informational_%',
                            'ProductRelated_%',
                            'total_duration',
                            'Administrative_Duration_%',
                            'Informational_Duration_%',
                            'ProductRelated_Duration_%',
                            'Administrative_Duration_avg',
                            'Informational_Duration_avg',
                            'ProductRelated_Duration_avg',
                            'page_values_x_bounce_rate',
                            'BounceRates',
                            'ExitRates',
                            'PageValues',
                            'SpecialDay'],
                
            'categorical' : ['Month',
                              'yearQuarter',
                              'OperatingSystems',
                              'Browser',
                              'Region',
                              'TrafficType',
                              'VisitorType']}


def read_data(balanced_data=True):
    
    if not balanced_data:
        train_data = pd.read_csv('Train_data.csv')
    elif balanced_data:
        train_data = pd.read_csv('balanced_train_data_smote.csv')
        
    test_data = pd.read_csv('Test_data.csv')
    
    return train_data, test_data


    
class NaiveBayes:
    
    def __init__(self, x_train, y_train, categorical_variables, numerical_columns):
        
        self.x_train = x_train
        self.y_train = y_train
        self.categorical_variables = categorical_variables
        self.numerical_columns = numerical_columns
        
        self.categorical_columns = []
        for col in list(x_train.columns):
            prefix = str(col).split('_')[0]
            if prefix in categorical_variables:
                self.categorical_columns.append(col)
        
        #print(self.categorical_columns)
    
    def gaussian_dist(self, x, mean, std):
        
        pdf = (1/(std*np.sqrt(2*np.pi))) * (np.exp(-0.5*((x - mean)/std)**2))
        
        return pdf
    
    def fit(self):
        
        self.means = {}
        self.likelihoods = {}
        self.stds = {}
        self.priors = {}
        for cls in self.y_train.unique():
            self.priors[cls] = len(self.y_train[self.y_train == cls])/len(self.y_train)
            for feature in self.numerical_columns:
                self.means[(feature, cls)] = self.x_train[self.y_train == cls][feature].mean()
                self.stds[(feature, cls)] = self.x_train[self.y_train == cls][feature].std()
            for feature in self.categorical_columns:
                self.likelihoods[(feature, cls)] = (self.x_train[self.y_train == cls][feature].sum() + 1) / self.x_train[feature].sum()

    
    def get_prediction(self, x):
        
        pred = {}
        for cls in self.y_train.unique():
            prior = self.priors[cls]
            pred[cls] = np.log(prior)
            for feature in self.x_train.columns:
                if feature in self.numerical_columns:
                    mean = self.means[(feature, cls)]
                    std = self.stds[(feature, cls)]
                    pred[cls] = pred[cls] + np.log(self.gaussian_dist(x[feature], mean, std))
                elif feature in self.categorical_columns:
                    pred[cls] = pred[cls] + np.log(self.likelihoods[(feature, cls)])
        
        return max(pred, key = pred.get)
    
    def predict(self, samples):
        
        y_pred = [self.get_prediction(row) for _, row in samples.iterrows()]
        return y_pred


class LogisticRegression_C:
    
    def __init__(self, x_train, y_train, learning_rate=1e-6, n_iter=5000,
                 batch_size=500):
        
        self.x_train = x_train
        self.y_train = y_train
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.n_iter = n_iter
    
    def sigmoid(self, x):
        
        x = x.astype(float)
        return 1/(1 + np.exp(-x))
    
    def cost_derivative(self, batch_idx):
        
        x = self.x_train.loc[batch_idx].values
        y = self.y_train.loc[batch_idx]
        derivative = (self.sigmoid(x.dot(self.w)) - y).dot(x)/len(x)
        
        return derivative
    
    def gradient_descent(self):
        
        self.w = np.random.normal(loc = 0, scale = 0.1, size = len(self.x_train.columns))
        index = random.sample(list(self.x_train.index), self.batch_size)
        for i in range(self.n_iter):
            cost_derivative = self.cost_derivative(index)
            self.w -= self.learning_rate * cost_derivative.astype(float)
    
    def train(self):
        
        self.x_train['bias'] = 1 #add bias
        self.gradient_descent()
    
    def predict(self, x):
        
        x['bias'] = 1
        pred = self.sigmoid(x.dot(self.w))
        pred = np.where(pred > 0.5, 1, 0)
        
        return pred

def logistic_regression(x_train, y_train, x_test, y_test):
    
    model = LogisticRegression_C(x_train, y_train)
    model.train()
    
    y_pred = model.predict(x_test)
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    model = LogisticRegression()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    cm = confusion_matrix(y_test, y_pred)
    print(cm)

def NB(x_train, y_train, x_test, y_test):
    
    model = NaiveBayes(x_train, y_train,
                       features['categorical'],
                       features['numerical'])
    model.fit()
    
    y_pred = model.predict(x_test)
    cm = confusion_matrix(y_test, y_pred)
    print(cm)

def random_forest(x_train, y_train, x_test, y_test):
    
    model = RandomForestClassifier()
    model.fit(x_train, y_train)
    
    y_pred = model.predict(x_test)
    cm = confusion_matrix(y_test, y_pred)
    print(cm)

def svm(x_train, y_train, x_test, y_test):
    
    model = SVC(gamma='auto')
    model.fit(x_train, y_train)
    
    y_pred = model.predict(x_test)
    cm = confusion_matrix(y_test, y_pred)
    print(cm)

def XgBoost(x_train, y_train, x_test, y_test):
    
    model = XGBClassifier()
    model.fit(x_train, y_train)
    
    y_pred = model.predict(x_test)
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    

def main():
    
    train_data, test_data = read_data()
    x_train = train_data.drop(columns=['Revenue'])
    y_train = train_data['Revenue']
    x_test = test_data.drop(columns=['Revenue'])
    y_test = test_data['Revenue']
    
    # print('Random Forest')
    #random_forest(x_train, y_train, x_test, y_test)
    # print('SVM')
    #svm(x_train, y_train, x_test, y_test)
    # print('XgBoost')
    #XgBoost(x_train, y_train, x_test, y_test)
    #NB(x_train, y_train, x_test, y_test)
    #logistic_regression(x_train, y_train, x_test, y_test)
    

if __name__ == '__main__':    
    main()