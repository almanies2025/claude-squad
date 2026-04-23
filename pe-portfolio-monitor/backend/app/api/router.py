"""API router — aggregates all route modules under /auth, /companies, /metrics, /alerts."""

from fastapi import APIRouter

from app.api import alerts, auth, companies, metrics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(metrics.router, prefix="", tags=["metrics"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
