import csv
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


def import_csv_in_group(path, groupname):
    group = Group.objects.get(name=groupname)
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            if User.objects.filter(username=row[0]).exists():
                print("User " + row[0] + " already exist.")
            else:
                user = User.objects.create_user(
                    row[0],  # username
                    row[1],  # email
                    row[2],  # password
                    first_name=row[3],
                    last_name=row[4],
                )
                user.groups.add(group)


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="deleted")[0]


class User(AbstractUser):
    def natural_key(self):
        return self.first_name, self.last_name

    def __str__(self):
        return self.first_name + " " + self.last_name


class ModelPlane(models.Model):
    gltf = models.FileField(upload_to="planes/")
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if (
            ModelPlane.objects.filter(manufacturer=self.manufacturer)
            .filter(model=self.model)
            .exists()
        ):
            raise ValidationError("Manufacturer with model must be unique")

    def __str__(self):
        return "%s %s" % (self.manufacturer, self.model)


class Plane(models.Model):
    registration = models.CharField(max_length=10)
    modelPlane = models.ForeignKey(
        ModelPlane, on_delete=models.PROTECT, blank=True, null=True
    )
    msn = models.IntegerField()

    def __str__(self):
        return self.registration
