from django.contrib.auth import authenticate
from django.db.models import Max

# from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token

# from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_200_OK,
)
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters import rest_framework as filters

from .models import Plane, Page, Comment, Camera
from .serializers import (
    PlaneSerializer,
    PageSerializer,
    UserSerializer,
    ListPageSerializer,
    CommentSerializer,
    CameraSerializer,
    InstructionSheetSerializer,
)
from .const import PROGRESS_CHOICES, NATURE_CHOICES


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


class PageFilter(filters.FilterSet):
    nature = filters.MultipleChoiceFilter(choices=NATURE_CHOICES)
    progress = filters.MultipleChoiceFilter(choices=PROGRESS_CHOICES)

    class Meta:
        model = Page
        fields = ["nature", "progress"]


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PageFilter

    def get_serializer_class(self):
        if self.action == "list":
            return ListPageSerializer
        # elif self.action == 'retrieve':
        else:
            return PageSerializer

    def get_queryset(self):
        return Page.objects.filter(
            plane__registration=self.kwargs["plane_registration"]
        )

    def perform_create(self, serializer):
        plane = get_object_or_404(Plane, registration=self.kwargs["plane_registration"])
        serializer.validated_data["comments"]["editor"] = self.request.user
        serializer.save(plane=plane)


class TourViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PageFilter

    def get_queryset(self):
        return Page.objects.filter(
            plane__registration=self.kwargs["plane_registration"]
        ).filter(tour__gt=0)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(page__id=self.kwargs["page_pk"])

    def perform_create(self, serializer):
        page = get_object_or_404(Page, id=self.kwargs["page_pk"])
        comment = serializer.save(page=page, editor=self.request.user)
        page_updated = PageSerializer(
            page, data={"progress": comment.progress}, partial=True
        )
        if page_updated.is_valid():
            print("valid")
            page_updated.save()


class CameraViewSet(viewsets.ModelViewSet):
    serializer_class = CameraSerializer
    # permission_classes = (IsAdminUser,)

    def get_queryset(self):
        return (
            Camera.objects.filter(plane__registration=self.kwargs["plane_registration"])
            .filter(view__gt=0)
            .order_by("view")
        )

    def perform_create(self, serializer):
        plane = get_object_or_404(Plane, registration=self.kwargs["plane_registration"])
        max_view = Camera.objects.filter(
            plane__registration=self.kwargs["plane_registration"]
        ).aggregate(Max("view"))["view__max"]
        if max_view:
            view = int(max_view) + 1
        else:
            view = 1
        serializer.save(plane=plane, view=view)


class InstructionShetViewSet(viewsets.ModelViewSet):
    serializer_class = InstructionSheetSerializer
