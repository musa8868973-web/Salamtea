# Compatibility entrypoint for local scripts. Not used by Procfile/gunicorn in production.
from backend.app.main import app  # Re-export the FastAPI app
