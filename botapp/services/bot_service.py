from typing import Dict, List, Optional
from asgiref.sync import sync_to_async
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from botapp.models import TelegramUser

logger = logging.getLogger(__name__)


class BaseService:
    """Base service with common utilities"""

    @staticmethod
    async def log_action(action_type: str, user_id: int, data: Dict = None):
        """Log user actions for analytics"""
        if data is None:
            data = {}

        logger.info(f"User {user_id} performed {action_type}: {data}")

    @staticmethod
    def format_date(date_obj: datetime) -> str:
        """Format date in user-friendly format"""
        return date_obj.strftime("%d %b %Y %H:%M")


class UserService(BaseService):
    """Service for user-related operations"""

    @staticmethod
    @sync_to_async
    def get_user_profile(telegram_id: int) -> Optional[Dict]:
        """Get user profile data from database"""
        try:
            user = TelegramUser.objects.get(user_id=telegram_id)
            return {
                'id': user.id,
                'telegram_id': user.user_id,
                'name': f"{user.first_name} {user.last_name or ''}".strip(),
                'username': user.username,
                'joined_date': user.created_at,
                'joined_date_formatted': UserService.format_date(user.created_at),
                'is_admin': user.is_admin,
                'profile_photo': user.profile_photo
            }
        except TelegramUser.DoesNotExist:
            logger.warning(f"User with telegram_id {telegram_id} not found")
            return None

    @staticmethod
    @sync_to_async
    def update_user_data(telegram_id: int, **kwargs) -> bool:
        """Update user data in database"""
        try:
            result = TelegramUser.objects.filter(user_id=telegram_id).update(**kwargs)
            return result > 0
        except Exception as e:
            logger.error(f"Error updating user {telegram_id}: {e}")
            return False

    @staticmethod
    @sync_to_async
    def set_user_state(telegram_id: int, state: str) -> bool:
        """Set user state in database for analytics or custom FSM"""
        try:
            TelegramUser.objects.filter(user_id=telegram_id).update(
                last_state=state,
                updated_at=timezone.now()
            )
            return True
        except Exception as e:
            logger.error(f"Error setting state for user {telegram_id}: {e}")
            return False

    @staticmethod
    @sync_to_async
    def get_user_stats() -> Dict:
        """Get user statistics for admin dashboard"""
        total_users = TelegramUser.objects.count()
        active_today = TelegramUser.objects.filter(
            updated_at__gte=timezone.now() - timedelta(days=1)
        ).count()
        active_week = TelegramUser.objects.filter(
            updated_at__gte=timezone.now() - timedelta(days=7)
        ).count()

        return {
            'total_users': total_users,
            'active_today': active_today,
            'active_week': active_week,
            'retention_rate': round(active_week / total_users * 100, 2) if total_users > 0 else 0
        }

    @staticmethod
    @sync_to_async
    def search_users(query: str, limit: int = 10) -> List[Dict]:
        """Search users by name, username, or telegram_id"""
        users = TelegramUser.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(telegram_id__icontains=query)
        )[:limit]

        return [
            {
                'id': user.id,
                'telegram_id': user.user_id,
                'name': f"{user.first_name} {user.last_name or ''}".strip(),
                'username': user.username
            }
            for user in users
        ]

    @staticmethod
    @sync_to_async
    def get_user_language(telegram_id: int) -> str:
        """Get user language preference"""
        try:
            user = TelegramUser.objects.get(user_id=telegram_id)
            return user.language
        except TelegramUser.DoesNotExist:
            return 'uz'  # Default to Uzbek if user not found

    @staticmethod
    @sync_to_async
    def set_user_language(telegram_id: int, language: str) -> bool:
        """Set user language preference"""
        try:
            result = TelegramUser.objects.filter(user_id=telegram_id).update(language=language)
            return result > 0
        except Exception as e:
            logger.error(f"Error setting language for user {telegram_id}: {e}")
            return False


class NotificationService(BaseService):
    """Service for sending notifications to users"""

    def __init__(self, bot):
        """Initialize with bot instance"""
        self.bot = bot

    @staticmethod
    @sync_to_async
    def get_admin_users() -> List[int]:
        """Get list of admin user IDs"""
        return list(TelegramUser.objects.filter(is_admin=True).values_list('telegram_id', flat=True))

    @staticmethod
    @sync_to_async
    def get_active_users(days: int = 30) -> List[int]:
        """Get list of active user IDs"""
        cutoff_date = timezone.now() - timedelta(days=days)
        return list(TelegramUser.objects.filter(
            updated_at__gte=cutoff_date
        ).values_list('telegram_id', flat=True))

    async def send_to_admins(self, message: str, **kwargs) -> None:
        """Send message to all admin users"""
        admin_ids = await self.get_admin_users()
        for admin_id in admin_ids:
            try:
                await self.bot.send_message(chat_id=admin_id, text=message, **kwargs)
            except Exception as e:
                logger.error(f"Error sending message to admin {admin_id}: {e}")

    async def broadcast(self, message: str, user_ids: List[int] = None, **kwargs) -> Dict:
        """Send mass message to users"""
        if user_ids is None:
            user_ids = await self.get_active_users()

        results = {"success": 0, "failed": 0, "total": len(user_ids)}

        for user_id in user_ids:
            try:
                await self.bot.send_message(chat_id=user_id, text=message, **kwargs)
                results["success"] += 1
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                results["failed"] += 1

        return results


class ContentService(BaseService):
    """Service for content-related operations"""

    @staticmethod
    @sync_to_async
    def get_bot_content(content_key: str, default: str = None) -> str:
        """Get content from database by key"""
        # This assumes you have a model for storing bot content
        # You would need to create a BotContent model
        # For simplicity, we'll just return dummy data
        content_map = {
            "welcome_message": "Welcome to our bot! How can I help you today?",
            "help_message": "Here are the available commands:\n/start - Start the bot\n/help - Get help",
            "about_message": "This bot was created using aiogram3 and Django."
        }

        return content_map.get(content_key, default)

    @staticmethod
    async def get_help_content(user_type: str = "regular") -> str:
        """Get help content based on user type"""
        if user_type == "admin":
            return await ContentService.get_bot_content("help_message_admin",
                                                        "Admin commands:\n/stats - View statistics\n/broadcast - Send message to all users")
        else:
            return await ContentService.get_bot_content("help_message",
                                                        "Here are the available commands:\n/start - Start the bot\n/help - Get help")


class AnalyticsService(BaseService):
    """Service for tracking and analyzing user actions"""

    @staticmethod
    @sync_to_async
    def track_command(telegram_id: int, command: str) -> None:
        """Track command usage"""
        # This would typically use a CommandLog model
        # For simplicity, we'll just log it
        logger.info(f"User {telegram_id} used command: {command}")

    @staticmethod
    @sync_to_async
    def get_popular_commands(days: int = 7, limit: int = 5) -> List[Dict]:
        """Get most popular commands"""
        # This would typically query the CommandLog model
        # For simplicity, we'll return dummy data
        return [
            {"command": "/start", "count": 145},
            {"command": "/help", "count": 87},
            {"command": "/profile", "count": 56},
            {"command": "/settings", "count": 34},
            {"command": "/about", "count": 22}
        ]

    @staticmethod
    @sync_to_async
    def get_user_retention(days: int = 30) -> Dict:
        """Get user retention statistics"""
        # This would typically involve complex queries
        # For simplicity, we'll return dummy data
        return {
            "new_users": 120,
            "returning_users": 450,
            "retention_rate": 78.5
        }


class PaymentService(BaseService):
    """Service for handling payments"""

    @staticmethod
    @sync_to_async
    def create_invoice(telegram_id: int, amount: float, description: str) -> Dict:
        """Create payment invoice"""
        # This would typically involve a Payment model and payment gateway
        # For simplicity, we'll return dummy data
        invoice_id = f"INV-{telegram_id}-{int(datetime.now().timestamp())}"
        return {
            "invoice_id": invoice_id,
            "amount": amount,
            "description": description,
            "status": "pending",
            "created_at": timezone.now()
        }

    @staticmethod
    @sync_to_async
    def check_payment_status(invoice_id: str) -> str:
        """Check payment status"""
        # This would typically query the payment gateway
        # For simplicity, we'll return dummy data
        return "completed"

