import sys

from lightgbm import early_stopping
sys.path.append('../')

import json
import warnings
import argparse
import numpy as np

from tqdm import tqdm

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score,
    recall_score,
    accuracy_score,
    f1_score
)

from utils.read_data import load_data
from utils.smiles2fing import Smiles2Fing
from utils.common import (
    data_split,
    ParameterGrid,
    CV
)

try:
    from xgboost import XGBClassifier
except: 
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "xgboost"])
    from xgboost import XGBClassifier


warnings.filterwarnings('ignore')


def main():
    x, y = load_data()

    params_dict = {
        'min_child_weight': [1, 2, 3, 5],
        'max_depth': [3, 6, 9],
        'gamma': np.linspace(0, 3, 10),
        'objective': ['multi:softmax'],
        'booster': ['gbtree']
    }
    params = ParameterGrid(params_dict)


    result = {}
    result['model'] = {}
    result['precision'] = {}
    result['recall'] = {}
    result['f1'] = {}
    result['accuracy'] = {}

    for p in tqdm(range(len(params))):
        
        result['model']['model'+str(p)] = params[p]
        result['precision']['model'+str(p)] = []
        result['recall']['model'+str(p)] = []
        result['f1']['model'+str(p)] = []
        result['accuracy']['model'+str(p)] = []
        
        for seed_ in range(10):
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, shuffle = True, random_state = seed_)
            
            try:
                model = XGBClassifier(random_state = seed_, **params[p])
            except: 
                model = XGBClassifier(**params[p])
                
            model.fit(x_train, y_train)
            pred = model.predict(x_test)
            
            result['precision']['model'+str(p)].append(precision_score(y_test, pred, average = 'macro'))
            result['recall']['model'+str(p)].append(recall_score(y_test, pred, average = 'macro'))
            result['f1']['model'+str(p)].append(f1_score(y_test, pred, average = 'macro'))
            result['accuracy']['model'+str(p)].append(accuracy_score(y_test, pred))
            
            # r_ = CV(x, 
            #         y, 
            #         XGBClassifier, 
            #         params[p], 
            #         seed = seed_)
            
            # result['precision']['model'+str(p)].append(r_['val_precision'])
            # result['recall']['model'+str(p)].append(r_['val_recall'])
            # result['f1']['model'+str(p)].append(r_['val_f1'])
            # result['accuracy']['model'+str(p)].append(r_['val_accuracy'])
        
    json.dump(result, open('../results/test_results/xgb.json', 'w'))


if __name__ == '__main__':
    main()
