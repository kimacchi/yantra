"""Routers package."""
from .submissions import router as submissions_router
from .compilers import router as compilers_router

__all__ = ["submissions_router", "compilers_router"]
