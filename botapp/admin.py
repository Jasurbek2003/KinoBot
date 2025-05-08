from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings

from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        "profile_photo_thumbnail", 'user_id', 'username', 'first_name', 'last_name', 'language', 'birthdate',
        'created_at',
        'updated_at'
    )
    search_fields = (
        'user_id', 'username', 'first_name', 'last_name', 'language', 'birthdate', 'profile_photo', 'created_at',
        'updated_at'
    )
    list_filter = (
        'language', 'user_id', 'username', 'first_name', 'last_name', 'birthdate', 'profile_photo', 'created_at',
        'updated_at'
    )
    ordering = (
        'user_id', 'username', 'first_name', 'last_name', 'birthdate', 'profile_photo', 'created_at', 'updated_at'
    )
    readonly_fields = ('created_at', 'updated_at')
    list_display_links = ('user_id', 'username', "profile_photo_thumbnail")
    fieldsets = (
        (None, {
            'fields': ('user_id', 'username', 'first_name', 'last_name', 'language', 'birthdate', 'profile_photo')
        }),
        ('Important dates', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('user_id', 'username', 'first_name', 'last_name', 'language', 'birthdate', 'profile_photo')
        }),
    )
    filter_horizontal = ()
    actions = []

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.save()

    def get_readonly_fields(self, request, obj=...):
        if obj:
            return self.readonly_fields + ('user_id',)
        return self.readonly_fields

    def profile_photo_thumbnail(self, obj):
        if obj.profile_photo:
            url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{obj.profile_photo}"
            return format_html('<img src="{}" width="150" height="150" />', url)
        return "(No Image)"

    profile_photo_thumbnail.short_description = 'Profile Photo'
    profile_photo_thumbnail.allow_tags = True
