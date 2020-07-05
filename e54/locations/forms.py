from django import forms

from core.form_helpers import CreateFormHelper, UpdateFormHelper

from .models import Location


class LocationForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = Location


class LocationCreateForm(LocationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = CreateFormHelper()


class LocationUpdateForm(LocationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form Helper
        self.helper = UpdateFormHelper()
