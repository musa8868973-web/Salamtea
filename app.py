import sys
import os

# backend directory ko Python path me add kar rahe hain
sys.path.insert(0, os.path.abspath("backend"))

from main import app