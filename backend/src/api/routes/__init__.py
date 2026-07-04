from .novel import router as novel_router
from .memory import router as memory_router
from .consistency import router as consistency_router
from .character import router as character_router
from .plot import router as plot_router
from .auth import router as auth_router
from .projects import router as projects_router
from .dashboard import router as dashboard_router
from .world_building import router as world_building_router

__all__ = [
    "novel_router",
    "memory_router",
    "consistency_router",
    "character_router",
    "plot_router",
    "auth_router",
    "projects_router",
    "dashboard_router",
    "world_building_router"
]