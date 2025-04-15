"""
API package for the RosBag Cockpit application.
This package contains all the API routes, models, and utilities for the application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .exception_handlers import register_exception_handlers
from .routes import router as api_router

# Create FastAPI app instance

app = FastAPI(
    title="RosBag Cockpit API",
    description="API for managing and analyzing ROS bag files",
    version="0.1.0",
)
register_exception_handlers(app)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)


# Function to get the app instance (useful for testing)
def get_app():
    return app
