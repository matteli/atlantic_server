import csv

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from .const import NATURE_CHOICES, PROGRESS_CHOICES
from . import gitdoc as gd
from django.template.defaultfilters import slugify


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
    # manufacturer = models.CharField(max_length=100, blank=True)
    # model = models.CharField(max_length=100, blank=True)
    modelPlane = models.ForeignKey(
        ModelPlane, on_delete=models.SET_NULL, blank=True, null=True
    )
    msn = models.IntegerField()

    def __str__(self):
        return self.registration


class Camera(models.Model):
    name = models.CharField(max_length=100)
    xpos = models.FloatField()
    ypos = models.FloatField()
    zpos = models.FloatField()
    xtarget = models.FloatField()
    ytarget = models.FloatField()
    ztarget = models.FloatField()
    zoom = models.FloatField(default=1.0)
    view = models.IntegerField(
        default=0
    )  # 0 not in globalview. >=1 give order in the list
    plane = models.ForeignKey(Plane, on_delete=models.CASCADE)


class Page(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    ATA = models.IntegerField()
    title = models.CharField(max_length=200)
    nature = models.CharField(max_length=1, choices=NATURE_CHOICES, default="O")
    progress = models.CharField(max_length=1, choices=PROGRESS_CHOICES, default="O")
    plane = models.ForeignKey(Plane, on_delete=models.CASCADE)
    tour = models.IntegerField(default=0)
    camera = models.OneToOneField(
        Camera, null=True, blank=True, on_delete=models.CASCADE
    )


class Comment(models.Model):
    class Meta:
        ordering = ["edited"]

    page = models.ForeignKey(Page, related_name="comments", on_delete=models.CASCADE)
    edited = models.DateTimeField(auto_now_add=True)
    editor = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    text = models.TextField(blank=True)
    progress = models.CharField(max_length=1, choices=PROGRESS_CHOICES, blank=True)
    image = models.TextField(blank=True)


class Doc(models.Model):
    model_plane = models.OneToOneField(ModelPlane, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        reponame = slugify(str(self.model_plane))
        gd.init_repo(reponame)
        gd.commit_file(
            reponame,
            "readme.md",
            "These documents were produced by Atlantic",
            "Matthieu Nué",
            "matthieu.nue@gmail.com",
            "First commit",
            first_commit=True,
        )
