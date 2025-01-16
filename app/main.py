import json
from urllib.request import Request

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from routers import admin_router, releases_router, auth_router, channels_router, platforms_router, tasks_router, \
    features_router

app = FastAPI()

app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(releases_router.router)
app.include_router(features_router.router)
app.include_router(tasks_router.router)
app.include_router(channels_router.router)
app.include_router(platforms_router.router)


@app.middleware("http")
async def dispatch(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except RequestValidationError as exc:
        error_details = exc.errors()
        readable_errors = [
            {
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"]
            }
            for error in error_details
        ]
        print("Validation Error:", json.dumps(readable_errors, indent=2, ensure_ascii=False))
        return JSONResponse(
            status_code=422,
            content={"detail": readable_errors}
        )
