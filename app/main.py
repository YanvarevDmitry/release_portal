import logging

from fastapi import FastAPI

from routers import admin_router, releases_router, auth_router, channels_router, platforms_router, tasks_router, \
    features_router, users_router

# setup loggers
logging.config.fileConfig('logg_config.py', disable_existing_loggers=False)
app = FastAPI()

app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(channels_router.router)
app.include_router(platforms_router.router)
app.include_router(releases_router.router)
app.include_router(features_router.router)
app.include_router(tasks_router.router)
app.include_router(users_router.router)
