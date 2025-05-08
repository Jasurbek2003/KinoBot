from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from botapp.models import TelegramUser


class AuthenticationMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Check if it's a message with user info
        if isinstance(event, Message) and event.from_user:
            # Get or create user
            user, created = await TelegramUser.objects.aget_or_create(
                user_id=event.from_user.id,
                defaults={
                    'username': event.from_user.username,
                    'first_name': event.from_user.first_name,
                    'last_name': event.from_user.last_name
                }
            )

            # Update user data if not created
            if not created:
                await TelegramUser.objects.filter(user_id=event.from_user.id).aupdate(
                    username=event.from_user.username,
                    first_name=event.from_user.first_name,
                    last_name=event.from_user.last_name
                )

            # Add user to data dict
            data['telegram_user'] = user

        return await handler(event, data)