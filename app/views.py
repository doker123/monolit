from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .forms import ChangeUserInfoForm
from .models import ProfileUser
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import CreateView
from .forms import RegisterUserForm
from django.views.generic.base import TemplateView
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