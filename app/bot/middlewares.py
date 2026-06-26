import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from redis.asyncio import Redis

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, redis_client: Redis, limit_seconds: int = 3):
        self.redis = redis_client
        self.limit = limit_seconds
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if not event.from_user:
            return await handler(event, data)
            
        user_id = event.from_user.id
        key = f"ratelimit:{user_id}"
        
        is_exists = await self.redis.exists(key)
        if is_exists:
            return await event.answer("⚠️ *System Guard*: Please do not spam links. Rate limit active (3s).", parse_mode="Markdown")
            
        await self.redis.setex(key, self.limit, "active")
        return await handler(event, data)