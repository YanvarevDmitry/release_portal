from fastapi import FastAPI
from app.routers import admin_router, profile_router, releases_router

app = FastAPI()

app.include_router(admin_router.router)
app.include_router(profile_router.router)
app.include_router(releases_router.router)
