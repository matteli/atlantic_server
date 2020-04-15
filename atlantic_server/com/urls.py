from django.urls import path
from .views import (
    auth_refresh,
    auth_user,
    auth_login,
    auth_logout,
)


urlpatterns = [
    path("auth/refresh", auth_refresh),
    path("auth/user", auth_user),
    path("auth/login", auth_login),
    path("auth/logout", auth_logout),
]
