import numpy as np
import pandas as pd

from django import forms

from core.form_helpers import (
    CreateFormHelper,
    DownloadFormHelper,
    ImportFormHelper,
    UpdateFormHelper,
)
from locations.models import Location

from .models import ProductionHistoricalData


class ProductionHistoricalDataCreateForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = ProductionHistoricalData

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = CreateFormHelper()

        # Form fields
        self.fields["location"].empty_label = None


class ProductionHistoricalDataDownloadForm(forms.Form):
    source = forms.ChoiceField(choices=[("eco2mix", "éCO2mix")])
    starting_date = forms.DateField(widget=forms.DateInput())
    ending_date = forms.DateField()
    insee_code = forms.ChoiceField(
        choices=[
            ("01", "Guadeloupe (01)"),
            ("02", "Martinique (02)"),
            ("03", "Guyane (03)"),
            ("04", "La Réunion (04)"),
            ("06", "Mayotte (06)"),
            ("11", "Île-de-France (11)"),
            ("24", "Centre-Val de Loire (24)"),
            ("27", "Bourgogne-Franche-Comté (27)"),
            ("28", "Normandie (28)"),
            ("32", "Hauts-de-France (32)"),
            ("44", "Grand Est (44)"),
            ("52", "Pays de la Loire (52)"),
            ("53", "Bretagne (53)"),
            ("75", "Nouvelle-Aquitaine (75)"),
            ("76", "Occitanie (76)"),
            ("84", "Auvergne-Rhône-Alpes (84)"),
            ("93", "Provence-Alpes-Côte d'Azur (93)"),
        ]
    )
    location = forms.ModelChoiceField(queryset=Location.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = DownloadFormHelper()

    def save(self):
        if self.cleaned_data["source"] == "eco2mix":
            ProductionHistoricalData.download_from_eco2mix(
                self.cleaned_data["location"],
                self.cleaned_data["insee_code"],
                self.cleaned_data["starting_date"],
                self.cleaned_data["ending_date"],
            )


class ProductionHistoricalDataImportForm(forms.Form):
    # WARNING: only éCO2mix is implemented at this time. Some
    # of the code is hard-coded for éCO2mix.
    source = forms.ChoiceField(choices=[("eCO2mix", "éCO2mix")])
    data = forms.FileField(widget=forms.widgets.FileInput)
    location = forms.ModelChoiceField(queryset=Location.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = ImportFormHelper()

    def save(self):
        # Read data
        data = pd.read_csv(self.files["data"])

        if self.cleaned_data["source"] == "eCO2mix":
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
            # WARNING: replacing NaN values with None must be done
            # at the end as it changes the data types
            data.replace({np.nan: None}, inplace=True)

            # Create ProductionHistoricalData objects
            # WARNING: this method is inefficient, data should be
            # directly written into the database withtout creating
            # ProductionHistoricalData objects (hence avoiding iterating over each
            # row of the DataFrame)
            # More informaton: https://stackoverflow.com/q/34425607
            records = [
                ProductionHistoricalData.from_eco2mix(
                    row[1], location=self.cleaned_data["location"]
                )
                for row in data.iterrows()
            ]

        ProductionHistoricalData.objects.bulk_create(records, ignore_conflicts=True)


class ProductionHistoricalDataUpdateForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = ProductionHistoricalData

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = UpdateFormHelper()

        # Form fields
        self.fields["location"].empty_label = None
