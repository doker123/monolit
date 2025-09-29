from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect
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

