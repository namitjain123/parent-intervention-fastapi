from fastapi import APIRouter

from app.api.routes import admin, episodes, questionnaires, users

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(questionnaires.router)
api_router.include_router(episodes.router)
api_router.include_router(admin.router)
