"""
Salamtea Backend — Server Launch Script
Run with:  python run.py
"""

import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("APP_HOST", os.getenv("HOST", "0.0.0.0")),
        port=int(os.getenv("APP_PORT", os.getenv("PORT", "8000"))),
        reload=os.getenv("APP_RELOAD", "true").lower() == "true",
        log_level="info",
    )
