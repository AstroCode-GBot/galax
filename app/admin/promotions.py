from fastapi import APIRouter, Depends, Request, Form, responses, status
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.database.models import Promotion
from app.admin.auth import get_current_admin

promo_router = APIRouter(prefix="/admin/promotions", tags=["Promo Architecture Layout Engines"])
templates = Jinja2Templates(directory="app/templates")

@promo_router.get("", response_class=responses.HTMLResponse)
async def list_promotions(request: Request, db: AsyncSession = Depends(get_db), admin: str = Depends(get_current_admin)):
    res = await db.execute(select(Promotion).order_by(Promotion.created_at.desc()))
    promotions = res.scalars().all()
    return templates.TemplateResponse("promotions.html", {"request": request, "promotions": promotions})

@promo_router.post("/create")
async def create_promotion(
    title: str = Form(...),
    message: str = Form(...),
    sponsor_username: str = Form(None),
    button_text: str = Form(None),
    button_url: str = Form(None),
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(get_current_admin)
):
    promo = Promotion(
        title=title,
        message=message,
        sponsor_username=sponsor_username,
        button_text=button_text,
        button_url=button_url,
        status=True
    )
    db.add(promo)
    await db.commit()
    return responses.RedirectResponse(url="/admin/promotions", status_code=status.HTTP_303_SEE_OTHER)

@promo_router.post("/{promo_id}/toggle")
async def toggle_promotion(promo_id: int, db: AsyncSession = Depends(get_db), admin: str = Depends(get_current_admin)):
    res = await db.execute(select(Promotion).where(Promotion.id == promo_id))
    promo = res.scalar_one_or_none()
    if promo:
        promo.status = not promo.status
        await db.commit()
    return responses.RedirectResponse(url="/admin/promotions", status_code=status.HTTP_303_SEE_OTHER)
