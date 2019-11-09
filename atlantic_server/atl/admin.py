from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Plane, Page, Comment, Camera, ModelPlane, Manual


class PageAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


admin.site.register(User, UserAdmin)
admin.site.register(Plane)
admin.site.register(ModelPlane)
admin.site.register(Page, PageAdmin)
admin.site.register(Comment)
admin.site.register(Camera)
admin.site.register(Manual)
