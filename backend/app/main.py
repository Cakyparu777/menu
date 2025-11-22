from fastapi import FastAPI
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.models import * # Import all models to ensure they are registered
from app.socket_manager import sio
import socketio

# Create tables
Base.metadata.create_all(bind=engine)

fastapi_app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

from fastapi.middleware.cors import CORSMiddleware

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@fastapi_app.get("/")
def root():
    return {"message": "Welcome to Restaurant Menu API"}

from app.api.api import api_router

fastapi_app.include_router(api_router, prefix=settings.API_V1_STR)

from fastapi.staticfiles import StaticFiles
import os

# Ensure static directory exists
os.makedirs("app/static/images", exist_ok=True)

# Mount static files
fastapi_app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Wrap FastAPI with Socket.IO
app = socketio.ASGIApp(sio, fastapi_app)
