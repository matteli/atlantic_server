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
)

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"planes", PlaneViewSet)

planes_router = routers.NestedSimpleRouter(router, r"planes", lookup="plane")
planes_router.register(r"pages", PageViewSet, basename="page")
planes_router.register(r"cameras", CameraViewSet, basename="camera")
planes_router.register(r"tours", TourViewSet, basename="tour")

pages_router = routers.NestedSimpleRouter(planes_router, r"pages", lookup="page")
pages_router.register(r"comments", CommentViewSet, basename="comment")


urlpatterns = [
    path("auth/refresh", auth_refresh),
    path("auth/user", auth_user),
    path("auth/login", auth_login),
    path("auth/logout", auth_logout),
]

urlpatterns += router.urls
urlpatterns += planes_router.urls
urlpatterns += pages_router.urls
