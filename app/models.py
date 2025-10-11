from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.dispatch import Signal
from django.db.models import Count


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

class Question(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок вопроса")
    short_description = models.TextField(max_length=500, verbose_name="Краткое описания")
    full_description = models.TextField(verbose_name="Полное описание")
    image = models.ImageField(upload_to='question_images/', blank=True, null=True, verbose_name="Фото для вопроса")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания голосования")
    expires_at = models.DateTimeField(verbose_name="Дата окончания голосования")

    def get_results(self):
        choices = self.choices.annotate(vote_count=Count('vote')).order_by('-vote_count')
        total_votes = sum(choice.vote_count for choice in choices)
        results = []
        for choice in choices:
            percentage = (choice.vote_count / total_votes * 100) if total_votes > 0 else 0
            results.append({
                'choice': choice.text,
                'votes': choice.vote_count,
                'percentage': round(percentage, 2)
            })
        return results

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name='Вопрос')
    text = models.CharField(max_length=200, verbose_name="Текст варианта")

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"

    def __str__(self):
        return f"{self.question.title} - {self.text}"

class Vote(models.Model):
    user = models.ForeignKey(ProfileUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, verbose_name="Выбор")
    voted_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата голосования")

    class Meta:
        unique_together = ('user', 'choice')
        verbose_name = "Голос"
        verbose_name_plural = "Голоса"

    def __str__(self):
        return f"{self.user.username} -> {self.choice.text}"