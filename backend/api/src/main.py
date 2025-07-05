"""
FastAPI application entry point for the TaskGPT API.

This module sets up the FastAPI application with all necessary routers
and initializes the database connection.
"""

from fastapi import FastAPI
from controllers import task_controller, user_controller
from utils.database import init_db

app: FastAPI = FastAPI()

init_db()

app.include_router(task_controller.router, prefix="/tasks", tags=["Tasks"])
app.include_router(user_controller.router, prefix="/users", tags=["Users"])

