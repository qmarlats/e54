import numpy as np
import plotly.offline as py

from django.db.models import Avg, Count
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView
from plotly.graph_objs import Figure, Layout, Scatter

from .forms import (
    ConsumptionHistoricalDataCreateForm,
    ConsumptionHistoricalDataDownloadForm,
    ConsumptionHistoricalDataImportForm,
    ConsumptionHistoricalDataUpdateForm,
    ConsumptionForecastCreateForm,
)
from .models import ConsumptionHistoricalData, ConsumptionForecast


class ConsumptionHistoricalDataListView(ListView):
    context_object_name = "historical_data"
    template_name = "consumption/historical_data/list.html"

    def get_queryset(self):
        historical_data = ConsumptionHistoricalData.objects
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
        return historical_data.annotate(records_count=Count("id")).annotate(
            average_consumption=Avg("total")
        )


class ConsumptionHistoricalDataCreateView(CreateView):
    form_class = ConsumptionHistoricalDataCreateForm
    model = ConsumptionHistoricalData
    success_url = reverse_lazy("consumption:historical-data:list")
    template_name = "consumption/historical_data/form.html"


class ConsumptionHistoricalDataImportView(FormView):
    form_class = ConsumptionHistoricalDataImportForm
    success_url = reverse_lazy("consumption:historical-data:list")
    template_name = "consumption/historical_data/form.html"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ConsumptionHistoricalDataDownloadView(FormView):
    form_class = ConsumptionHistoricalDataDownloadForm
    success_url = reverse_lazy("consumption:historical-data:list")
    template_name = "consumption/historical_data/form.html"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ConsumptionHistoricalDataDetailView(ListView):
    context_object_name = "records"
    template_name = "consumption/historical_data/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Datetime
        datetimes = np.array(self.object_list.values_list("datetime", flat=True))
        datetimes = [timezone.localtime(datetime) for datetime in datetimes]

        # ConsumptionHistoricalData
        consumption = np.array(self.object_list.values_list("total", flat=True))
        consumption_trace = Scatter(
            x=datetimes, y=consumption, name="ConsumptionHistoricalData"
        )
        consumption_data = [consumption_trace]
        consumption_layout = Layout(
            xaxis={"title": "Time"}, yaxis={"title": "ConsumptionHistoricalData (MW)"}
        )
        consumption_figure = Figure(data=consumption_data, layout=consumption_layout)
        consumption_plot = py.plot(
            consumption_figure, auto_open=False, output_type="div"
        )

        # Update context
        context["consumption_plot"] = consumption_plot

        return context

    def get_queryset(self):
        return ConsumptionHistoricalData.objects.filter(
            datetime__year=self.kwargs["year"],
            datetime__month=self.kwargs["month"],
            datetime__day=self.kwargs["day"],
        )


class ConsumptionHistoricalDataUpdateView(UpdateView):
    form_class = ConsumptionHistoricalDataUpdateForm
    model = ConsumptionHistoricalData
    success_url = reverse_lazy("consumption:historical-data:list")
    template_name = "consumption/historical_data/form.html"


class ConsumptionHistoricalDataDeleteView(ListView):
    def get(self, *args, **kwargs):
        # Remove
        historical_data = ConsumptionHistoricalData.objects

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
                    "consumption:historical-data:list-month",
                    kwargs={
                        "year": self.kwargs["year"],
                        "month": self.kwargs["month"],
                    },
                )
            )
        elif "month" in self.kwargs:
            return redirect(
                reverse_lazy(
                    "consumption:historical-data:list-year",
                    kwargs={"year": self.kwargs["year"],},
                )
            )
        elif "year" in self.kwargs:
            return redirect(reverse_lazy("consumption:historical-data:list"))


class ConsumptionForecastListView(ListView):
    context_object_name = "forecasts"
    template_name = "consumption/forecasts/list.html"

    def get_queryset(self):
        forecasts = ConsumptionForecast.objects
        if "month" in self.kwargs:
            forecasts = forecasts.filter(
                datetime__year=self.kwargs["year"], datetime__month=self.kwargs["month"]
            )
            forecasts = forecasts.annotate(day=TruncDay("datetime")).values("day")
        elif "year" in self.kwargs:
            forecasts = forecasts.filter(datetime__year=self.kwargs["year"])
            forecasts = forecasts.annotate(month=TruncMonth("datetime")).values("month")
        else:
            forecasts = forecasts.annotate(year=TruncYear("datetime")).values("year")
        return forecasts.annotate(records_count=Count("id")).annotate(
            average_consumption=Avg("total")
        )


class ConsumptionForecastCreateView(FormView):
    form_class = ConsumptionForecastCreateForm
    success_url = reverse_lazy("consumption:forecasts:list")
    template_name = "consumption/forecasts/form.html"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ConsumptionForecastDetailView(ListView):
    context_object_name = "forecasts"
    template_name = "consumption/forecasts/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Plotly config
        config = {
            "displaylogo": False,
        }

        # Datetime
        datetimes = np.array(self.object_list.values_list("datetime", flat=True))
        datetimes = [timezone.localtime(datetime) for datetime in datetimes]

        # ConsumptionHistoricalData
        consumption = np.array(self.object_list.values_list("total", flat=True))
        consumption_trace = Scatter(
            x=datetimes, y=consumption, name="ConsumptionHistoricalData"
        )
        consumption_data = [consumption_trace]
        consumption_layout = Layout(
            xaxis={"title": "Time"}, yaxis={"title": "ConsumptionHistoricalData (MW)"}
        )
        consumption_figure = Figure(data=consumption_data, layout=consumption_layout)
        consumption_plot = py.plot(
            consumption_figure, auto_open=False, output_type="div", config=config
        )

        # Update context
        context["consumption_plot"] = consumption_plot

        return context

    def get_queryset(self):
        return ConsumptionForecast.objects.filter(
            datetime__year=self.kwargs["year"],
            datetime__month=self.kwargs["month"],
            datetime__day=self.kwargs["day"],
        )


class ConsumptionForecastUpdateView(UpdateView):
    fields = "__all__"
    model = ConsumptionForecast
    success_url = reverse_lazy("consumption:forecasts:list")
    template_name = "consumption/forecasts/form.html"


class ConsumptionForecastDeleteView(ListView):
    def get(self, *args, **kwargs):
        # Remove
        forecasts = ConsumptionForecast.objects

        if "year" in self.kwargs:
            forecasts = forecasts.filter(datetime__year=self.kwargs["year"])
        if "month" in self.kwargs:
            forecasts = forecasts.filter(
                datetime__month=self.kwargs["month"]
            )
        if "day" in self.kwargs:
            forecasts = forecasts.filter(datetime__day=self.kwargs["day"])

        forecasts.delete()

        # Redirect
        if "day" in self.kwargs:
            return redirect(
                reverse_lazy(
                    "consumption:forecasts:list-month",
                    kwargs={
                        "year": self.kwargs["year"],
                        "month": self.kwargs["month"],
                    },
                )
            )
        elif "month" in self.kwargs:
            return redirect(
                reverse_lazy(
                    "consumption:forecasts:list-year",
                    kwargs={"year": self.kwargs["year"],},
                )
            )
        elif "year" in self.kwargs:
            return redirect(reverse_lazy("consumption:forecasts:list"))
