from django.contrib import admin
from .models import channel_model,course,course_session
# Register your models here.
admin.site.register(channel_model)
admin.site.register(course)
admin.site.register(course_session)
