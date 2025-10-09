import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.main import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)
resources_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../content"))

app.mount(
    "/content",
    StaticFiles(directory=resources_path),
    name="content"
)


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="fastapi-session",
)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"], #["http://192.168.43.45:5173", "http://192.168.80.177:5173/"], #settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

from app.admin.config import admin
admin.mount_to(app)
app.include_router(api_router, prefix=settings.API_V1_STR)
