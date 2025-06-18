from fastapi import FastAPI
from backend.api.controllers import task_controller, user_controller
from backend.api.utils.database import init_db

app = FastAPI()

init_db()

app.include_router(task_controller.router, prefix="/tasks", tags=["Tasks"])
app.include_router(user_controller.router, prefix="/users", tags=["Users"])

