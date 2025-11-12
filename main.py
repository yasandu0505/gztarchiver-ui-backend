from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from api.routes import api_router
from database.optimization import optimize_database_indexes

# Initialize FastAPI app
app = FastAPI(
    title="GZT Archiver UI Backend",
    description="Backend API for GZT Archiver",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router)

# Auto-optimize database on startup
@app.on_event("startup")
async def startup_event():
    """Optimize database indexes on startup"""
    optimize_database_indexes()
