# File: __init__.py
# Package: inputMethod
# Aim: Initial file of the inputMethod package

import os

# Setup dirname of cellDicts and find the cellDicts .json files
_cellDict_dir = os.path.join(os.path.dirname(__file__), '..', 'cellDicts')

_cellDict_path = os.path.join(_cellDict_dir, 'merged.json')
