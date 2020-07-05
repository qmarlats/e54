import pandas as pd
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import BaseModel


class Location(BaseModel):
    # Name
    name = models.CharField(_("name"), max_length=50)

    # Coordinates
    latitude = models.DecimalField(
        _("latitude"), max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        _("longitude"), max_digits=9, decimal_places=6, blank=True, null=True
    )

    class Meta:
        verbose_name = _("location")
        verbose_name_plural = _("locations")

    def __str__(self):
        return self.name
