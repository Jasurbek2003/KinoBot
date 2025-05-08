from aiogram import types, Router, Bot, F
from aiogram.enums import ContentType

from aiogram.filters import Command
from aiogram.types import UserProfilePhotos, CallbackQuery, FSInputFile

from asgiref.sync import sync_to_async
from django.conf import settings

from botapp.bot import bot
from botapp.keyboards.reply_keyboards import get_main_keyboard
from botapp.keyboards.inline_keyboards import get_settings_inline_keyboard
from botapp.models import TelegramUser
from botapp.services.bot_service import UserService

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message, bot: Bot, _=None, user_language='uz'):
    photos: UserProfilePhotos = await bot.get_user_profile_photos(user_id=message.from_user.id)
    file_id = photos.photos[0][-1].file_id if photos.total_count > 0 else None
    file_path = None
    if file_id:
        file = await bot.get_file(file_id)
        file_path = file.file_path

    if await sync_to_async(TelegramUser.objects.filter(user_id=message.from_user.id).exists)():
        await sync_to_async(TelegramUser.objects.filter(user_id=message.from_user.id).update)(
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            birthdate=message.chat.birthdate,
            profile_photo=file_path,
        )
        await message.answer(_('welcome_back'), reply_markup=get_main_keyboard(user_language))
    else:
        await sync_to_async(TelegramUser.objects.get_or_create)(
            user_id=message.from_user.id,
            defaults={
                "username": message.from_user.username,
                "first_name": message.from_user.first_name,
                "last_name": message.from_user.last_name,
                "birthdate": message.chat.birthdate,
                "profile_photo": file_path,
                "language": "uz",  # Default language
            }
        )
        await message.answer(_('welcome_new'), reply_markup=get_main_keyboard(user_language))


# https://api.telegram.org/file/bot6908708614:AAG7KqPnzD3VuhiFfE2BOTXb7sYK1UcTJM4/videos/file_9.mp4
# url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{user_data['profile_photo']}"

@router.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Настройки"]))
async def settings_handler(message: types.Message, _=None, user_language='uz'):
    await message.answer(
        _('settings_menu'),
        reply_markup=get_settings_inline_keyboard(user_language)
    )


# Add callback handler for language selection
@router.callback_query(F.data.startswith("language:"))
async def language_callback(query: CallbackQuery, _=None):
    # Get selected language code
    lang_code = query.data.split(':')[1]

    # Update user language preference
    await sync_to_async(TelegramUser.objects.filter(user_id=query.from_user.id).update)(language=lang_code)

    # Get new translation function with updated language
    from botapp.utils.translations import get_text
    _ = lambda key, **kwargs: get_text(key, lang_code, **kwargs)

    # Answer callback query
    await query.answer(_('language_selected'))

    # Update message with new language
    await query.message.edit_text(_('settings_menu'), reply_markup=get_settings_inline_keyboard(lang_code))
    await query.message.answer(_('language_selected'), reply_markup=get_main_keyboard(lang_code))




@router.message(F.text.in_(["👤 Profil", "👤 Профиль"]))
async def show_profile(message: types.Message, _=None, user_language='uz'):
    user_service = UserService()
    user_data = await user_service.get_user_profile(message.from_user.id)

    if not user_data:
        await message.answer("Could not find your profile information.")
        return

    profile_text = _('profile_info', name=user_data['name'], joined_date=user_data['joined_date_formatted'])


    # Check if user has a profile photo
    if user_data.get('profile_photo'):
        try:
            # Get the photo path
            photo_path = user_data['profile_photo']  # e.g., photos/file_6.jpg

            # Create temp directory if it doesn't exist
            import os
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Create photos subdirectory inside temp if needed
            photos_dir = os.path.join(temp_dir, "photos")
            if not os.path.exists(photos_dir):
                os.makedirs(photos_dir)

            # Set local path for downloaded file
            local_path = os.path.join(temp_dir, photo_path)

            # Ensure directory for the file exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Download file if it doesn't exist locally
            if not os.path.exists(local_path):
                url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{photo_path}"
                import requests
                photo = requests.get(url, stream=True)
                if photo.status_code == 200:
                    with open(local_path, 'wb') as f:
                        for chunk in photo.iter_content(1024):
                            f.write(chunk)

            # Send the photo
            if os.path.exists(local_path):
                f = FSInputFile(local_path)
                await message.answer_photo(
                    photo=f,
                    caption=profile_text
                )

                # Delete the file after sending
                try:
                    os.remove(local_path)
                    # If you want to log the deletion
                    print(f"File {local_path} was successfully deleted")
                except Exception as del_error:
                    print(f"Error deleting file {local_path}: {del_error}")
            else:
                await message.answer(f"{profile_text}\n\nError: Could not retrieve profile photo.")

        except Exception as e:
            # Log the error and send text-only response
            import logging
            logging.error(f"Error sending profile photo: {e}")
            await message.answer(f"{profile_text}\n\nError: Could not send profile photo. {str(e)}")
    else:
        # No profile photo available
        await message.answer(profile_text)

@router.message(F.content_type == ContentType.VIDEO)
async def handle_videos(message: types.Message, bot: Bot, _=None):
    await message.answer(_('video_received'))
    # Process the video
    file_id = message.video.file_id
    # Do something with the file_id
    print(file_id)
    if file_id:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        print(file_path)



def register_handlers(dp):
    dp.include_router(router)