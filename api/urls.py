from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, vote_view
from django.conf.urls.static import static
from django.conf import settings

app_name = "api"

router = DefaultRouter()

router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path('', include(router.urls)),
    path('questions/<int:pk>/vote/', vote_view, name='vote-api'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)