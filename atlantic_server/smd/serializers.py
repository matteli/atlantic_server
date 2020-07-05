from rest_framework import serializers
from .models import Doc, File
from ..com.models import User, ModelPlane


class DocSerializer(serializers.ModelSerializer):
    model_plane = serializers.StringRelatedField()

    class Meta:
        model = Doc
        fields = "__all__"


class ModelPlaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelPlane
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class FileSerializer(serializers.ModelSerializer):
    # editor = UserSerializer()
    # doc = ModelPlaneSerializer()
    editor = serializers.StringRelatedField()

    class Meta:
        model = File
        fields = ["blob_id", "doc", "editor", "type", "state", "hidden"]
