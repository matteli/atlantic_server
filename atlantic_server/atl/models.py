from django.db import models
from ..com.const import NATURE_CHOICES, PROGRESS_CHOICES
from ..com.models import Plane, User
from ..com.models import get_sentinel_user


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
