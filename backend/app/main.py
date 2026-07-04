from __future__ import annotations

"""
FinContext API — Main Application
==================================
AI-powered contextual analysis for Indian equities.

Run with: uvicorn app.main:app --reload --port 8000
"""

import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.db import init_db
from app.routers import (
    stocks,
    market,
    portfolio,
    watchlist,
    analysis,
    zerodha,
    portfolio_intelligence,
    global_news,
    company_data,
    risk,
    embeddings as embeddings_router,
    outcomes as outcomes_router,
    telegram as telegram_router,
    onboarding as onboarding_router,
    auth as auth_router,
)
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")
# Print loaded CORS config at boot — visible in Render logs. Helps diagnose
# "Access-Control-Allow-Origin missing" errors caused by env var typos.
logger.info("CORS_ORIGINS loaded: %r", settings.CORS_ORIGINS)
logger.info("CORS_ORIGIN_REGEX loaded: %r", settings.CORS_ORIGIN_REGEX)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="FinContext API",
    description="AI-powered contextual analysis engine for Indian equities.",
    version="0.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


@app.get("/_debug/cors", tags=["system"])
async def debug_cors():
    """Returns the loaded CORS config so you can verify env-var values from Render
    without redeploying. Safe to keep enabled — exposes only allowed origins, no secrets."""
    return {
        "allow_origins": settings.CORS_ORIGINS,
        "allow_origin_regex": settings.CORS_ORIGIN_REGEX,
    }

app.include_router(stocks.router)
app.include_router(market.router)
app.include_router(portfolio.router)
app.include_router(watchlist.router)
app.include_router(analysis.router)
app.include_router(zerodha.router)
app.include_router(portfolio_intelligence.router)
app.include_router(global_news.router)
app.include_router(company_data.router)
app.include_router(risk.router)
app.include_router(embeddings_router.router)
app.include_router(outcomes_router.router)
app.include_router(telegram_router.router)
app.include_router(onboarding_router.router)
app.include_router(auth_router.router)


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "healthy", "version": "0.5.0"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    import os
    favicon_path = os.path.join(os.path.dirname(__file__), "favicon.png")
    return FileResponse(favicon_path)
