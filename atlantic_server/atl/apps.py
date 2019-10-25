from django.apps import AppConfig
from rest_framework.authentication import TokenAuthentication


class AtlConfig(AppConfig):
    name = "atlantic_server.atl"


class BearerAuthentication(TokenAuthentication):
    keyword = "Bearer"
