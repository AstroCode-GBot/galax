from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_promotion_keyboard(text: str, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, url=url)]
    ])