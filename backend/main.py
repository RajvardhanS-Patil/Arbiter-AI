"""
Arbiter AI — Main API Server
Binds backend routes, database migrations, CORS, and hooks orchestrator to WebSockets.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
import database as db_module

# Import routers
from routes.research import router as research_router
from routes.reports import router as reports_router
from routes.sessions import router as sessions_router
from routes.websocket import router as ws_router, manager as ws_manager
from agents.orchestrator import orchestrator_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for DB migration."""
    # Run DB schema creation
    await db_module.init_db()
    
    # Register WebSocket broadcast callback with Orchestrator
    async def ws_broadcast_callback(session_id: str, ws_event: dict):
        await ws_manager.broadcast(session_id, ws_event)
        
    orchestrator_agent.set_ws_broadcast(ws_broadcast_callback)
    
    yield
    # Shutdown logic (none needed for SQLite/FastAPI)


app = FastAPI(
    title="Arbiter AI API",
    description="Fact verification and multi-agent interrogation platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend proxy
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(research_router, prefix="/api/v1", tags=["Research"])
app.include_router(reports_router, prefix="/api/v1", tags=["Reports"])
app.include_router(sessions_router, prefix="/api/v1", tags=["Sessions"])
app.include_router(ws_router, tags=["WebSocket"])


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Arbiter AI",
        "description": "The Court of Truth Awaits. AI models available: " + 
                      ", ".join(settings.available_providers)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.BACKEND_PORT, reload=True)
