from fastapi import FastAPI
from routers import admin_router, releases_router, auth_router, channels_router, platforms_router

app = FastAPI()

app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(releases_router.router)
app.include_router(channels_router.router)
app.include_router(platforms_router.router)
