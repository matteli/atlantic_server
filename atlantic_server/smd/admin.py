from django.contrib import admin
from .models import (
    Doc,
    File,
)

admin.site.register(Doc)
admin.site.register(File)
