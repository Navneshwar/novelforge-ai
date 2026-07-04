import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.core.config import settings
from src.api.routes import novel, memory, consistency, character, plot, auth, projects, dashboard, world_building
from src.core.database import init_db
import logging
from loguru import logger
import os

# Configure logging
logger.add("logs/app.log", rotation="500 MB", retention="10 days", level="INFO")
logging.basicConfig(level=logging.INFO)

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Novel Writing Assistant with Persistent Memory using Cognee",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(novel.router, prefix="/api/novels", tags=["Novels"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
app.include_router(consistency.router, prefix="/api/consistency", tags=["Consistency"])
app.include_router(character.router, prefix="/api/characters", tags=["Characters"])
app.include_router(plot.router, prefix="/api/plots", tags=["Plots"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(world_building.router, prefix="/api/world", tags=["World Building"])

# API status endpoint (was at "/" — moved so "/" can serve the built frontend
# in production; see the static-file mount at the bottom of this file)
@app.get("/api/status")
async def api_status():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "status": "running",
        "llm_model": settings.LLM_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "service": settings.APP_NAME}

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    logger.info(f"📝 LLM Model: {settings.LLM_MODEL}")
    logger.info(f"🧠 Embedding Model: {settings.EMBEDDING_MODEL}")
    logger.info(f"🔗 API Docs: http://localhost:8000/docs")
    logger.info(f"✅ Server ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"🛑 {settings.APP_NAME} shutting down...")

# --- Serve the built frontend (production only) ---
# In dev, the frontend runs separately under Vite (npm run dev) with its own
# proxy for /api. In production there is no Vite dev server, so if a built
# frontend is present at FRONTEND_DIST_DIR we serve it from this same FastAPI
# process: one process, one URL, no CORS to configure. This block is a no-op
# (skipped entirely) if that directory doesn't exist, so it never interferes
# with local dev where you run `npm run dev` separately.
_FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
_FRONTEND_DIST = os.path.abspath(_FRONTEND_DIST)

if os.path.isdir(_FRONTEND_DIST):
    _ASSETS_DIR = os.path.join(_FRONTEND_DIST, "assets")
    if os.path.isdir(_ASSETS_DIR):
        app.mount("/assets", StaticFiles(directory=_ASSETS_DIR), name="frontend-assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Catch-all for React Router (BrowserRouter uses real paths like
        /novel/123, not hash routes). Any path that isn't /api/*, /docs,
        /redoc, or /health falls through to here and gets index.html, and
        React Router figures out what to render client-side. A real static
        file under dist/ (e.g. favicon.ico) is served directly if present."""
        candidate = os.path.join(_FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(_FRONTEND_DIST, "index.html"))
else:
    logger.warning(
        f"No frontend build found at {_FRONTEND_DIST} — serving API only. "
        "Run `npm run build` in frontend/ before deploying if you want this "
        "process to serve the UI too."
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
        workers=1  # For Windows, keep workers=1 to avoid issues
    )
