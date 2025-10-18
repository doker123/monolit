from django.contrib import admin
from .models import ProfileUser
from .models import Question
# зарегистрировать в админке эти модели.
admin.site.register(ProfileUser)
admin.site.register(Question)


