from django.urls import path
from .views import index
from .views import other_page
from .views import BBLoginView
from .views import profile
from .views import logout_view
from .views import ChangeUserInfoView
from .views import BBPasswordChangeView

app_name = 'app'

urlpatterns = [
    path('<str:page>', other_page, name='other_page'),
    path('', index, name='index'),
    path('accounts/login', BBLoginView.as_view(), name='login'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/password/change/', BBPasswordChangeView.as_view(), name='password_change'),
]