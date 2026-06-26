from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.admin.routes import admin_router
from app.admin.promotions import promo_router
from app.admin.downloads import download_ledger_router
from app.database.session import engine, Base, AsyncSessionLocal
from app.database.models import AdminUser, ApiRoute
from app.admin.auth import hash_password
from sqlalchemy import select

app = FastAPI(title="All Saver Pro Control Matrix", version="2.4.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(admin_router)
app.include_router(promo_router)
app.include_router(download_ledger_router)

@app.on_event("startup")
async def absolute_auto_initialization():
    # 1. Automatically generate all missing database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # 2. Automatically seed administrative credentials and fallback routes
    async with AsyncSessionLocal() as session:
        admin_check = await session.execute(select(AdminUser))
        if not admin_check.first():
            root_admin = AdminUser(
                username="admin_matrix",
                password_hash=hash_password("MatrixCoreSecured2026!"),
                permissions="root"
            )
            session.add(root_admin)
            
        api_check = await session.execute(select(ApiRoute))
        if not api_check.first():
            default_apis = [
                ApiRoute(name="TikWM Direct", platform="tiktok", endpoint="https://www.tikwm.com/api/?url=", priority=1),
                ApiRoute(name="IGram Site", platform="instagram", endpoint="https://igram.site/api/instagram?url=", priority=1),
                ApiRoute(name="Serverless Gateway", platform="facebook", endpoint="https://serverless-tooly-gateway-6n4h522y.ue.gateway.dev/facebook/video?url=", priority=1),
                ApiRoute(name="PinsSaver Global", platform="pinterest", endpoint="https://api.pinssaver.com/pin?url=", priority=1),
                ApiRoute(name="Spotyloader Core", platform="spotify", endpoint="https://spotyloader.com/api/spotify/info?url=", priority=1),
                ApiRoute(name="Teradown Production", platform="terabox", endpoint="https://teradown-dzv3.onrender.com/api?url=", priority=1)
            ]
            session.add_all(default_apis)
            
        await session.commit()

@app.get("/health")
async def health_check():
    return {"status": "online", "database": "synchronized"}
