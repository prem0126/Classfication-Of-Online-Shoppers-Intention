#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 16:15:26 2022

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
from sklearn.metrics import precision_score, recall_score
import pandas as pd
import json

#from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV


def read_dataset(dataset_type):
    assert dataset_type in ['Unbalanced', 'Smote', 'Rbo']
    
    if dataset_type == 'Unbalanced':
        train_data = pd.read_csv('Train_data.csv')
    elif dataset_type == 'Smote':
        train_data = pd.read_csv('balanced_train_data_smote.csv')
    elif dataset_type == 'Rbo':
        train_data = pd.read_csv('balanced_train_data_rbo.csv')
        
    test_data = pd.read_csv('Test_data.csv')
    
    return train_data, test_data

def evaluate(model, x_train, y_train, x_test, y_test):
    
    #Evaluate Test set
    y_pred = model.predict(x_test)
    cm_test = confusion_matrix(y_test, y_pred)
    precision_test = precision_score(y_test, y_pred)
    recall_test = recall_score(y_test, y_pred)
    
    #Evaluate Train set
    y_pred = model.predict(x_train)
    cm_train = confusion_matrix(y_train, y_pred)
    precision_train = precision_score(y_train, y_pred)
    recall_train = recall_score(y_train, y_pred)
    
    result = {'train' : {'cm' : cm_train.tolist(),
                         'precision' : precision_train.tolist(),
                         'recall' : recall_train.tolist()},
              'test' : {'cm' : cm_test.tolist(),
                        'precision' : precision_test.tolist(),
                        'recall' : recall_test.tolist()}}
    
    return result

def RandomForest(x_train, y_train, x_test, y_test):
    
    with open('MDI_features.json', 'r') as file:
        features_selected = json.load(file)
    file.close()
    
    #Subsetting features selected using MDI method
    x_train = x_train[x_train.columns.intersection(features_selected)]
    x_test = x_test[x_test.columns.intersection(features_selected)]
    
    n_estimators = [int(x) for x in np.linspace(start = 200, stop = 1000, num = 10)] #Number of trees
    max_features = ['sqrt', 'log2'] #Num of features to consider at every split
    max_depth = [int(x) for x in np.linspace(10, 100, num = 11)] #Max num of levels in a tree
    max_depth.append(None)
    min_samples_split = [2, 5, 10, 20, 30] #Min num of samples required to split a node
    min_samples_leaf = [1, 2, 4] #Min num of samples required at each leaf
    bootstrap = [True, False] #Selecting samples
    
    param_grid = {'bootstrap': [True],
                'max_depth': [80, 90, 100, 110],
                'max_features': [2, 3],
                'min_samples_leaf': [3, 4, 5],
                'min_samples_split': [8, 10, 12],
                'n_estimators': [100, 200, 300, 1000]}
    
    model = RandomForestClassifier()
    model_grid = GridSearchCV(estimator=model,
                                param_grid=param_grid, 
                                cv=3,
                                n_jobs=-1,
                                verbose=2)
    
    model_grid.fit(x_train, y_train)
    
    best_params = model_grid.best_params_
    with open('RandomForest_bestparams.json', 'w') as file:
        json.dump(best_params, file)
    file.close()
    
    best_model = model_grid.best_estimator_
    best_model.fit(x_train, y_train)
    
    result = evaluate(best_model, x_train, y_train, x_test, y_test)
    
    return result
    
def svm(x_train, y_train, x_test, y_test):
    
    with open('mRMR_features.json', 'r') as file:
        features_selected = json.load(file)
    file.close()
    
    #Subsetting features selected using MDI method
    x_train = x_train[x_train.columns.intersection(features_selected)]
    x_test = x_test[x_test.columns.intersection(features_selected)]
    
    param_grid = {'C': [0.1, 1, 10, 100],
                  'gamma': [1, 0.1, 0.01, 0.001],
                  'kernel': ['rbf', 'poly', 'sigmoid']}
    
    model = SVC()
    model_grid = GridSearchCV(estimator=SVC(),
                              param_grid=param_grid,
                              refit=True,verbose=2,
                              n_jobs=-1, cv=3)
    model_grid.fit(x_train, y_train)
    
    best_params = model_grid.best_params_
    with open('SVM_bestparams.json', 'w') as file:
        json.dump(best_params, file)
    file.close()
    
    best_model = model_grid.best_estimator_
    best_model.fit(x_train, y_train)
    
    result = evaluate(best_model, x_train, y_train, x_test, y_test)
    
    return result

def xgboost(x_train, y_train, x_test, y_test):
    
    with open('mRMR_features.json', 'r') as file:
        features_selected = json.load(file)
    file.close()
    
    #Subsetting features selected using MDI method
    x_train = x_train[x_train.columns.intersection(features_selected)]
    x_test = x_test[x_test.columns.intersection(features_selected)]
    
    param_grid = {'max_depth' : [3,6,10],
                  'learning_rate' : [0.01, 0.05, 0.1],
                  'n_estimators' : [60, 100, 200]}
        
    model = XGBClassifier()
    model_grid = GridSearchCV(estimator=model,
                            param_grid=param_grid,
                            scoring = 'roc_auc',
                            n_jobs = -1,
                            cv = 3,
                            verbose=2)
    model_grid.fit(x_train, y_train)
    
    best_params = model_grid.best_params_
    with open('XGboost_bestparams.json', 'w') as file:
        json.dump(best_params, file)
    file.close()
    
    best_model = model_grid.best_estimator_
    best_model.fit(x_train, y_train)
    
    result = evaluate(best_model, x_train, y_train, x_test, y_test)
    
    return result
    

def main():
    
    train_smote, test_smote = read_dataset('Smote')
    x_train_smote = train_smote.drop(columns=['Revenue'])
    y_train_smote = train_smote['Revenue']
    x_test_smote = test_smote.drop(columns=['Revenue'])
    y_test_smote = test_smote['Revenue']
    
    rf_result_smote = RandomForest(x_train_smote, y_train_smote,
                                   x_test_smote, y_test_smote)
    
    svm_result_smote = svm(x_train_smote, y_train_smote,
                           x_test_smote, y_test_smote)
    
    xgboost_result_smote = xgboost(x_train_smote, y_train_smote,
                           x_test_smote, y_test_smote)
    
    smote_result = {'Random Forest' : rf_result_smote,
                    'Svm' : svm_result_smote,
                    'XGboost' : xgboost_result_smote}
    
    with open('Finetuned_models_smote.json', 'w') as file:
        json.dump(smote_result, file)
    file.close()    
    
    

if __name__ == '__main__':
    main()