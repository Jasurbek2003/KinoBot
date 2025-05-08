from django.core.management.base import BaseCommand
import asyncio
import logging
from botapp.bot import dp, bot
from botapp.handlers import main_handlers
from botapp.middleware.authentication import AuthenticationMiddleware
from botapp.middleware.language import LanguageMiddleware
from botapp.middleware.throttling import ThrottlingMiddleware, AdvancedThrottlingMiddleware


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **options):
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        asyncio.run(self.start_bot())

    async def start_bot(self):
        dp.message.middleware(AuthenticationMiddleware())
        dp.message.middleware(ThrottlingMiddleware())
        dp.message.middleware(AdvancedThrottlingMiddleware())

        dp.message.middleware(LanguageMiddleware())
        dp.callback_query.middleware(LanguageMiddleware())


        main_handlers.register_handlers(dp)
        # admin_handlers.register_handlers(dp)

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())