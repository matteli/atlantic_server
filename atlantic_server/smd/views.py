import re
import os
from lxml import etree
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import DocSerializer, FileSerializer
from .models import Doc, File
from .gitdoc import Repo


class DocViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocSerializer
    queryset = Doc.objects.all()
    lookup_field = "slug_model_plane"


class DocRefViewSet(viewsets.ViewSet):
    def list(self, request, doc_slug_model_plane=None):
        branches = Repo(doc_slug_model_plane).list_branches()
        return Response(branches, status=HTTP_200_OK)

    def create(self, request, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk=None, doc_slug_model_plane=None):
        if Repo(doc_slug_model_plane).branch_exist(pk):
            return Response(pk, status=HTTP_200_OK)
        else:
            return Response(pk, status=HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def partial_update(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)


class DocRefFileViewSet(viewsets.ViewSet):
    def init_xml_doc(self, type, dm_code):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        parser = etree.XMLParser(remove_blank_text=True)
        if type == "xpro":
            root = etree.parse(base_dir + "/documents/procedure.xml", parser)
            node = root.xpath("//dmCode")
            node[0].set("modelIdentCode", dm_code["modelIdentCode"])
            node[0].set("systemDiffCode", dm_code["systemDiffCode"])
            node[0].set("systemCode", dm_code["systemCode"])
            node[0].set("subSystemCode", dm_code["subSystemCode"])
            node[0].set("subSubSystemCode", dm_code["subSubSystemCode"])
            node[0].set("assyCode", dm_code["assyCode"])
            node[0].set("disassyCode", dm_code["disassyCode"])
            node[0].set("disassyCodeVariant", dm_code["disassyCodeVariant"])
            node[0].set("infoCode", dm_code["infoCode"])
            node[0].set("infoCodeVariant", dm_code["infoCodeVariant"])
            node[0].set("itemLocationCode", dm_code["itemLocationCode"])
        xml_str = etree.tostring(
            root, encoding="unicode", method="xml", pretty_print=True,
        )
        return xml_str

    def format_xml(self, xml_str):
        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.fromstring(bytes(xml_str, encoding="utf8"), parser=parser)
        return etree.tostring(
            root,
            encoding="unicode",
            method="xml",
            doctype='<?xml version="1.0" encoding="UTF-8"?>',
            pretty_print=True,
        )

    def list(self, request, doc_slug_model_plane=None, reference_pk=None):
        files = Repo(doc_slug_model_plane).list_files(reference_pk)
        blobs = list(map(lambda d: d.get("blob_id"), files))
        queryset = File.objects.filter(blob_id__in=blobs)
        response = FileSerializer(queryset, many=True).data
        for resp in response:
            for file in files:
                if file["blob_id"] == resp["blob_id"]:
                    resp["filename"] = file["filename"]
                    break
        return Response(response, status=HTTP_200_OK)

    def create(self, request, doc_slug_model_plane=None, reference_pk=None):
        dm_code = {
            "modelIdentCode": doc_slug_model_plane.upper(),
            "systemDiffCode": self.request.data["systemDiffCode"],
            "systemCode": self.request.data["systemCode"],
            "subSystemCode": self.request.data["subSystemCode"],
            "subSubSystemCode": self.request.data["subSubSystemCode"],
            "assyCode": self.request.data["assyCode"],
            "disassyCode": f"{int(self.request.data['disassyCode']):02d}",
            "disassyCodeVariant": f"{int(self.request.data['disassyCodeVariant']):01d}",
            "infoCode": self.request.data["infoCode"],
            "infoCodeVariant": self.request.data["infoCodeVariant"],
            "itemLocationCode": self.request.data["itemLocationCode"],
        }
        type = self.request.data["type"]
        filename = (
            f"{dm_code['modelIdentCode']}-"
            f"{dm_code['systemDiffCode']}-"
            f"{dm_code['systemCode']}-"
            f"{dm_code['subSystemCode']}-"
            f"{dm_code['assyCode']}-"
            f"{dm_code['disassyCode']}"
            f"{dm_code['disassyCodeVariant']}-"
            f"{dm_code['infoCode']}"
            f"{dm_code['infoCodeVariant']}-"
            f"{dm_code['itemLocationCode']}.XML"
        )
        content = self.init_xml_doc(type, dm_code)
        ids = Repo(doc_slug_model_plane).commit_file(
            filename,
            content,
            str(self.request.user),
            self.request.user.email,
            branch_name=reference_pk,
        )
        if ids["blob_id"]:
            meta = {
                "blob_id": ids["blob_id"],
                "doc": doc_slug_model_plane,
                # "editor": self.request.user,  # .pk,
                "type": type,
            }
            serializer = FileSerializer(data=meta)
            if serializer.is_valid():
                file = serializer.save(editor=self.request.user)
                return Response(
                    {
                        "meta": FileSerializer(file).data,
                        "filename": filename,
                        "content": content,
                    },
                    status=HTTP_200_OK,
                )
        return Response({}, status=HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, doc_slug_model_plane=None, reference_pk=None):
        filename = re.sub(r"-(?!.*-)", ".", pk).upper()
        blob = Repo(doc_slug_model_plane).get_blob_by_name(reference_pk, filename)
        if blob["blob_id"]:
            queryset = File.objects.get(pk=blob["blob_id"])
            meta = FileSerializer(queryset).data
            return Response(
                {
                    "meta": meta,
                    "commit": blob["commit_id"],
                    "content": blob["blob_content"],
                },
                status=HTTP_200_OK,
            )
        return Response({}, status=HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, doc_slug_model_plane=None, reference_pk=None):
        filename = re.sub(r"-(?!.*-)", ".", pk).upper()
        content = self.format_xml(self.request.data["content"])
        commit_id = self.request.data["commit"]
        meta = self.request.data["meta"]

        ids = Repo(doc_slug_model_plane).commit_file(
            filename,
            content,
            str(self.request.user),
            self.request.user.email,
            branch_name=reference_pk,
            parent_commit_id=commit_id,
        )
        if ids["blob_id"]:
            meta["doc"] = doc_slug_model_plane
            # meta["editor"] = self.request.user  # .pk
            meta["blob_id"] = ids["blob_id"]
            serializer = FileSerializer(data=meta)
            if serializer.is_valid():
                file = serializer.save(editor=self.request.user)
                return Response(
                    {
                        "meta": FileSerializer(file).data,
                        "commit": ids["commit_id"],
                        "content": content,
                    },
                    status=HTTP_200_OK,
                )
        return Response({}, status=HTTP_400_BAD_REQUEST)

    def partial_update(
        self, request, pk=None, doc_slug_model_plane=None, reference_pk=None
    ):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None, doc_slug_model_plane=None, reference_pk=None):
        return Response({}, status=HTTP_403_FORBIDDEN)


class FileViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def create(self, request, doc_slug_model_plane=None):
        """
        {"filename":"essai.md","branch":"all","content":"coucou"}
        """
        filename = re.sub(r"-(?!.*-)", ".", self.request.data["filename"])
        content = self.request.data["content"]
        commit = Repo(doc_slug_model_plane).commit_file(
            filename,
            content,
            str(self.request.user),
            self.request.user.email,
            branch_name=self.request.data["branch"],
        )
        if commit:
            return Response(content, status=HTTP_200_OK)
        else:
            return Response({}, status=HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, doc_slug_model_plane=None):
        content = Repo(doc_slug_model_plane).get_content_by_id(pk)
        if content:
            return Response(content, status=HTTP_200_OK)
        else:
            return Response({}, status=HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def partial_update(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None, doc_slug_model_plane=None):
        return Response({}, status=HTTP_403_FORBIDDEN)
