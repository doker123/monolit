from django.urls import path
from .views import index, DeleteUserView
from .views import other_page
from .views import BBLoginView
from .views import profile
from .views import logout_view
from .views import ChangeUserInfoView
from .views import BBPasswordChangeView
from .views import RegisterUserView, RegisterDoneView, QuestionListView, QuestionDetailView, vote_view, create_question_view

# Название приложения, используется для namespace URL
app_name = 'app'

# Список маршрутов URL для приложения
urlpatterns = [
    # Маршрут для отображения других страниц (страницы, не попадающие под другие маршруты)
    # <str:page> - захватывает строку из URL и передаёт её в представление other_page
    path('<str:page>', other_page, name='other_page'),
    # Маршрут для главной страницы
    path('', index, name='index'),
    # Маршрут для страницы входа в систему
    path('accounts/login/', BBLoginView.as_view(), name='login'),
    # Маршрут для удаления профиля пользователя
    path('accounts/profile/delete', DeleteUserView.as_view(), name='profile_delete'),
    # Маршрут для изменения информации пользователя
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    # Маршрут для просмотра профиля пользователя
    path('accounts/profile/', profile, name='profile'),
    # Маршрут для страницы, отображающейся после успешной регистрации
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    # Маршрут для страницы регистрации пользователя
    path('app/accounts/register', RegisterUserView.as_view(), name='register'),
    # Маршрут для выхода из системы
    path('accounts/logout/', logout_view, name='logout'),
    # Маршрут для изменения пароля
    path('accounts/password/change/', BBPasswordChangeView.as_view(), name='password_change'),
    # Маршрут для списка вопросов
    path('question/', QuestionListView.as_view(), name='question_list'),
    # Маршрут для детального просмотра конкретного вопроса (pk - первичный ключ вопроса)
    path('question/<int:pk>/', QuestionDetailView.as_view(), name='question_detail'),
    # Маршрут для голосования за вариант ответа в конкретном вопросе
    path('question/<int:pk>/vote/', vote_view, name='vote'),
    # Маршрут для создания нового вопроса
    path('create/', create_question_view, name='create_question')
]