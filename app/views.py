from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .forms import ChangeUserInfoForm
from .models import ProfileUser, Question, Choice, Vote
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import CreateView
from .forms import RegisterUserForm
from django.views.generic.base import TemplateView
from django.views.generic import DeleteView
from django.contrib import messages
from django.views.generic import DetailView, ListView
from .forms import QuestionForm
# Представление для главной страницы
def index(request):
    # Отображает шаблон index.html
    return render(request, 'app/index.html')

# Представление для отображения других страниц
def other_page(request, page):
    try:
        # Пробует получить шаблон по указанному пути
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        # Если шаблон не найден, вызывает ошибку 404
        raise Http404
    # Отображает полученный шаблон
    return HttpResponse(template.render(request=request))

# Класс для представления страницы входа
class BBLoginView(LoginView):
    # Указывает шаблон для страницы входа
    template_name = 'app/login.html'

# Представление для профиля пользователя (требует аутентификации)
@login_required
def profile(request):
    # Отображает шаблон профиля
    return render(request, 'app/profile.html')

# Представление для выхода из системы
def logout_view(request):
    # Выполняет выход пользователя
    logout(request)
    # Перенаправляет на главную страницу
    return redirect('/')

# Класс для изменения информации пользователя
class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    # Модель, с которой работает представление
    model = ProfileUser
    # Шаблон для отображения формы
    template_name = 'app/change_user_info.html'
    # Форма, используемая для изменения данных
    form_class = ChangeUserInfoForm
    # URL для перенаправления после успешного обновления
    success_url = reverse_lazy('app:profile')
    # Сообщение об успешном обновлении
    success_message = 'Личные данные пользователя изменены.'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Инициализирует ID пользователя
        self.user_id = None

    # Метод для обработки запроса и получения ID текущего пользователя
    def dispatch(self, request,*args, **kwargs):
        self.user_id = request.user.id
        return super().dispatch(request,*args, **kwargs)

    # Метод для получения объекта пользователя, который нужно обновить
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        # Получает объект пользователя по ID
        return get_object_or_404(queryset, pk=self.user_id)

# Класс для изменения пароля пользователя
class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    # Шаблон для страницы изменения пароля
    template_name = 'app/password_change.html'
    # URL для перенаправления после успешного изменения пароля
    success_url = reverse_lazy('app:profile')
    # Сообщение об успешном изменении пароля
    success_message = 'Пороль пользователя изменён'

# Класс для регистрации нового пользователя
class RegisterUserView(CreateView):
    # Модель пользователя
    model = ProfileUser
    # Шаблон для регистрации
    template_name = 'app/register_user.html'
    # Форма регистрации
    form_class = RegisterUserForm
    # URL для перенаправления после успешной регистрации
    success_url = reverse_lazy('app:register_done')

# Класс для отображения страницы после успешной регистрации
class RegisterDoneView(TemplateView):
    # Шаблон для страницы "регистрация завершена"
    template_name = 'app/register_done.html'

# Класс для удаления пользователя
class DeleteUserView(LoginRequiredMixin, DeleteView):
    # Модель пользователя
    model = ProfileUser
    # Шаблон для подтверждения удаления
    template_name = 'app/delete-user.html'
    # URL для перенаправления после успешного удаления
    success_url = reverse_lazy('app:index')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Инициализирует ID пользователя
        self.user_id = None

    # Метод для обработки запроса и получения ID текущего пользователя
    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.id
        return super().dispatch(request, *args, **kwargs)

    # Метод, вызываемый при POST-запросе (удаление)
    def post(self, request, *args, **kwargs):
        # Выполняет выход пользователя перед удалением
        logout(request)
        # Добавляет сообщение об успешном удалении
        messages.add_message(request, messages.SUCCESS, 'Пользователь удалён')
        return super().post(request, *args, **kwargs)

    # Метод для получения объекта пользователя, который нужно удалить
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        # Получает объект пользователя по ID
        return get_object_or_404(queryset, pk=self.user_id)

# Класс для отображения списка вопросов
class QuestionListView(ListView):
    # Модель вопроса
    model = Question
    # Шаблон для отображения списка
    template_name = 'app/question_list.html'
    # Имя переменной в контексте шаблона для списка вопросов
    context_object_name = 'questions'

    # Метод для получения списка вопросов (только активные, отсортированные по дате создания)
    def get_queryset(self):
        return Question.objects.filter(expires_at__gt=timezone.now()).order_by('-created_at')

# Класс для отображения деталей вопроса
class QuestionDetailView(DetailView):
    # Модель вопроса
    model = Question
    # Шаблон для отображения деталей
    template_name = 'app/question_detail.html'
    # Имя переменной в контексте шаблона для объекта вопроса
    context_object_name = 'question'

    # Метод для добавления дополнительного контекста в шаблон
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()

        # Проверяет, голосовал ли текущий пользователь за этот вопрос
        user_has_voted = False
        if self.request.user.is_authenticated:
            user_has_voted = Vote.objects.filter(user=self.request.user, choice__question=question).exists()

        context["user_has_voted"] = user_has_voted
        # Если пользователь уже голосовал, добавляет результаты в контекст
        if user_has_voted:
                context['results'] = question.get_results()

        return context

# Представление для голосования за вопрос (требует аутентификации)
@login_required
def vote_view(request, pk):
    # Получает вопрос по ID, если не найден - ошибка 404
    question = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        # Получает ID выбранного варианта ответа из POST-данных
        choice_id = request.POST.get('choice')
        # Получает вариант ответа, связанный с этим вопросом
        choice = get_object_or_404(Choice, pk=choice_id, question=question)

        # Проверяет, голосовал ли пользователь уже за этот вопрос
        if Vote.objects.filter(user=request.user, choice__question=question).exists():
            # Если да, добавляет сообщение об ошибке
            messages.error(request, "Вы уже голосовали за этот вопрос.")
        else:
            # Если нет, создаёт новый голос
            Vote.objects.create(user=request.user, choice=choice)
            # Добавляет сообщение об успешном голосовании
            messages.success(request, "Спасибо за ваш голос!")

    # Перенаправляет обратно на страницу вопроса
    return redirect('app:question_detail', pk=question.pk)

# Представление для создания нового вопроса (требует аутентификации)
@login_required
def create_question_view(request):
    if request.method == 'POST':
        # Если метод POST, обрабатываем отправленные данные
        q_form = QuestionForm(request.POST, request.FILES)
        if q_form.is_valid():
            # Сохраняем вопрос
            question = q_form.save()

            # Создаём варианты ответа (до 5)
            for i in range(1, 6):
                choice_text = request.POST.get(f'choice_{i}')
                if choice_text:
                    Choice.objects.create(question=question, text=choice_text)
            # Перенаправляем на список вопросов
            return redirect('app:question_list')
    else:
        # Если метод GET, отображаем пустую форму
        q_form = QuestionForm()

    # Отображает шаблон создания вопроса
    return render(request, 'app/create_question.html', {'form': q_form})