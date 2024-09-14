"""
Initializes and configures the FastAPI application
Sets up the app instance and integrates components like and database connections
"""
from fastapi import FastAPI
from db import engine, Base
from controller import router as api_router
from fastapi.staticfiles import StaticFiles
from models import Athlete, Trainer

# Initialize FastAPI app
StatSync = FastAPI()

# Mount the static directory for serving static files
StatSync.mount("/static", StaticFiles(directory="static"), name="static")

# Include the API router with the routes
StatSync.include_router(api_router)

# Create the database tables
Base.metadata.create_all(bind=engine)

print("Database and tables created successfully.")
