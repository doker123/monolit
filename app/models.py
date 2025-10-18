from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.dispatch import Signal
from django.db.models import Count

# Сигнал, отправляемый при регистрации нового пользователя
user_registered = Signal()

# модель пользователя с моими доп полями
class ProfileUser(AbstractUser):
    # Поле для хранения аватара пользователя (обязательное)
    avatar = models.ImageField( upload_to='avatars/', null=False, blank=False, verbose_name="Аватар")
    # Поле для отслеживания статуса активации пользователя
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прощёл активацию')
    # Поле для определения, нужно ли отправлять пользователю сообщения
    send_messages = models.BooleanField(default=True, verbose_name="Оповешать о новых сообщениях")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

# Модель для вопроса (например, для голосования)
class Question(models.Model):
    # Заголовок вопроса
    title = models.CharField(max_length=200, verbose_name="Заголовок вопроса")
    # Краткое описание вопроса
    short_description = models.TextField(max_length=500, verbose_name="Краткое описания")
    # Полное описание вопроса
    full_description = models.TextField(verbose_name="Полное описание")
    # Изображение, связанное с вопросом (необязательное)
    image = models.ImageField(upload_to='question_images/', blank=True, null=True, verbose_name="Фото для вопроса")
    # Дата и время создания вопроса (автоматически заполняется)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания голосования")
    # Дата и время окончания голосования
    expires_at = models.DateTimeField(verbose_name="Дата окончания голосования")

    # Метод для получения результатов голосования по данному вопросу
    def get_results(self):
        # Получаем варианты ответа, подсчитываем количество голосов за каждый
        choices = self.choices.annotate(vote_count=Count('vote')).order_by('-vote_count')
        # Считаем общее количество голосов
        total_votes = sum(choice.vote_count for choice in choices)
        results = []
        # Вычисляем процент голосов за каждый вариант
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

    # Свойство, показывающее, истекло ли время голосования
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    # Переопределяем метод save, чтобы автоматически установить срок окончания голосования
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Если срок окончания не установлен, устанавливаем его на 7 дней от текущей даты
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

# Модель для варианта ответа на вопрос
class Choice(models.Model):
    # Связь с вопросом (один вопрос - много вариантов ответа)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name='Вопрос')
    # Текст варианта ответа
    text = models.CharField(max_length=200, verbose_name="Текст варианта")

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"

    def __str__(self):
        return f"{self.question.title} - {self.text}"

# Модель для голоса пользователя
class Vote(models.Model):
    # Связь с пользователем, который проголосовал
    user = models.ForeignKey(ProfileUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    # Связь с выбранным вариантом ответа
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, verbose_name="Выбор")
    # Дата и время голосования (автоматически заполняется)
    voted_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата голосования")

    class Meta:
        # Ограничение: один пользователь может голосовать за один вариант только один раз
        unique_together = ('user', 'choice')
        verbose_name = "Голос"
        verbose_name_plural = "Голоса"

    def __str__(self):
        return f"{self.user.username} -> {self.choice.text}"