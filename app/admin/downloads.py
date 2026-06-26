from fastapi import APIRouter, Depends, Request, responses
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.database.models import Download
from app.admin.auth import get_current_admin

download_ledger_router = APIRouter(prefix="/admin/downloads", tags=["Download Engine Core Ledgers"])
templates = Jinja2Templates(directory="app/templates")

@download_ledger_router.get("", response_class=responses.HTMLResponse)
async def view_downloads_ledger(request: Request, platform: str = None, db: AsyncSession = Depends(get_db), admin: str = Depends(get_current_admin)):
    query = select(Download).order_by(Download.created_at.desc())
    if platform:
        query = query.where(Download.platform == platform)
    res = await db.execute(query.limit(100))
    downloads = res.scalars().all()
    return templates.TemplateResponse("downloads.html", {"request": request, "downloads": downloads})
