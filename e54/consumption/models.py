import datetime
import io

import numpy as np
import pandas as pd

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import BaseModel
from core.nn import NN
from core.public_holidays import FrancePublicHolidays
from locations.models import Location

from .api import RTE


class Consumption(BaseModel):
    # Date and time and location
    datetime = models.DateTimeField(_("date and time"), db_index=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    # Consumption source
    total = models.PositiveIntegerField(_("total"), blank=True, null=True)

    class Meta:
        abstract = True

    @classmethod
    def from_rte(cls, data, location):
        if isinstance(data, pd.Series):
            return cls(
                datetime=pd.Timestamp(data["start_date"], tz=settings.TIME_ZONE),
                total=data["value"],
                location=location,
            )


class ConsumptionHistoricalData(Consumption):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["datetime", "location"],
                name="unique_consumption_historical_data",
            )
        ]
        default_related_name = "consumption_historical_data"

    @classmethod
    def download_from_rte(cls, starting_date, ending_date, commit=True):
        # Get or create "France" Location
        location, _ = Location.objects.get_or_create(name="France")

        # Initialize Dark Sky API
        rte = RTE()

        # Prepare requests
        dates = pd.date_range(start=starting_date, end=ending_date)
        rte.get_consolidated_consumption(start_date=starting_date, end_date=ending_date)

        # Fetch data
        responses = rte.fetch()

        # Build DataFrame from responses
        data = pd.DataFrame(
            responses[0].json["consolidated_power_consumption"][0]["values"]
        )

        # Clean data
        data.drop_duplicates("start_date", inplace=True)
        data.fillna(value=np.nan, inplace=True)
        data["value"].clip(0, inplace=True)
        data.replace({np.nan: None}, inplace=True)

        # Build HistoricalData from DataFrame
        records = [cls.from_rte(row[1], location=location) for row in data.iterrows()]

        # Save data
        if commit:
            cls.objects.bulk_create(records, ignore_conflicts=True)


class ConsumptionForecast(Consumption):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["datetime", "location"], name="unique_consumption_forecast"
            )
        ]
        default_related_name = "consumption_forecasts"
