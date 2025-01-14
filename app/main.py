from fastapi import FastAPI
from routers import admin_router, releases_router

app = FastAPI()

app.include_router(admin_router.router)
app.include_router(releases_router.router)
