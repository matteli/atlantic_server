from rest_framework import serializers
from .models import (
    Plane,
    User,
    ModelPlane,
)


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
