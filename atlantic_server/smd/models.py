from django.db import models
from .gitdoc import init_repo
from ..com.models import User, ModelPlane, get_sentinel_user
from ..com.const import STATE_CHOICES


class Doc(models.Model):
    model_plane = models.OneToOneField(ModelPlane, on_delete=models.CASCADE)
    slug_model_plane = models.CharField(primary_key=True, max_length=210)

    def __str__(self):
        return self.slug_model_plane

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(
            force_insert, force_update, using, update_fields
        )  # Call the "real" save() method.
        repo_name = self.slug_model_plane
        repo = init_repo(repo_name)
        response = repo.commit_file(
            "README.MD",
            "These documents were produced by Atlantic",
            "Matthieu Nué",
            "matthieu.nue@gmail.com",
            "master",
            "First commit",
            first_commit=True,
        )
        """File.objects.create(
            blob_id=response["blob_id"],
            doc=self,
            editor=User.objects.filter(is_superuser=True).first(),
        )"""


class File(models.Model):
    blob_id = models.CharField(primary_key=True, max_length=40)
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    editor = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    type = models.CharField(
        max_length=4,
        choices=(
            ("raw", "Raw file"),
            ("md", "Markdown file"),
            ("xpro", "Procedure S1000D"),
        ),
        default="raw",
    )
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default="D",)
    hidden = models.BooleanField(default=False)
