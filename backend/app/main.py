import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .seed import seed_database
from .routers import health, countries, news, stories, admin, forex, patro, ai_detector
from .services.live_news_engine import run_live_news_background_loop
import asyncio

# Ensure backend root is in sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="TruthWire: Country-first hybrid news aggregation and evidence-verification portal (NP, US, CA pilot)."
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(countries.router, prefix=settings.API_V1_PREFIX)
app.include_router(news.router, prefix=settings.API_V1_PREFIX)
app.include_router(stories.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(forex.router, prefix=settings.API_V1_PREFIX)
app.include_router(patro.router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_detector.router, prefix=settings.API_V1_PREFIX)

_live_news_task = None

@app.on_event("startup")
async def on_startup():
    print("Initializing TruthWire tables...")
    Base.metadata.create_all(bind=engine)
    seed_database()
    global _live_news_task
    _live_news_task = asyncio.create_task(run_live_news_background_loop())
    print("TruthWire API & 30s Live News Engine initialization complete.")

@app.on_event("shutdown")
def on_shutdown():
    global _live_news_task
    if _live_news_task:
        _live_news_task.cancel()

@app.get("/")
def root():
    return {
        "message": "Welcome to TruthWire API",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "countries": f"{settings.API_V1_PREFIX}/countries",
        "news": f"{settings.API_V1_PREFIX}/news?country=NP&feed=latest"
    }
