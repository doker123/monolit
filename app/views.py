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
def index(request):
    return render(request, 'app/index.html')

def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))

class BBLoginView(LoginView):
    template_name = 'app/login.html'

@login_required
def profile(request):
    return render(request, 'app/profile.html')

def logout_view(request):
    logout(request)
    return redirect('/')

class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = ProfileUser
    template_name = 'app/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('app:profile')
    success_message = 'Личные данные пользователя изменены.'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = None

    def dispatch(self, request,*args, **kwargs):
        self.user_id = request.user.id
        return super().dispatch(request,*args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'app/password_change.html'
    success_url = reverse_lazy('app:profile')
    success_message = 'Пороль пользователя изменён'

class RegisterUserView(CreateView):
    model = ProfileUser
    template_name = 'app/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('app:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'app/register_done.html'

class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = ProfileUser
    template_name = 'app/delete-user.html'
    success_url = reverse_lazy('app:index')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = None

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.id
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удалён')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

class QuestionListView(ListView):
    model = Question
    template_name = 'app/question_list.html'
    context_object_name = 'questions'

    def get_queryset(self):
        return Question.objects.filter(expires_at__gt=timezone.now()).order_by('-created_at')

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'app/question_detail.html'
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()

        user_has_voted = False
        if self.request.user.is_authenticated:
            user_has_voted = Vote.objects.filter(user=self.request.user, choice__question=question).exists()

        context["user_has_voted"] = user_has_voted
        if user_has_voted:
                context['results'] = question.get_results()

        return context

@login_required
def vote_view(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        choice_id = request.POST.get('choice')
        choice = get_object_or_404(Choice, pk=choice_id, question=question)

        if Vote.objects.filter(user=request.user, choice__question=question).exists():
            messages.error(request, "Вы уже голосовали за этот вопрос.")
        else:
            Vote.objects.create(user=request.user, choice=choice)
            messages.success(request, "Спасибо за ваш голос!")

    return redirect('app:question_detail', pk=question.pk)

@login_required
def create_question_view(request):
    if request.method == 'POST':
        q_form = QuestionForm(request.POST, request.FILES)
        if q_form.is_valid():
            question = q_form.save()

            for i in range(1, 6):
                choice_text = request.POST.get(f'choice_{i}')
                if choice_text:
                    Choice.objects.create(question=question, text=choice_text)
            return redirect('app:question_list')
    else:
        q_form = QuestionForm()

    return render(request, 'app/create_question.html', {'form': q_form})