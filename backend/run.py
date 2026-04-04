"""Flask application entry point."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import jsonify, request

from app import create_app

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()


def resolve_static_folder() -> str | None:
    """Pick the first valid static directory that contains index.html."""
    backend_dir = Path(__file__).resolve().parent
    candidates = [
        backend_dir / "static",
        backend_dir.parent / "frontend" / "dist",
    ]

    for path in candidates:
        if (path / "index.html").is_file():
            return str(path)
    return None


static_folder = resolve_static_folder()
if static_folder:
    app.static_folder = static_folder
    logger.info("Using static folder: %s", static_folder)
else:
    logger.warning("No static folder found (expected backend/static or frontend/dist).")


@app.before_request
def log_api_request() -> None:
    if request.path.startswith("/api/"):
        logger.info("API request: %s %s", request.method, request.path)


@app.after_request
def log_api_response(response):
    if request.path.startswith("/api/"):
        logger.info("API response: %s %s", response.status_code, request.path)
    return response


@app.get("/api/debug/static-info")
def static_info():
    backend_dir = Path(__file__).resolve().parent
    frontend_dist = backend_dir.parent / "frontend" / "dist"
    backend_static = backend_dir / "static"

    return jsonify(
        {
            "app_static_folder": app.static_folder,
            "paths": {
                "backend_static": {
                    "path": str(backend_static),
                    "exists": backend_static.exists(),
                    "has_index_html": (backend_static / "index.html").is_file(),
                },
                "frontend_dist": {
                    "path": str(frontend_dist),
                    "exists": frontend_dist.exists(),
                    "has_index_html": (frontend_dist / "index.html").is_file(),
                },
            },
            "environment": os.getenv("FLASK_ENV", "development"),
            "database_host": app.config.get("MYSQL_HOST", "not_set"),
        }
    )


@app.get("/")
def api_info():
    return jsonify(
        {
            "message": "Super Idol API is running",
            "status": "success",
            "endpoints": {
                "auth": "/api/auth/*",
                "food": "/api/food/*",
                "exercise": "/api/exercise/*",
                "preferences": "/api/preferences/*",
                "myfavorite": "/api/myfavorite/*",
                "reports": "/api/reports/*",
                "debug": "/api/debug/static-info",
            },
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
