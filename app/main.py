from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from app.database.session import engine, Base, AsyncSessionLocal
from app.database.models import User, Download, ApiRoute
from app.config import settings

app = FastAPI(title="All Saver Pro Control Matrix")

@app.on_event("startup")
async def prepare_infrastructure():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health_check():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(select(func.count(User.id)))
        return {
            "status": "online",
            "bot": "running",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"database": "disconnected", "error": str(e)})

# Core API Management Endpoints
@app.get("/api/v1/metrics")
async def get_system_metrics():
    async with AsyncSessionLocal() as session:
        users = await session.execute(select(func.count(User.id)))
        downloads = await session.execute(select(func.count(Download.id)))
        return {
            "total_users": users.scalar() or 0,
            "total_downloads": downloads.scalar() or 0
        }