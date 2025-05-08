from django.db import models

class TelegramUser(models.Model):
    LANGUAGE_CHOICES = (
        ('uz', 'Uzbek'),
        ('ru', 'Russian'),
    )

    user_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    profile_photo = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='uz')
    subscription = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.user_id) + " " + self.username


class Movie(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    file = models.CharField(max_length=255, null=True, blank=True)
    poster = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class Subscription(models.Model):
    TYPE_CHOICES = (
        ('group', 'group'),
        ('channel', 'channel'),
        ('instagram', 'instagram'),
    )
    username = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.username


