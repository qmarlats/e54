import numpy as np
import pandas as pd

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import BaseModel
from locations.models import Location

from .api import DarkSky


class Weather(BaseModel):
    # Date and time and location
    datetime = models.DateTimeField(_("date and time"), db_index=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    # Atmosphere
    cloud_cover = models.DecimalField(
        _("cloud cover"), max_digits=3, decimal_places=2, blank=True, null=True
    )
    humidity = models.DecimalField(
        _("humidity"), max_digits=3, decimal_places=2, blank=True, null=True
    )
    pressure = models.DecimalField(
        _("pressure"), max_digits=6, decimal_places=2, blank=True, null=True
    )
    uv_index = models.PositiveSmallIntegerField(_("UV index"), blank=True, null=True)
    visibility = models.DecimalField(
        _("visibility"), max_digits=4, decimal_places=2, blank=True, null=True
    )

    # Precipitation
    precipitation_intensity = models.DecimalField(
        _("precipitation intensity"),
        max_digits=6,
        decimal_places=4,
        blank=True,
        null=True,
    )
    precipitation_probability = models.DecimalField(
        _("precipitation probability"),
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
    )
    precipitation_type = models.CharField(
        _("precipitation type"), max_length=5, blank=True, null=True
    )

    # Temperature
    apparent_temperature = models.DecimalField(
        _("apparent temperature"), max_digits=4, decimal_places=2, blank=True, null=True
    )
    dew_point = models.DecimalField(
        _("dew point"), max_digits=4, decimal_places=2, blank=True, null=True
    )
    temperature = models.DecimalField(
        _("temperature"), max_digits=4, decimal_places=2, blank=True, null=True
    )

    # Wind
    wind_bearing = models.PositiveSmallIntegerField(
        _("wind bearing"), blank=True, null=True
    )
    wind_gust = models.DecimalField(
        _("wind gust"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    wind_speed = models.DecimalField(
        _("wind speed"), max_digits=5, decimal_places=2, blank=True, null=True
    )

    class Meta:
        abstract = True

    @classmethod
    def from_darksky(cls, data, location):
        if isinstance(data, pd.Series):
            return cls(
                datetime=pd.Timestamp(data["time"], unit="s", tz=settings.TIME_ZONE),
                cloud_cover=data["cloudCover"],
                humidity=data["humidity"],
                pressure=data["pressure"],
                uv_index=data["uvIndex"],
                visibility=data["visibility"],
                precipitation_intensity=data["precipIntensity"],
                precipitation_probability=data["precipProbability"],
                precipitation_type=data["precipType"],
                apparent_temperature=data["apparentTemperature"],
                dew_point=data["dewPoint"],
                temperature=data["temperature"],
                wind_bearing=data["windBearing"],
                wind_gust=data["windGust"],
                wind_speed=data["windSpeed"],
                location=location,
            )


class WeatherHistoricalData(Weather):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["datetime", "location"], name="unique_weather_historical_data",
            )
        ]
        default_related_name = "weather_historical_data"

    @classmethod
    def download_from_darksky(cls, location, starting_date, ending_date, commit=True):
        # Initialize Dark Sky API
        darksky = DarkSky()

        # Prepare requests
        dates = pd.date_range(start=starting_date, end=ending_date)
        for date in dates:
            darksky.forecast(location.latitude, location.longitude, date)

        # Fetch data
        responses = darksky.fetch()

        # Build DataFrame from responses
        data = pd.DataFrame()
        for response in responses:
            data = data.append(response.json["hourly"]["data"])

        # Clean data
        data.drop_duplicates("time", inplace=True)
        data.fillna(value=np.nan, inplace=True)
        data["uvIndex"].clip(0, inplace=True)
        data["windBearing"].clip(0, inplace=True)
        data.replace({np.nan: None}, inplace=True)

        # Build HistoricalData from DataFrame
        records = [
            cls.from_darksky(row[1], location=location) for row in data.iterrows()
        ]

        # Save data
        if commit:
            WeatherHistoricalData.objects.bulk_create(records, ignore_conflicts=True)
