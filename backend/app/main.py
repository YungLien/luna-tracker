import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import public_config_status
from app.routers import auth, meals, activities, dashboard

app = FastAPI(title="Luna Tracker API")

_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
_allowed_origins = [o.strip() for o in _origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(meals.router)
app.include_router(activities.router)
app.include_router(dashboard.router)


@app.get("/health")
async def health():
    return {"status": "ok", "config": public_config_status()}
