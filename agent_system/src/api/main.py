"""
Sports Quest AI Backend API - Main FastAPI application
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from ..models.database import init_db, get_db
from .routes import users, teams, quests, events, workflow, sync, sportdevs
from ..core.workflow_engine import sports_quest_workflow

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    await init_db()
    
    # Start event scheduler on startup
    from ..services.event_scheduler import start_event_scheduler, stop_event_scheduler
    await start_event_scheduler()
    
    yield
    
    # Stop event scheduler on shutdown
    await stop_event_scheduler()


app = FastAPI(
    title="Sports Quest AI Backend",
    description="AI-powered sports quest generation system with multi-agent architecture",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])  
app.include_router(quests.router, prefix="/api/quests", tags=["quests"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(workflow.router, prefix="/api/workflow", tags=["workflow"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])
app.include_router(sportdevs.router, tags=["sportdevs"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sports Quest AI Backend API",
        "version": "1.0.0",
        "status": "running",
        "agent_system": "OpenAI Agents Python"
    }


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        await db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "agents": "ready"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )