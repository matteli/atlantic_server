from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User,
    Plane,
    ModelPlane,
)

admin.site.register(User, UserAdmin)
admin.site.register(Plane)
admin.site.register(ModelPlane)
