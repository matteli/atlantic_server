import re
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import DocSerializer, ListFileSerializer
from .models import Doc, File
from . import gitdoc as gd


class DocViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocSerializer
    queryset = Doc.objects.all()
    lookup_field = "slug_model_plane"


class DocPlaneViewSet(viewsets.ViewSet):
    def list(self, request, doc_slug_model_plane=None):
        branches = gd.list_branches(doc_slug_model_plane)
        return Response(branches, status=HTTP_200_OK)

    def create(self, request, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk=None, doc_slug_model_plane=None):
        branch = gd.branch_exist(doc_slug_model_plane, pk)
        if branch:
            return Response(branch, status=HTTP_200_OK)
        else:
            return Response(branch, status=HTTP_404_NOT_FOUND)

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
                    r["filename"] = l["filename"]
                    break
        print(resp)
        return Response(resp, status=HTTP_200_OK)

    def retrieve(self, request, pk=None, doc_slug_model_plane=None, plane_pk=None):
        filename = re.sub(r"-(?!.*-)", ".", self.kwargs["pk"])
        branch = gd.get_content_by_name(
            self.kwargs["doc_slug_model_plane"], self.kwargs["plane_pk"], filename,
        )
        if branch:
            return Response(branch, status=HTTP_200_OK)
        else:
            return Response(branch, status=HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, doc_slug_model_plane=None, plane_pk=None):
        filename = re.sub(r"-(?!.*-)", ".", self.kwargs["pk"])
        content = request.data["content"]
        hash_blob = gd.commit_file(
            doc_slug_model_plane,
            filename,
            content,
            str(self.request.user),
            self.request.user.email,
            branch_name=plane_pk,
        )
        if hash_blob:
            if not File.objects.filter(pk=hash_blob).exists():
                File.objects.create(
                    hash=hash_blob,
                    doc=Doc.objects.get(pk=doc_slug_model_plane),
                    editor=self.request.user,
                )
            return Response(content, status=HTTP_200_OK)
        else:
            return Response({}, status=HTTP_400_BAD_REQUEST)

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
        filename = re.sub(r"-(?!.*-)", ".", request.data["filename"])
        content = request.data["content"]
        c = gd.commit_file(
            doc_slug_model_plane,
            filename,
            content,
            str(self.request.user),
            # "m@m.fr",
            self.request.user.email,
            branch_name=request.data["branch"],
        )
        if c:
            return Response(content, status=HTTP_200_OK)
        else:
            return Response({}, status=HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, doc_slug_model_plane=None):
        content = gd.get_content_by_hash(doc_slug_model_plane, pk)
        if content:
            return Response(content, status=HTTP_200_OK)
        else:
            return Response({}, status=HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def partial_update(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None, doc_slug_model_plane=None):
        pass
