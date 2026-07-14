"""
Entry point kept at the top level so `uvicorn main:app` (and the Azure Web App
deployment, which runs from this directory) continues to work unchanged.
The actual application lives in app/main.py.
"""

from app.main import app

__all__ = ["app"]
