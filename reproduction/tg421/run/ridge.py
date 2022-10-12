import sys
sys.path.append('../')

import json
import openpyxl
import warnings
import argparse
import numpy as np

from tqdm import tqdm

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error
)

from utils.read_data import load_data
from utils.smiles2fing import Smiles2Fing
from utils.common import ParameterGrid

from sklearn.linear_model import Ridge

warnings.filterwarnings('ignore')

from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--admin-type', type = str, default = 'oral')
    try:
        args = parser.parse_args()
    except:
        args = parser.parse_args([])
        
    x, y = load_data(args.admin_type)

    params_dict = {
        'alpha': np.linspace(1e-3, 10, 20),
        'normalize': [True, False],
        'tol': np.logspace(-4, -2, 10)
    }
    params = ParameterGrid(params_dict)

    result = {}
    result['model'] = {}
    result['mse'] = {}
    result['rmse'] = {}
    result['mae'] = {}

    for p in tqdm(range(len(params))):
        
        result['model']['model'+str(p)] = params[p]
        result['mse']['model'+str(p)] = []
        result['rmse']['model'+str(p)] = []
        result['mae']['model'+str(p)] = []
        
        for seed_ in range(10):
            x_train, x_test, y_train, y_test = train_test_split(x, y, shuffle = True, random_state = seed_)
            
            try:
                model = Ridge(random_state = seed_, **params[p])
            except: 
                model = Ridge(**params[p])
                
            model.fit(x_train, y_train)
            pred = model.predict(x_test)
            
            result['mse']['model'+str(p)].append(mean_squared_error(y_test, pred))
            result['rmse']['model'+str(p)].append(mean_squared_error(y_test, pred)**0.5)
            result['mae']['model'+str(p)].append(mean_absolute_error(y_test, pred))
            
        
    json.dump(result, open('../results/test_results/ridge.json', 'w'))


if __name__ == '__main__':
    main()

