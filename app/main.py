from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.auth import auth_router
from app.api.portfolio import portfolio_router
from app.api.watchlist import watchlist_router

from app.api.market import market_router
from app.api.agent import agent_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for the ET Market Oracle Hackathon Project"
)

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS, # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(portfolio_router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(watchlist_router, prefix="/api/watchlist", tags=["Watchlist"])
app.include_router(market_router, prefix="/api/market", tags=["Market"])
app.include_router(agent_router, prefix="/api/agent", tags=["Agent"])

@app.get("/", tags=["Health"])
async def root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}

@app.get("/health", tags=["Health"])
async def health_check():
    """Check if the API is running and configs are loaded."""
    return {
        "status": "healthy",
        "pinecone_configured": bool(settings.PINECONE_API_KEY),
        "database_configured": bool(settings.DATABASE_URL)
    }