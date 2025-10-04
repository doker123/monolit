from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import Signal

# Сигнал
user_registered = Signal()
# модель пользователя с моими доп полями
class ProfileUser(AbstractUser):
    avatar = models.ImageField( upload_to='avatars/', null=False, blank=False, verbose_name="Аватар")
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прощёл активацию')
    send_messages = models.BooleanField(default=True, verbose_name="Оповешать о новых сообщениях")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username