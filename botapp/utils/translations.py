# botapp/utils/translations.py

TRANSLATIONS = {
    'uz': {
        # Main keyboard buttons
        'balance': "💰 Balansim",
        'statistics': "📊 Statistika",
        'debts': "💸 Qarzlar",
        'history': "📋 Tarix",
        'subscription': "💎 Obuna",
        'settings': "⚙️ Sozlamalar",
        'profile': "👤 Profil",
        'keyboard_placeholder': "Quyidagilardan birini tanlang.",

        # Command responses
        'welcome_back': "Qaytib kelganingizdan xursandmiz!",
        'welcome_new': "Botimizga xush kelibsiz!",
        'profile_info': "Sizning profilingiz:\nIsm: {name}\nAzo bo'lgan sana: {joined_date}",
        'video_received': "Siz video yubordingiz!",

        # Settings
        'settings_menu': "Iltimos, quyidagilardan birini tanlang:",
        'language_selected': "O'zbek tili tanlandi!",
        'language_button': "🇺🇿 O'zbek tili",
        'change_language': "Tilni o'zgartirish",
        'help_message': "ℹ️ Yordam",
        'about_us': "ℹ️ Biz haqimizda",
    },
    'ru': {
        # Main keyboard buttons
        'balance': "💰 Баланс",
        'statistics': "📊 Статистика",
        'debts': "💸 Долги",
        'history': "📋 История",
        'subscription': "💎 Подписка",
        'settings': "⚙️ Настройки",
        'profile': "👤 Профиль",
        'keyboard_placeholder': "Выберите один из следующих.",

        # Command responses
        'welcome_back': "Рады видеть вас снова!",
        'welcome_new': "Добро пожаловать в наш бот!",
        'profile_info': "Ваш профиль:\nИмя: {name}\nДата регистрации: {joined_date}",
        'video_received': "Вы отправили видео!",

        # settings
        'settings_menu': "Пожалуйста, выберите один из следующих вариантов:",
        'language_selected': "Выбран русский язык!",
        'language_button': "🇷🇺 Русский язык",
        'change_language': "Изменить язык",
        'help_message': "ℹ️ Помощь",
        'about_us': "ℹ️ О нас",
    }
}


def get_text(key, language='uz', **kwargs):
    """Get translated text by key and language with formatting"""
    if language not in TRANSLATIONS:
        language = 'uz'  # Default to Uzbek if language not found

    text = TRANSLATIONS[language].get(key, TRANSLATIONS['uz'].get(key, key))

    # Format the text with any provided keyword arguments
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass

    return text