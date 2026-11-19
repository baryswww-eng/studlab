"""Aggregates all v1 endpoint routers. New modules (auth, courses, ...) are added here."""

from fastapi import APIRouter

from app.api.v1.endpoints import ai, assessment, auth, catalog, health, progress, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(catalog.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(progress.router)
api_router.include_router(assessment.router)
api_router.include_router(ai.router)
