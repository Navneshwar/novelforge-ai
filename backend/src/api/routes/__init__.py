from .novel import router as novel_router
from .memory import router as memory_router
from .consistency import router as consistency_router
from .character import router as character_router

__all__ = [
    "novel_router",
    "memory_router",
    "consistency_router",
    "character_router"
]