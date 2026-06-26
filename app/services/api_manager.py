import aiohttp
from typing import Optional, List
from sqlalchemy import select
from app.database.session import AsyncSessionLocal
from app.database.models import ApiRoute

class DistributedApiFallbackEngine:
    @classmethod
    async def get_active_routes(cls, platform: str) -> List[str]:
        async with AsyncSessionLocal() as session:
            stmt = select(ApiRoute).where(
                ApiRoute.platform == platform,
                ApiRoute.status == True
            ).order_by(ApiRoute.priority.asc())
            res = await session.execute(stmt)
            return [api.endpoint for api in res.scalars().all()]

    @classmethod
    async def fetch_with_fallback(cls, platform: str, url: str) -> Optional[dict]:
        endpoints = await cls.get_active_routes(platform)
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    target_url = f"{endpoint}{url}"
                    async with session.get(target_url, timeout=10) as resp:
                        if resp.status == 200:
                            return await resp.json()
                except Exception:
                    continue # Try the next route if this one fails
        return None