from django.db import models
from django.utils.translation import ugettext_lazy as _


class BaseModel(models.Model):
    created_at = models.DateTimeField(_("creation date"), auto_now_add=True)
    updated_at = models.DateTimeField(_("update date"), auto_now=True)

    class Meta:
        abstract = True
