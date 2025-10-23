from rest_framework import serializers
from app.models import Question, Choice, Vote, ProfileUser


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'is_activated', 'send_messages')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'question', 'text')


class VoteSerializer(serializers.ModelSerializer):
    user = ProfileUser(read_only=True)
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

        # Метод, вызываемый при обновлении вопроса

    def update(self, instance, validated_data):

        choices_text = validated_data.pop('choices_text', None)

        # Обновляем основные поля вопроса
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Если были переданы тексты вариантов, обновляем их
        if choices_text is not None:
            # Сначала удаляем старые варианты
            instance.choices.all().delete()
            # Затем создаём новые
            for text in choices_text:
                Choice.objects.create(question=instance, text=text)

        return instance