from django.apps import AppConfig
from rest_framework.authentication import TokenAuthentication


class ComConfig(AppConfig):
    name = "atlantic_server.com"


class BearerAuthentication(TokenAuthentication):
    keyword = "Bearer"
