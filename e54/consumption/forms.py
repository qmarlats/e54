import datetime

import numpy as np
import pandas as pd

from django import forms
from django.conf import settings

from consumption.api import RTE
from core.form_helpers import (
    CreateFormHelper,
    DownloadFormHelper,
    ForecastFormHelper,
    ImportFormHelper,
    UpdateFormHelper,
)
from locations.models import Location
from weather.api import DarkSky
from weather.models import Weather

from .forecasters import ConsumptionInFranceForecaster
from .models import ConsumptionHistoricalData, ConsumptionForecast


class ConsumptionHistoricalDataCreateForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = ConsumptionHistoricalData

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = CreateFormHelper()

        # Form fields
        self.fields["location"].empty_label = None


class ConsumptionHistoricalDataDownloadForm(forms.Form):
    source = forms.ChoiceField(choices=[("RTE", "RTE")])
    starting_date = forms.DateField(widget=forms.DateInput())
    ending_date = forms.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = DownloadFormHelper()

    def save(self):
        if self.cleaned_data["source"] == "RTE":
            ConsumptionHistoricalData.download_from_rte(
                self.cleaned_data["starting_date"],
                self.cleaned_data["ending_date"],
            )


class ConsumptionHistoricalDataImportForm(forms.Form):
    # WARNING: only RTE is implemented at this time. Some
    # of the code is hard-coded for RTE.
    source = forms.ChoiceField(choices=[("RTE", "RTE")])
    data = forms.FileField(widget=forms.widgets.FileInput)
    location = forms.ModelChoiceField(queryset=Location.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = ImportFormHelper()

    def save(self):
        # Read data
        data = pd.read_csv(self.files["data"])

        if self.cleaned_data["source"] == "RTE":
            # Clean data
            data.drop_duplicates("start_date", inplace=True)
            data.fillna(value=np.nan, inplace=True)
            data["value"].clip(0, inplace=True)
            # WARNING: replacing NaN values with None must be done
            # at the end as it changes the data types
            data.replace({np.nan: None}, inplace=True)

            # Create ConsumptionHistoricalData objects
            # WARNING: this method is inefficient, data should be
            # directly written into the database withtout creating
            # ConsumptionHistoricalData objects (hence avoiding iterating over each
            # row of the DataFrame)
            # More informaton: https://stackoverflow.com/q/34425607
            records = [
                ConsumptionHistoricalData.from_rte(
                    row[1], location=self.cleaned_data["location"]
                )
                for row in data.iterrows()
            ]

        ConsumptionHistoricalData.objects.bulk_create(records, ignore_conflicts=True)


class ConsumptionHistoricalDataUpdateForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = ConsumptionHistoricalData

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = UpdateFormHelper()

        # Form fields
        self.fields["location"].empty_label = None


class ConsumptionForecastCreateForm(forms.Form):
    forecaster = forms.ChoiceField(
        choices=[("ConsumptionInFrance", "Consumption in France",)]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = ForecastFormHelper()

    def save(self):
        if self.cleaned_data["forecaster"] == "ConsumptionInFrance":
            forecaster = ConsumptionInFranceForecaster()
            forecasts = forecaster.forecast()
            today = datetime.date.today()
            datetimes = pd.date_range(
                start=today + datetime.timedelta(days=1),
                end=today + datetime.timedelta(days=2),
                freq="30Min",
                tz=settings.TIME_ZONE,
            )[:-1]
            forecasts = pd.DataFrame({"datetime": datetimes, "total": forecasts[:, 0]})
            records = [
                ConsumptionForecast(**row[1], location=Location.objects.get(name="France"))
                for row in forecasts.iterrows()
            ]
            ConsumptionForecast.objects.bulk_create(records, ignore_conflicts=True)
