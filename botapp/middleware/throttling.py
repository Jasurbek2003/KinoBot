# bot/middleware/throttling.py
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
import asyncio
from datetime import datetime


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for rate limiting user requests to prevent spam and abuse.
    """

    def __init__(self, rate_limit=1.0, key_prefix='antiflood_'):
        """
        Initialize throttling middleware

        :param rate_limit: Minimum time between requests in seconds
        :param key_prefix: Prefix for throttling keys
        """
        self.rate_limit = rate_limit
        self.prefix = key_prefix
        self.user_timeouts = {}

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Apply throttling only to messages
        if isinstance(event, Message):
            user_id = event.from_user.id
            key = f"{self.prefix}_{user_id}"

            # Check if user is in timeout and if enough time has passed
            current_time = datetime.now().timestamp()
            if key in self.user_timeouts:
                last_request_time = self.user_timeouts[key]
                time_passed = current_time - last_request_time

                if time_passed < self.rate_limit:
                    # If user is sending requests too quickly, throttle the request
                    wait_time = self.rate_limit - time_passed
                    await asyncio.sleep(wait_time)

            # Update the last request time
            self.user_timeouts[key] = current_time

        # Process the request
        return await handler(event, data)


# Advanced version with different rate limits for different handlers
class AdvancedThrottlingMiddleware(BaseMiddleware):
    """
    Advanced throttling middleware with different rate limits for different commands
    and ability to exempt certain users (like admins).
    """

    def __init__(self):
        self.default_rate_limit = 1.0  # Default rate limit in seconds
        self.user_timeouts = {}
        self.rate_limits = {
            # Command name: rate limit in seconds
            "start": 5.0,  # Allow /start once every 5 seconds
            "help": 3.0,  # Allow /help once every 3 seconds
            "default": 1.0  # Default for all other commands
        }
        self.exempt_users = set()  # Set of user IDs exempt from throttling

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message) or not event.text:
            return await handler(event, data)

        # Check if user is exempt from throttling (e.g., admins)
        user_id = event.from_user.id
        if user_id in self.exempt_users:
            return await handler(event, data)

        # Determine the rate limit based on the command
        command = event.text.split()[0].lower().lstrip('/')
        rate_limit = self.rate_limits.get(command, self.rate_limits['default'])

        # Create a unique key for this user and command
        key = f"throttle_{user_id}_{command}"

        # Check if user is in timeout for this command
        current_time = datetime.now().timestamp()
        if key in self.user_timeouts:
            last_request_time = self.user_timeouts[key]
            time_passed = current_time - last_request_time

            if time_passed < rate_limit:
                # User is sending requests too quickly
                # Option 1: Wait (delay response)
                # await asyncio.sleep(rate_limit - time_passed)

                # Option 2: Notify user about throttling
                if command != "throttled_notification":  # Prevent notification loop
                    remaining = round(rate_limit - time_passed, 1)
                    await event.answer(
                        f"Please wait {remaining} seconds before using this command again.",
                        reply=True
                    )
                return None  # Stop processing the handler

        # Update the last request time
        self.user_timeouts[key] = current_time

        # Clean up old entries to prevent memory leaks
        self._cleanup_timeouts(current_time)

        # Process the request
        return await handler(event, data)

    def add_exempt_user(self, user_id: int):
        """Add a user to the exempt list"""
        self.exempt_users.add(user_id)

    def remove_exempt_user(self, user_id: int):
        """Remove a user from the exempt list"""
        if user_id in self.exempt_users:
            self.exempt_users.remove(user_id)

    def set_rate_limit(self, command: str, limit: float):
        """Set rate limit for a specific command"""
        self.rate_limits[command] = limit

    def _cleanup_timeouts(self, current_time: float, max_age: float = 3600):
        """Clean up old timeout entries to prevent memory leaks"""
        keys_to_delete = []
        for key, timestamp in self.user_timeouts.items():
            if current_time - timestamp > max_age:  # Remove entries older than max_age
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self.user_timeouts[key]