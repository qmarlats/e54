import numpy as np
import pandas as pd

from django import forms
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _

from core.form_helpers import (
    CreateFormHelper,
    DownloadFormHelper,
    ImportFormHelper,
    UpdateFormHelper,
)
from locations.models import Location

from .models import WeatherHistoricalData


class WeatherHistoricalDataCreateForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = WeatherHistoricalData

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = CreateFormHelper()

        # Form fields
        self.fields["location"].empty_label = None


class WeatherHistoricalDataDownloadForm(forms.Form):
    source = forms.ChoiceField(choices=[("DarkSky", "Dark Sky")])
    starting_date = forms.DateField(widget=forms.DateInput())
    ending_date = forms.DateField()
    location = forms.ModelChoiceField(queryset=Location.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = DownloadFormHelper()

    def save(self):
        if self.cleaned_data["source"] == "DarkSky":
            WeatherHistoricalData.download_from_darksky(
                self.cleaned_data["location"],
                self.cleaned_data["starting_date"],
                self.cleaned_data["ending_date"],
            )


class WeatherHistoricalDataImportForm(forms.Form):
    source = forms.ChoiceField(choices=[("DarkSky", "Dark Sky")])
    data = forms.FileField(widget=forms.widgets.FileInput)
    location = forms.ModelChoiceField(queryset=Location.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = ImportFormHelper()

    def save(self):
        # Read data
        data = pd.read_csv(self.files["data"])

        if self.cleaned_data["source"] == "DarkSky":
            # Clean data
            data.drop_duplicates("time", inplace=True)
            data.fillna(value=np.nan, inplace=True)
            data["uvIndex"].clip(0, inplace=True)
            data["windBearing"].clip(0, inplace=True)
            # WARNING: replacing NaN values with None must be done
            # at the end as it changes the data types
            data.replace({np.nan: None}, inplace=True)

            # Create WeatherHistoricalData objects
            # WARNING: this method is inefficient, data should be
            # directly written into the database withtout creating
            # WeatherHistoricalData objects (hence avoiding iterating over each
            # row of the DataFrame)
            # More informaton: https://stackoverflow.com/q/34425607
            records = [
                WeatherHistoricalData.from_darksky(
                    row[1], location=self.cleaned_data["location"]
                )
                for row in data.iterrows()
            ]

        WeatherHistoricalData.objects.bulk_create(records, ignore_conflicts=True)


class WeatherHistoricalDataUpdateForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = WeatherHistoricalData

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = UpdateFormHelper()

        # Form fields
        self.fields["location"].empty_label = None
