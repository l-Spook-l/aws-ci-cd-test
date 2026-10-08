from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.users import router as user_router

app = FastAPI(title="FastAPI AWS Project")


app.include_router(health_router)
app.include_router(user_router)
