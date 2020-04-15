from rest_framework import serializers
from .models import Doc, File


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
