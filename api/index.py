import sys
import os

# Set current working directory to 'backend'
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

from run import app