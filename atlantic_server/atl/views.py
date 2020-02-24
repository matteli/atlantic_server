import os, re

from django.contrib.auth import authenticate
from django.db.models import Max

from rest_framework.authtoken.models import Token
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS,
    BasePermission,
)
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_200_OK,
)
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.renderers import JSONRenderer

from django_filters import rest_framework as filters

from .models import Plane, Page, Comment, Camera, Doc, File
from .serializers import (
    PlaneSerializer,
    PageSerializer,
    UserSerializer,
    ListPageSerializer,
    CommentSerializer,
    CameraSerializer,
    DocSerializer,
    ListFileSerializer,
)
from . import gitdoc as gd
from .const import PROGRESS_CHOICES, NATURE_CHOICES


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


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
    permission_classes = (IsAuthenticatedOrReadOnly,)

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


class TourViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PageSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PageFilter

    def get_queryset(self):
        return Page.objects.filter(
            plane__registration=self.kwargs["plane_registration"]
        ).filter(tour__gt=0)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

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
    permission_classes = (IsAdminUser | ReadOnly,)

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


class DocViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocSerializer
    queryset = Doc.objects.all()
    lookup_field = "slug_model_plane"

    # def get_object(self):
    #    return Doc.objects.get(slug_model_plane=self.kwargs["pk"])


class DocPlaneViewSet(viewsets.ViewSet):
    def list(self, request, doc_slug_model_plane=None):
        l = gd.list_branches(doc_slug_model_plane)
        return Response(l, status=HTTP_200_OK)

    def create(self, request, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk=None, doc_slug_model_plane=None):
        b = gd.branch_exist(doc_slug_model_plane, pk)
        if b:
            return Response(b, status=HTTP_200_OK)
        else:
            return Response(b, status=HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def partial_update(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)


class PlaneFileViewSet(viewsets.ViewSet):
    def list(self, request, doc_slug_model_plane=None, plane_pk=None):
        list_file = gd.list_files(
            self.kwargs["doc_slug_model_plane"], self.kwargs["plane_pk"]
        )
        list_hash = list(map(lambda d: d.get("hash"), list_file))
        queryset = File.objects.filter(hash__in=list_hash)
        resp = ListFileSerializer(queryset, many=True).data
        for r in resp:
            for l in list_file:
                if l["hash"] == r["hash"]:
                    r["title"] = l["title"]
                    break

        return Response(resp, status=HTTP_200_OK)

    def create(self, request, doc_slug_model_plane=None, plane_pk=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk=None, doc_slug_model_plane=None, plane_pk=None):
        filename = re.sub(r"-(?!.*-)", ".", self.kwargs["pk"])
        b = gd.get_content_by_name(
            self.kwargs["doc_slug_model_plane"], self.kwargs["plane_pk"], filename,
        )
        if b:
            return Response(b, status=HTTP_200_OK)
        else:
            return Response(b, status=HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, doc_slug_model_plane=None, plane_pk=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def partial_update(
        self, request, pk=None, doc_slug_model_plane=None, plane_pk=None
    ):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None, doc_slug_model_plane=None, plane_pk=None):
        return Response({}, status=HTTP_403_FORBIDDEN)


class FileViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def create(self, request, doc_slug_model_plane=None):
        """
        {"filename":"essai.md","branch":"all","content":"coucou"}
        """
        c = gd.commit_file(
            doc_slug_model_plane,
            request.data["filename"],
            request.data["content"],
            str(self.request.user),
            # "m@m.fr",
            self.request.user.email,
            branch_name=request.data["branch"],
        )
        if c:
            return Response({"commit": c}, status=HTTP_200_OK)
        else:
            return Response({}, status=HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, doc_slug_model_plane=None):
        d = gd.get_content_by_hash(doc_slug_model_plane, pk)
        return Response(d, status=HTTP_200_OK)

    def update(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def partial_update(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None, doc_slug_model_plane=None):
        pass
