import os

from .config import *

if not os.path.exists(WEIGHTS_PATH):
    _script_dir = os.path.dirname(__file__)
    WEIGHTS_PATH = os.path.join(_script_dir, WEIGHTS_PATH)
