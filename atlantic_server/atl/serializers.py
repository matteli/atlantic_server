from rest_framework import serializers
from django.db.models import Max
from .models import (
    Page,
    Plane,
    User,
    Comment,
    Camera,
    ModelPlane,
    Doc,
    File,
)
import io
from . import gitdoc as gd


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "roles")
        read_only_fields = ("username", "first_name", "last_name", "roles")

    def get_roles(self, obj):
        if obj.is_staff:
            return ["admin"]
        else:
            return []


class ModelPlaneSerializer(serializers.ModelSerializer):
    gltf = serializers.FileField(use_url=False)

    class Meta:
        model = ModelPlane
        fields = "__all__"


class PlaneSerializer(serializers.ModelSerializer):
    modelPlane = ModelPlaneSerializer()

    class Meta:
        model = Plane
        fields = "__all__"


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        exclude = ("plane",)


class CameraPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        exclude = ("plane",)
        read_only_fields = ("name",)


class CommentSerializer(serializers.ModelSerializer):
    editor = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ("edited", "editor", "text", "progress", "image")
        read_only_fields = ("editor",)


class ListPageSerializer(serializers.ModelSerializer):
    camera = CameraPageSerializer()

    class Meta:
        model = Page
        fields = ("x", "y", "z", "nature", "progress", "id", "camera")


class PageSerializer(serializers.ModelSerializer):
    camera = CameraPageSerializer()
    comments = CommentSerializer()

    class Meta:
        model = Page
        fields = (
            "id",
            "x",
            "y",
            "z",
            "ATA",
            "title",
            "nature",
            "progress",
            "comments",
            "tour",
            "camera",
        )

    def validate_tour(self, tour):
        if tour == 0:
            return 0
        else:
            max_tour = Page.objects.all().aggregate(Max("tour"))["tour__max"]
            if max_tour:
                return int(max_tour) + 1
            else:
                return 1

    def create(self, validated_data):
        camera_data = validated_data.pop("camera")
        comment_data = validated_data.pop("comments")
        camera = Camera.objects.create(
            **camera_data, name=validated_data["title"], plane=validated_data["plane"]
        )
        page = Page.objects.create(camera=camera, **validated_data)
        Comment.objects.create(**comment_data, page=page, progress="O")
        return page


class DocSerializer(serializers.ModelSerializer):
    model_plane = serializers.StringRelatedField()

    class Meta:
        model = Doc
        fields = ("model_plane", "slug_model_plane")


class ListFileSerializer(serializers.ModelSerializer):
    editor = serializers.StringRelatedField()

    class Meta:
        model = File
        exclude = ["doc"]

    # def get_content(self, obj):
    #    return gd.get_content(obj.doc, obj.hash)


'''class CreateFileSerializer(serializers.ModelSerializer):
    editor = serializers.PrimaryKeyRelatedField()
    doc = serializers.PrimaryKeyRelatedField()
    content = serializers.CharField()

    class Meta:
        model = File
        fields = "__all__"'''
