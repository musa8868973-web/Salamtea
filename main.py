# Expose the FastAPI app for gunicorn to import as "main:app"
# This forwards to the application package under backend/app

from backend.app.main import app  # backend.app.main defines the FastAPI instance
