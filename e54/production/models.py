import numpy as np
import pandas as pd

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import BaseModel
from locations.models import Location

from .api import ReseauxEnergies


class Production(BaseModel):
    # Date and time and location
    datetime = models.DateTimeField(_("date and time"), db_index=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    # Production source
    bioenergy = models.PositiveIntegerField(_("bioenergy"), blank=True, null=True)
    hydro = models.PositiveIntegerField(_("hydro"), blank=True, null=True)
    nuclear = models.PositiveIntegerField(_("nuclear"), blank=True, null=True)
    pumped = models.PositiveIntegerField(_("pumped"), blank=True, null=True)
    solar = models.PositiveIntegerField(_("solar"), blank=True, null=True)
    thermal = models.PositiveIntegerField(_("thermal"), blank=True, null=True)
    wind = models.PositiveIntegerField(_("wind"), blank=True, null=True)
    total = models.PositiveIntegerField(_("total"), blank=True, null=True)

    class Meta:
        abstract = True

    @classmethod
    def from_eco2mix(cls, data, location):
        if isinstance(data, pd.Series):
            return cls(
                datetime=pd.Timestamp(data["date_heure"], tz=settings.TIME_ZONE),
                bioenergy=data["bioenergies"],
                hydro=data["hydraulique"],
                nuclear=data["nucleaire"],
                pumped=data["pompage"],
                solar=data["solaire"],
                thermal=data["thermique"],
                wind=data["eolien"],
                total=data["consommation"],
                location=location,
            )


class ProductionHistoricalData(Production):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["datetime", "location"],
                name="unique_production_historical_data",
            )
        ]
        default_related_name = "production_historical_data"

    @classmethod
    def download_from_eco2mix(
        cls, location, insee_code, starting_date, ending_date, commit=True
    ):
        # Initialize Dark Sky API
        reseauxenergies = ReseauxEnergies()

        # Starting and ending dates
        starting_date = pd.Timestamp(starting_date).date().isoformat()
        ending_date = pd.Timestamp(ending_date).date().isoformat()
        date_filter = f"date_heure IN [date'{starting_date}' TO date'{ending_date}']"

        # Regions
        region_filter = f"code_insee_region={insee_code}"

        # Final "where" filter
        where_filters = f"{date_filter} AND ({region_filter})"

        # Parameters for the API call
        parameters = {
            "where": where_filters,
            "timezone": settings.TIME_ZONE,
            "rows": "-1",
            "sort": "date_heure",
        }

        # Prepare requests
        reseauxenergies.export_eco2mix_regional_consumption(**parameters)

        # Fetch data
        responses = reseauxenergies.fetch()

        # Build DataFrame from responses
        data = pd.DataFrame(responses[0].json)

        # Clean data
        data.drop_duplicates("date_heure", inplace=True)
        data.fillna(value=np.nan, inplace=True)
        data["bioenergies"].clip(0, inplace=True)
        data["hydraulique"].clip(0, inplace=True)
        data["nucleaire"].clip(0, inplace=True)
        data["pompage"].clip(0, inplace=True)
        data["solaire"].clip(0, inplace=True)
        data["thermique"].clip(0, inplace=True)
        data["eolien"].clip(0, inplace=True)
        data["consommation"].clip(0, inplace=True)
        data.replace({np.nan: None}, inplace=True)

        # Build HistoricalData from DataFrame
        records = [
            cls.from_eco2mix(row[1], location=location) for row in data.iterrows()
        ]

        # Save data
        if commit:
            ProductionHistoricalData.objects.bulk_create(records, ignore_conflicts=True)
