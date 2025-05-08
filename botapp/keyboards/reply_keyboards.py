from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from botapp.utils.translations import get_text

def get_main_keyboard(language='uz') -> ReplyKeyboardMarkup:
    """Create main reply keyboard with translated buttons"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text('balance', language)),
                KeyboardButton(text=get_text('statistics', language)),
            ],
            [
                KeyboardButton(text=get_text('debts', language)),
                KeyboardButton(text=get_text('history', language))
            ],
            [
                KeyboardButton(text=get_text('subscription', language)),
                KeyboardButton(text=get_text('settings', language))
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=get_text('keyboard_placeholder', language),
        is_persistent=True,
        selective=True
    )
    return keyboard