import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from sqlalchemy import select
from app.database.session import AsyncSessionLocal
from app.database.models import User, Download, Promotion
from app.services.download_service import DownloadScraperEngine

bot_router = Router()

@bot_router.message(CommandStart())
async def run_start_command(message: Message):
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.id == message.from_user.id)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        
        if not user:
            user = User(
                id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            session.add(user)
        else:
            user.last_activity = datetime.datetime.utcnow()
        await session.commit()
        
    await message.answer("👋 *Welcome to All Saver Pro!*\n\nSend me a link from TikTok, Instagram, Facebook, Pinterest, Spotify, or Terabox, and I'll fetch the media for you instantly.", parse_mode="Markdown")

@bot_router.message(F.text)
async def handle_incoming_links(message: Message, bot: Bot):
    url = message.text.strip()
    platform = DownloadScraperEngine.identify_platform(url)
    
    if not platform:
        await message.answer("❌ *Unsupported link or platform. Please verify your asset address.*", parse_mode="Markdown")
        return

    async with AsyncSessionLocal() as session:
        user_res = await session.execute(select(User).where(User.id == message.from_user.id))
        user = user_res.scalar_one_or_none()
        if user and user.is_banned:
            await message.answer("🚫 You are banned from utilizing this engine interface.")
            return

    # Visual Processing Indicators
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    status_msg = await message.answer("👀 Checking your link...")
    
    await status_msg.edit_text("⏳ Processing download...")
    
    payload = await DownloadScraperEngine.process_download(platform, url)
    
    if not payload or not payload.get("direct_url"):
        await status_msg.edit_text("❌ *Download extraction failed. System pipeline error.*", parse_mode="Markdown")
        return

    try:
        await status_msg.edit_text("✅ Download completed")
        
        # Check active promotional injection rules
        async with AsyncSessionLocal() as db_session:
            promo_res = await db_session.execute(select(Promotion).where(Promotion.status == True).limit(1))
            promo = promo_res.scalar_one_or_none()
            
            # Record download log metric
            dw = Download(user_id=message.from_user.id, platform=platform, url=url, file_name=payload.get("title"), status="completed")
            db_session.add(dw)
            if user:
                user.download_count += 1
            await db_session.commit()

        if payload.get("direct_url"):
            await message.reply_video(
                video=payload["direct_url"], 
                caption=f"🎥 *Asset Title*: {payload.get('title')}\n\n🤖 Powered by @AllSaverPro_bot",
                parse_mode="Markdown"
            )
            
            if promo:
                # Add inline link if dynamic marketing copy applies
                kb = None
                if promo.button_text and promo.button_url:
                    kb = get_promotion_keyboard(promo.button_text, promo.button_url)
                await message.answer(f"📢 *Sponsor Announcement*\n\n{promo.message}", parse_mode="Markdown", reply_markup=kb)

    except Exception as e:
        await message.answer(f"⚠️ Error transferring file asset into Telegram Cloud ecosystem: {str(e)}")