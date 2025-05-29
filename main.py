"""
FastAPI application main entry point.
Configures the application, includes routers, and sets up middleware.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

# Import configuration and models
from app.config.database import create_tables, engine
from app.routes.user_routes import user_router
from app.routes.post_routes import post_router

# Import models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.post import Post

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events for database initialization.
    
    Args:
        app: FastAPI application instance
    """
    # Startup events
    logger.info("Starting up the application...")
    
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    yield
    
    # Shutdown events
    logger.info("Shutting down the application...")
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application instance
app = FastAPI(
    title="Lucid Task API",
    description="FastAPI application with MVC pattern, JWT authentication, and MySQL database",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Global HTTP exception handler.
    Provides consistent error response format.
    
    Args:
        request: HTTP request object
        exc: HTTP exception to handle
        
    Returns:
        JSONResponse: Formatted error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    Provides generic error response for unexpected errors.
    
    Args:
        request: HTTP request object
        exc: Exception to handle
        
    Returns:
        JSONResponse: Generic error response
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500
        }
    )


# Include routers
app.include_router(user_router)
app.include_router(post_router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing API information.
    
    Returns:
        dict: API welcome message and available endpoints
    """
    return {
        "message": "Lucid Task API",
        "version": "1.0.0",
        "endpoints": {
            "signup": "/api/users/signup",
            "login": "/api/users/login",
            "add_post": "/api/posts/add",
            "get_posts": "/api/posts/get",
            "delete_post": "/api/posts/delete"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Application health status
    """
    return {
        "status": "healthy",
        "service": "Lucid Task API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    """
    Development server entry point.
    Run the application with uvicorn for development.
    """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )