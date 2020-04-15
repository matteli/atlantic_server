from django.contrib import admin
from .models import (
    Page,
    Comment,
    Camera,
)


class PageAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


admin.site.register(Page, PageAdmin)
admin.site.register(Comment)
admin.site.register(Camera)
