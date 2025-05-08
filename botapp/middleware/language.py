from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, CallbackQuery

from asgiref.sync import sync_to_async
from botapp.models import TelegramUser
from botapp.utils.translations import get_text


class LanguageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Get user_id from either Message or CallbackQuery
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id:
            # Get user language preference
            try:
                user = await sync_to_async(TelegramUser.objects.get)(user_id=user_id)
                language = user.language
            except TelegramUser.DoesNotExist:
                language = 'uz'  # Default to Uzbek if user not found

            # Add language and translation function to data dict
            data['user_language'] = language

            # Create a custom get_text function that already has the language set
            def _get_text(key, **kwargs):
                return get_text(key, language, **kwargs)

            data['_'] = _get_text

        return await handler(event, data)