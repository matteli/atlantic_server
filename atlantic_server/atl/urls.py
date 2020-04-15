from rest_framework_nested import routers
from .views import (
    PageViewSet,
    CommentViewSet,
    CameraViewSet,
    TourViewSet,
)
from ..com.views import PlaneViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"planes", PlaneViewSet)

planes_router = routers.NestedSimpleRouter(router, r"planes", lookup="plane")
planes_router.register(r"pages", PageViewSet, basename="page")
planes_router.register(r"cameras", CameraViewSet, basename="camera")
planes_router.register(r"tours", TourViewSet, basename="tour")

planes_pages_router = routers.NestedSimpleRouter(planes_router, r"pages", lookup="page")
planes_pages_router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = []
urlpatterns += router.urls
urlpatterns += planes_router.urls
urlpatterns += planes_pages_router.urls
