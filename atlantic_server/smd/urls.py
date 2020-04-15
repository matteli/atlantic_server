from rest_framework_nested import routers
from .views import (
    DocViewSet,
    DocPlaneViewSet,
    FileViewSet,
    PlaneFileViewSet,
)

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"docs", DocViewSet, basename="doc")

docs_router = routers.NestedSimpleRouter(router, r"docs", lookup="doc")
docs_router.register(r"planes", DocPlaneViewSet, basename="plane")
docs_router.register(r"files", FileViewSet, basename="file")

docs_planes_router = routers.NestedSimpleRouter(docs_router, r"planes", lookup="plane")
docs_planes_router.register(r"files", PlaneFileViewSet, basename="file")

urlpatterns = []
urlpatterns += router.urls
urlpatterns += docs_router.urls
urlpatterns += docs_planes_router.urls
