from fastapi import APIRouter

from app.api.routes import utils, cities, users, surveys, games

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(cities.router)
api_router.include_router(utils.router)
api_router.include_router(surveys.router)
api_router.include_router(games.router)