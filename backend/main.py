import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.core.config import settings
from src.api.routes import novel, memory, consistency, character, plot, auth, projects, dashboard
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

# Health check endpoint
@app.get("/")
async def root():
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

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
        workers=1  # For Windows, keep workers=1 to avoid issues
    )
