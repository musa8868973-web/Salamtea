import sys
import os

# Root directory aur backend directory ko Python path me top standard priority par add kar rahe hain
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
backend_dir = os.path.join(root_dir, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.chdir(backend_dir)

try:
    from run import app
except ImportError:
    from backend.run import app