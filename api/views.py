from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from app.models import Question, Choice, Vote, ProfileUser # Импортируем ваши модели
from .serializers import (
    QuestionSerializer,
    QuestionCreateUpdateSerializer,
    VoteSerializer,
    ProfileUserSerializer
) # Импортируем ваши сериализаторы

# Представление для модели ProfileUser (если нужно предоставить API для пользователей)
class UserViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = ProfileUser.objects.all()
    serializer_class = ProfileUserSerializer


# Представление для модели Question
class QuestionViewSet(viewsets.ModelViewSet):

    queryset = Question.objects.all()
    # Используем разные сериализаторы для разных действий
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return QuestionCreateUpdateSerializer # Для создания/обновления
        return QuestionSerializer # Для чтения (список, детали)


    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def results(self, request, pk=None):
        question = self.get_object() # Получаем объект Question по pk
        results_data = question.get_results() # Используем метод из модели
        return Response(results_data)


@api_view(['POST'])
def vote_view(request, pk):

    question = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        # Предполагаем, что ID варианта ответа передаётся в теле запроса JSON как 'choice'
        choice_id = request.data.get('choice') # Используем request.data вместо request.POST

        if not choice_id:
             return Response({'error': 'ID варианта ответа (choice) не предоставлен.'}, status=status.HTTP_400_BAD_REQUEST)

        choice = get_object_or_404(Choice, pk=choice_id, question=question)

        # Проверяем, голосовал ли пользователь уже за этот вопрос
        if Vote.objects.filter(user=request.user, choice__question=question).exists():
            return Response({'error': 'Вы уже голосовали за этот вопрос.'}, status=status.HTTP_400_BAD_REQUEST)

        # Создаём голос
        vote = Vote.objects.create(user=request.user, choice=choice)
        serializer = VoteSerializer(vote) # Сериализуем созданный голос (опционально)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Если метод не POST
    return Response({'error': 'Только POST-запросы разрешены для голосования.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

