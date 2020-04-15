from django.db.models import Max

from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    BasePermission,
    SAFE_METHODS,
)
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from django_filters import rest_framework as filters

from ..com.models import Plane
from .models import Page, Comment, Camera
from .serializers import (
    PageSerializer,
    ListPageSerializer,
    CommentSerializer,
    CameraSerializer,
)
from ..com.const import PROGRESS_CHOICES, NATURE_CHOICES


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


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
