from rest_framework_nested import routers
from .views import (
    DocViewSet,
    DocRefViewSet,
    FileViewSet,
    DocRefFileViewSet,
)

router = routers.SimpleRouter(trailing_slash=False)
# /docs/{pk}
router.register(r"docs", DocViewSet, basename="doc")

docs_router = routers.NestedSimpleRouter(router, r"docs", lookup="doc")
# /docs/{doc_slug_model_plane}/references/{pk}
docs_router.register(r"references", DocRefViewSet, basename="reference")
# /docs/{doc_slug_model_plane}/files/{pk}
docs_router.register(r"files", FileViewSet, basename="file")

docs_planes_router = routers.NestedSimpleRouter(
    docs_router, r"references", lookup="reference"
)
# /docs/{doc_slug_model_plane}/references/{reference_pk}/files/{pk}
docs_planes_router.register(r"files", DocRefFileViewSet, basename="file")

urlpatterns = []
urlpatterns += router.urls
urlpatterns += docs_router.urls
urlpatterns += docs_planes_router.urls
