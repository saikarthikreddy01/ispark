"""Backward-compatible import shim.

The unified hackathon application lives in :mod:`backend.app`. Older commands
that still import ``backend.server:app`` are redirected to the same focused
FastAPI instance; no legacy hard-coded academic response logic remains here.
"""

from backend.app import app

__all__ = ["app"]
