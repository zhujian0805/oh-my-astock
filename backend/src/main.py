"""
FastAPI backend for oh-my-astock
Provides REST API for Chinese stock market data access using DuckDB
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from .config import settings
from .database import db_service
from .routers import stocks

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting oh-my-astock backend...")
    try:
        await db_service.connect()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down oh-my-astock backend...")
    await db_service.close()

# Create FastAPI app
app = FastAPI(
    title="oh-my-astock API",
    description="RESTful API for accessing Chinese stock market data from DuckDB database",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Referrer Policy middleware to fix strict-origin-when-cross-origin CORS issues
@app.middleware("http")
async def add_referrer_policy_header(request, call_next):
    """Add Referrer-Policy header to fix CORS issues with strict-origin-when-cross-origin"""
    response = await call_next(request)
    response.headers["Referrer-Policy"] = "origin-when-cross-origin"
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db_healthy = await db_service.is_healthy()
        status = "ok" if db_healthy else "degraded"

        return {
            "status": status,
            "timestamp": None,  # Will be set by FastAPI
            "database_connected": db_healthy
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# Include routers
app.include_router(stocks.router, prefix="/api", tags=["stocks"])

@app.get("/api/docs")
async def api_docs():
    """API documentation endpoint"""
    return {
        "title": "Stock Market Data API",
        "version": "0.1.0",
        "description": "RESTful API for accessing Chinese stock market data from DuckDB database",
        "endpoints": {
            "GET /api/health": "Health check endpoint",
            "GET /api/stocks": "Get all available stocks",
            "GET /api/stocks/{code}/historical": "Get historical data for a stock",
            "GET /api/market/sse-summary": "Get Shanghai Stock Exchange summary data"
        },
        "documentation": "See README.md for detailed API documentation"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )
