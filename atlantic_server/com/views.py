from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_200_OK,
)
from django.contrib.auth import authenticate
from .models import Plane
from .serializers import (
    PlaneSerializer,
    UserSerializer,
)


@api_view(["GET", "POST"])
@permission_classes((IsAuthenticated,))
def auth_refresh(request):
    return Response(
        {"token": request.auth.key},
        status=HTTP_200_OK,
        headers={"Authorization": request.auth.key},
    )


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def auth_logout(request):
    request.user.auth_token.delete()
    return Response({}, status=HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def auth_user(request):
    return Response({"data": UserSerializer(request.user).data}, status=HTTP_200_OK)


@api_view(["POST"])
def auth_login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response(
            {"error": "Please provide both username and password"},
            status=HTTP_400_BAD_REQUEST,
        )
    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {"error": "Bad password or username"}, status=HTTP_422_UNPROCESSABLE_ENTITY
        )
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {"token": token.key}, status=HTTP_200_OK, headers={"Authorization": token.key}
    )


class PlaneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plane.objects.all()
    serializer_class = PlaneSerializer
    lookup_field = "registration"
