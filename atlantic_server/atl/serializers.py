from rest_framework import serializers
from django.db.models import Max
from .models import (
    Page,
    Plane,
    User,
    Comment,
    Camera,
    ModelPlane,
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


"""class RepoDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepoDoc
        fields = "__all__"


class FileDocSerializerRL(serializers.ModelSerializer):
    stream = serializers.SerializerMethodField()

    class Meta:
        model = FileDoc
        fields = "__all__"

    def get_stream(self, obj):
        return "coucou"


class FileDocSerializerCU(serializers.ModelSerializer):
    stream = serializers.CharField(write_only=True)

    class Meta:
        model = FileDoc
        fields = ("file", "stream")

    def update(self, instance, validated_data):
        gd.commit_file(
            validated_data.pop("stream"),
            validated_data["file"],
            "moi",
            "matthieu.nue@gmail.com",
            "other commit",
            str(validated_data["repodoc"].modelPlane),
            validated_data.pop("parent"),
        )
        filedoc = super().update(validated_data)
        return filedoc

    def create(self, validated_data):
        gd.commit_file(
            validated_data.pop("stream"),
            validated_data["file"],
            "moi",
            "matthieu.nue@gmail.com",
            "first commit",
            str(validated_data["repodoc"].modelPlane),
        )
        filedoc = super().create(validated_data)
        # fileDoc = FileDoc.objects.create(**validated_data)
        return filedoc"""
