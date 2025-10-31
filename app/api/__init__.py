from fastapi import APIRouter
from app.api import gemini

api_router = APIRouter()

api_router.include_router(gemini.router, prefix='/gemini', tags=['Gemini'])