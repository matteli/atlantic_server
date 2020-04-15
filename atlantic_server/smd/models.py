from django.db import models
from . import gitdoc as gd
from ..com.models import User, ModelPlane, get_sentinel_user
from ..com.const import STATE_CHOICES


class Doc(models.Model):
    model_plane = models.OneToOneField(ModelPlane, on_delete=models.CASCADE)
    slug_model_plane = models.CharField(primary_key=True, max_length=210)

    def __str__(self):
        return self.slug_model_plane

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        reponame = self.slug_model_plane
        gd.init_repo(reponame)
        blob = gd.commit_file(
            reponame,
            "readme.md",
            "These documents were produced by Atlantic",
            "Matthieu Nué",
            "matthieu.nue@gmail.com",
            "all",
            "First commit",
            first_commit=True,
        )
        File.objects.create(
            hash=blob, doc=self, editor=User.objects.filter(is_superuser=True).first()
        )


class File(models.Model):
    hash = models.CharField(primary_key=True, max_length=40)
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    editor = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    permission = models.CharField(
        max_length=3, default="644"
    )  # UNIX like permission without execute (6 or 4 on 3 digit)
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default="D",)
    hidden = models.BooleanField(default=False)
