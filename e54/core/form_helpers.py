from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class CreateFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(
            Submit("submit", "Create", css_class="btn btn-primary btn-block")
        )


class UpdateFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(
            Submit("submit", "Update", css_class="btn btn-primary btn-block")
        )


class DownloadFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(
            Submit("submit", "Download", css_class="btn btn-primary btn-block")
        )


class ImportFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(
            Submit("submit", "Import", css_class="btn btn-primary btn-block")
        )


class ForecastFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(
            Submit("submit", "Forecast", css_class="btn btn-primary btn-block")
        )
