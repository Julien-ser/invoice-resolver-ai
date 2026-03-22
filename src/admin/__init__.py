"""
Admin panel module.

Exposes admin_router for FastAPI application.
"""

from .routes import router as admin_router

__all__ = ["admin_router"]
