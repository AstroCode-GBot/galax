import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit_seconds: int = 3):
        # Using a standard dictionary to store user activity in RAM
        self.storage = {}
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
        current_time = time.time()
        
        # Check if user has an existing cooling period active
        if user_id in self.storage:
            last_request_time = self.storage[user_id]
            if current_time - last_request_time < self.limit:
                return await event.answer("⚠️ *System Guard*: Please do not spam links. Rate limit active (3s).", parse_mode="Markdown")
                
        # Update user's timestamp matrix
        self.storage[user_id] = current_time
        return await handler(event, data)
