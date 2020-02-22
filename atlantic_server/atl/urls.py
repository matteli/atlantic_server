from django.urls import path

# from rest_framework import routers
from rest_framework_nested import routers
from .views import (
    auth_refresh,
    auth_user,
    auth_login,
    auth_logout,
    PlaneViewSet,
    PageViewSet,
    CommentViewSet,
    CameraViewSet,
    TourViewSet,
    DocViewSet,
    DocPlaneViewSet,
    FileViewSet,
    PlaneFileViewSet,
)

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"planes", PlaneViewSet)

planes_router = routers.NestedSimpleRouter(router, r"planes", lookup="plane")
planes_router.register(r"pages", PageViewSet, basename="page")
planes_router.register(r"cameras", CameraViewSet, basename="camera")
planes_router.register(r"tours", TourViewSet, basename="tour")

planes_pages_router = routers.NestedSimpleRouter(planes_router, r"pages", lookup="page")
planes_pages_router.register(r"comments", CommentViewSet, basename="comment")

router.register(r"docs", DocViewSet, basename="doc")

docs_router = routers.NestedSimpleRouter(router, r"docs", lookup="doc")
docs_router.register(r"planes", DocPlaneViewSet, basename="plane")
docs_router.register(r"files", FileViewSet, basename="file")

docs_planes_router = routers.NestedSimpleRouter(docs_router, r"planes", lookup="plane")
docs_planes_router.register(r"files", PlaneFileViewSet, basename="file")

urlpatterns = [
    path("auth/refresh", auth_refresh),
    path("auth/user", auth_user),
    path("auth/login", auth_login),
    path("auth/logout", auth_logout),
]

urlpatterns += router.urls
urlpatterns += planes_router.urls
urlpatterns += planes_pages_router.urls
urlpatterns += docs_router.urls
urlpatterns += docs_planes_router.urls
