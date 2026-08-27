import sys
import os

# Absolute path resolution for Vercel & local VS Code
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from run import app