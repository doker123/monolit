from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, vote_view

app_name = "api"

router = DefaultRouter()

router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path('', include(router.urls)),
    path('questions/<int:pk>/vote/', vote_view, name='vote-api'),
]