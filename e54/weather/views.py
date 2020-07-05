import numpy as np
import plotly.offline as py

from django.db.models import Avg, Count
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.list import ListView
from plotly.graph_objs import Figure, Layout, Scatter

from .forms import (
    WeatherHistoricalDataCreateForm,
    WeatherHistoricalDataDownloadForm,
    WeatherHistoricalDataImportForm,
    WeatherHistoricalDataUpdateForm,
)
from .models import WeatherHistoricalData


class WeatherHistoricalDataListView(ListView):
    context_object_name = "historical_data"
    template_name = "weather/historical_data/list.html"

    def get_queryset(self):
        historical_data = WeatherHistoricalData.objects
        if "month" in self.kwargs:
            historical_data = historical_data.filter(
                datetime__year=self.kwargs["year"], datetime__month=self.kwargs["month"]
            )
            historical_data = historical_data.annotate(day=TruncDay("datetime")).values(
                "day"
            )
        elif "year" in self.kwargs:
            historical_data = historical_data.filter(datetime__year=self.kwargs["year"])
            historical_data = historical_data.annotate(
                month=TruncMonth("datetime")
            ).values("month")
        else:
            historical_data = historical_data.annotate(
                year=TruncYear("datetime")
            ).values("year")
        return (
            historical_data.annotate(records_count=Count("id"))
            .annotate(average_temperature=Avg("temperature"))
            .annotate(average_precipitation_intensity=Avg("precipitation_intensity"))
            .annotate(average_wind_speed=Avg("wind_speed"))
            .annotate(average_temperature=Avg("temperature"))
            .annotate(average_humidity=Avg("humidity"))
        )


class WeatherHistoricalDataCreateView(CreateView):
    form_class = WeatherHistoricalDataCreateForm
    model = WeatherHistoricalData
    success_url = reverse_lazy("weather:historical-data:list")
    template_name = "weather/historical_data/form.html"


class WeatherHistoricalDataDownloadView(FormView):
    form_class = WeatherHistoricalDataDownloadForm
    success_url = reverse_lazy("weather:historical-data:list")
    template_name = "weather/historical_data/form.html"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class WeatherHistoricalDataImportView(FormView):
    form_class = WeatherHistoricalDataImportForm
    success_url = reverse_lazy("weather:historical-data:list")
    template_name = "weather/historical_data/form.html"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class WeatherHistoricalDataDetailView(ListView):
    context_object_name = "records"
    template_name = "weather/historical_data/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Plotly config
        config = {
            "displaylogo": False,
        }

        # Datetime
        datetimes = np.array(self.object_list.values_list("datetime", flat=True))
        datetimes = [timezone.localtime(datetime) for datetime in datetimes]

        # Temperature
        temperature = np.array(self.object_list.values_list("temperature", flat=True))
        apparent_temperature = np.array(
            self.object_list.values_list("apparent_temperature", flat=True)
        )
        temperature_trace = Scatter(x=datetimes, y=temperature, name="Temperature")
        apparent_temperature_trace = Scatter(
            x=datetimes, y=apparent_temperature, name="Apparent Temperature"
        )
        temperature_data = [temperature_trace, apparent_temperature_trace]
        temperature_layout = Layout(
            xaxis={"title": "Time"}, yaxis={"title": "Temperature (°C)"}
        )
        temperature_figure = Figure(data=temperature_data, layout=temperature_layout)
        temperature_plot = py.plot(
            temperature_figure, auto_open=False, output_type="div", config=config
        )

        # Update context
        context["temperature_plot"] = temperature_plot

        return context

    def get_queryset(self):
        return WeatherHistoricalData.objects.filter(
            datetime__year=self.kwargs["year"],
            datetime__month=self.kwargs["month"],
            datetime__day=self.kwargs["day"],
        )


class WeatherHistoricalDataUpdateView(UpdateView):
    form_class = WeatherHistoricalDataUpdateForm
    model = WeatherHistoricalData
    success_url = reverse_lazy("weather:historical-data:list")
    template_name = "weather/historical_data/form.html"


class WeatherHistoricalDataDeleteView(ListView):
    def get(self, *args, **kwargs):
        # Remove
        historical_data = WeatherHistoricalData.objects

        if "year" in self.kwargs:
            historical_data = historical_data.filter(datetime__year=self.kwargs["year"])
        if "month" in self.kwargs:
            historical_data = historical_data.filter(
                datetime__month=self.kwargs["month"]
            )
        if "day" in self.kwargs:
            historical_data = historical_data.filter(datetime__day=self.kwargs["day"])

        historical_data.delete()

        # Redirect
        if "day" in self.kwargs:
            return redirect(
                reverse_lazy(
                    "weather:historical-data:list-month",
                    kwargs={
                        "year": self.kwargs["year"],
                        "month": self.kwargs["month"],
                    },
                )
            )
        elif "month" in self.kwargs:
            return redirect(
                reverse_lazy(
                    "weather:historical-data:list-year",
                    kwargs={"year": self.kwargs["year"],},
                )
            )
        elif "year" in self.kwargs:
            return redirect(reverse_lazy("weather:historical-data:list"))
