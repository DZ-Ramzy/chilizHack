#!/usr/bin/env python3
"""
Sports Quest AI Backend - Main Application Entry Point

A production-ready FastAPI application with multi-agent architecture
for AI-powered sports quest generation with ESPN API integration.
"""
import uvicorn
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
load_dotenv()

def setup_logging():
    """Configure logging for the application"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Configure loguru
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Log to file in production
    if os.getenv("ENVIRONMENT", "development") == "production":
        logger.add(
            "logs/sports_quest_ai.log",
            rotation="1 day",
            retention="30 days",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        )

def validate_environment():
    """Validate required environment variables"""
    required_vars = [
        "SPORTDEVS_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file and ensure all required variables are set")
        sys.exit(1)
    
    logger.info("✅ Environment validation passed")

async def initialize_database():
    """Initialize database if needed"""
    try:
        from src.core.init_data import initialize_sample_data
        
        # Check if database exists and has data
        db_path = Path("sports_quest.db")
        if not db_path.exists():
            logger.info("🗄️  Database not found, initializing with sample data...")
            await initialize_sample_data()
            logger.info("✅ Database initialized successfully")
        else:
            logger.info("🗄️  Database found, skipping initialization")
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Don't exit - let the app start even if DB init fails
        logger.warning("⚠️  Continuing without database initialization")

def create_app():
    """Create and configure the FastAPI application"""
    from src.api.main import app
    return app

def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logging()
        logger.info("🚀 Starting Sports Quest AI Backend")
        
        # Validate environment
        validate_environment()
        
        # Initialize database
        asyncio.run(initialize_database())
        
        # Get configuration
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", 8000))
        environment = os.getenv("ENVIRONMENT", "development")
        reload = environment == "development"
        
        logger.info(f"🌐 Server configuration:")
        logger.info(f"   Host: {host}")
        logger.info(f"   Port: {port}")
        logger.info(f"   Environment: {environment}")
        logger.info(f"   Reload: {reload}")
        
        # Create FastAPI app
        app = create_app()
        
        # Start server
        logger.info("🎯 Starting uvicorn server...")
        if reload:
            # Use import string for reload mode
            uvicorn.run(
                "src.api.main:app",
                host=host,
                port=port,
                reload=reload,
                log_level=os.getenv("LOG_LEVEL", "info").lower(),
                access_log=True
            )
        else:
            # Use app object for production
            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=reload,
                log_level=os.getenv("LOG_LEVEL", "info").lower(),
                access_log=True
            )
        
    except KeyboardInterrupt:
        logger.info("👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()