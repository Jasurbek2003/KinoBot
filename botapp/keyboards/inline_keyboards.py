from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from botapp.utils.translations import get_text

def get_settings_inline_keyboard(language='uz') -> InlineKeyboardMarkup:
    """Create inline keyboard for language selection"""
    if language=="ru":
        language_button = InlineKeyboardButton(text="🇺🇿 Tilni o'zbek tiliga o'zgartirish", callback_data="language:uz")
    else:
        language_button = InlineKeyboardButton(text="🇷🇺 Изменить язык на русский", callback_data="language:ru")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_text("help_message", language), callback_data="settings:help"),
                InlineKeyboardButton(text=get_text("about_us", language), callback_data="settings:about"),
            ],
            [
                language_button
            ],
        ]
    )
    return keyboard