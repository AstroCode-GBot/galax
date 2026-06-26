import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import settings
from app.bot.handlers import bot_router

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(bot_router)
    
    logging.info("Starting Telegram Bot Core Sub-Worker daemon Process...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())