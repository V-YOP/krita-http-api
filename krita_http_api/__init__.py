import sys
import os.path as path
sys.path.insert(0, path.join(path.dirname(path.abspath(__file__)), 'third_deps'))
sys.path.insert(0, path.dirname(path.dirname(path.abspath(__file__))))
from .krita_http_api import *

