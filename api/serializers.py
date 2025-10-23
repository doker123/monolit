# api/serializers.py (или app/serializers.py, в зависимости от структуры)

from rest_framework import serializers
from app.models import Question, Choice, Vote, ProfileUser # Убедитесь, что путь к моделям правильный

# Исправлено: имя класса изменено с ProfileSerializer на ProfileUserSerializer
# чтобы соответствовать использованию в VoteSerializer
class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'is_activated', 'send_messages')

# Убедитесь, что ChoiceSerializer определён до VoteSerializer
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'question', 'text')

# VoteSerializer использует ProfileUserSerializer и ChoiceSerializer
class VoteSerializer(serializers.ModelSerializer):
    # Теперь используем правильное имя ProfileUserSerializer
    user = ProfileUserSerializer(read_only=True)
    choice = ChoiceSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = ('id', 'user', 'choice', 'voted_at')

class QuestionCreateUpdateSerializer(serializers.ModelSerializer):
    choices_text = serializers.ListField(
        child=serializers.CharField(max_length=200),
        allow_empty=False,
        max_length=5,
        write_only=True,
        help_text="Список текстов вариантов ответа (максимум 5)."
    )

    class Meta:
        model = Question
        # Поля модели, которые можно изменять через API
        fields = ['id', 'title', 'short_description', 'full_description', 'image', 'expires_at', 'choices_text']

    def create(self, validated_data):
        choices_text = validated_data.pop('choices_text')
        question = Question.objects.create(**validated_data)
        for text in choices_text:
            Choice.objects.create(question=question, text=text)
        return question

    def update(self, instance, validated_data):
        choices_text = validated_data.pop('choices_text', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if choices_text is not None:
            instance.choices.all().delete()
            for text in choices_text:
                Choice.objects.create(question=instance, text=text)
        return instance

# Убедитесь, что QuestionSerializer определён до QuestionReadSerializer,
# если QuestionReadSerializer будет его использовать (хотя в данном коде - нет)
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

# Добавлен сериализатор для чтения вопроса, как в предыдущем примере
class QuestionReadSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    user_has_voted = serializers.SerializerMethodField()
    results = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'title', 'short_description', 'full_description', 'image', 'created_at', 'expires_at', 'is_expired', 'choices', 'user_has_voted', 'results']

    def get_user_has_voted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Vote.objects.filter(user=request.user, choice__question=obj).exists()
        return False

    def get_results(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and self.get_user_has_voted(obj):
            return obj.get_results()
        return None