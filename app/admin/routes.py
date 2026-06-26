from fastapi import APIRouter, Depends, Request, Form, responses, status
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.database.models import User, Download, ApiRoute, Promotion, AdminUser
from app.admin.auth import get_current_admin, hash_password, verify_password, create_admin_token

admin_router = APIRouter(prefix="/admin", tags=["Admin Portal Management"])
templates = Jinja2Templates(directory="app/templates")

@admin_router.get("/login", response_class=responses.HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@admin_router.post("/login")
async def process_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AdminUser).where(AdminUser.username == username)
    res = await db.execute(stmt)
    admin = res.scalar_one_or_none()
    
    if not admin or not verify_password(password, admin.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid administrative credentials supplied."})
        
    response = responses.RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    token = create_admin_token(username)
    response.set_cookie(key="admin_session", value=token, httponly=True, secure=True)
    return response

@admin_router.get("/dashboard", response_class=responses.HTMLResponse)
async def system_dashboard(request: Request, admin: str = Depends(get_current_admin)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "admin": admin})

@admin_router.get("/users", response_class=responses.HTMLResponse)
async def user_accounts_view(request: Request, db: AsyncSession = Depends(get_db), admin: str = Depends(get_current_admin)):
    res = await db.execute(select(User).order_by(User.join_date.desc()))
    users = res.scalars().all()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@admin_router.post("/users/{user_id}/ban")
async def toggle_ban_user(user_id: int, db: AsyncSession = Depends(get_db), admin: str = Depends(get_current_admin)):
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if user:
        user.is_banned = not user.is_banned
        await db.commit()
    return responses.RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)

@admin_router.get("/apis", response_class=responses.HTMLResponse)
async def api_management_view(request: Request, db: AsyncSession = Depends(get_db), admin: str = Depends(get_current_admin)):
    res = await db.execute(select(ApiRoute).order_by(ApiRoute.priority.asc()))
    apis = res.scalars().all()
    return templates.TemplateResponse("apis.html", {"request": request, "apis": apis})

@admin_router.post("/apis/create")
async def create_api_route(
    name: str = Form(...),
    platform: str = Form(...),
    endpoint: str = Form(...),
    priority: int = Form(...),
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(get_current_admin)
):
    api = ApiRoute(name=name, platform=platform, endpoint=endpoint, priority=priority)
    db.add(api)
    await db.commit()
    return responses.RedirectResponse(url="/admin/apis", status_code=status.HTTP_303_SEE_OTHER)