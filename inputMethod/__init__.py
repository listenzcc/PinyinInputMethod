# File: __init__.py
# Package: inputMethod
# Aim: Initial file of the inputMethod package

import os

# Setup dirname of cellDicts and find the cellDicts .json files
_cellDicts_dir = os.path.join(os.path.dirname(__file__), '..', 'cellDicts')

_cellDicts_path = []
for fname in os.listdir(_cellDicts_dir):
    if fname.startswith('_') and fname.endswith('.json'):
        _cellDicts_path.append(os.path.join(_cellDicts_dir, fname))
