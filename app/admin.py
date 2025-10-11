from django.contrib import admin
from .models import ProfileUser
from .models import Question

admin.site.register(ProfileUser)
admin.site.register(Question)


