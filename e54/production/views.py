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
    ProductionHistoricalDataCreateForm,
    ProductionHistoricalDataDownloadForm,
    ProductionHistoricalDataImportForm,
    ProductionHistoricalDataUpdateForm,
)
from .models import ProductionHistoricalData


class ProductionHistoricalDataListView(ListView):
    context_object_name = "historical_data"
    template_name = "production/historical_data/list.html"

    def get_queryset(self):
        historical_data = ProductionHistoricalData.objects
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
            average_production=Avg("total")
        )


class ProductionHistoricalDataCreateView(CreateView):
    form_class = ProductionHistoricalDataCreateForm
    model = ProductionHistoricalData
    success_url = reverse_lazy("production:historical-data:list")
    template_name = "production/historical_data/form.html"


class ProductionHistoricalDataDownloadView(FormView):
    form_class = ProductionHistoricalDataDownloadForm
    success_url = reverse_lazy("production:historical-data:list")
    template_name = "production/historical_data/form.html"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ProductionHistoricalDataImportView(FormView):
    form_class = ProductionHistoricalDataImportForm
    success_url = reverse_lazy("production:historical-data:list")
    template_name = "production/historical_data/form.html"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ProductionHistoricalDataDetailView(ListView):
    context_object_name = "records"
    template_name = "production/historical_data/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Datetime
        datetimes = np.array(self.object_list.values_list("datetime", flat=True))
        datetimes = [timezone.localtime(datetime) for datetime in datetimes]

        # ProductionHistoricalData
        production = np.array(self.object_list.values_list("total", flat=True))
        production_trace = Scatter(x=datetimes, y=production, name="production")
        production_data = [production_trace]
        production_layout = Layout(
            xaxis={"title": "Time"}, yaxis={"title": "ProductionHistoricalData (MW)"}
        )
        production_figure = Figure(data=production_data, layout=production_layout)
        production_plot = py.plot(production_figure, auto_open=False, output_type="div")

        # Update context
        context["production_plot"] = production_plot

        return context

    def get_queryset(self):
        return ProductionHistoricalData.objects.filter(
            datetime__year=self.kwargs["year"],
            datetime__month=self.kwargs["month"],
            datetime__day=self.kwargs["day"],
        )


class ProductionHistoricalDataUpdateView(UpdateView):
    form_class = ProductionHistoricalDataUpdateForm
    model = ProductionHistoricalData
    success_url = reverse_lazy("production:historical-data:list")
    template_name = "production/historical_data/form.html"


class ProductionHistoricalDataDeleteView(ListView):
    def get(self, *args, **kwargs):
        # Remove
        historical_data = ProductionHistoricalData.objects

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
                    "production:historical-data:list-month",
                    kwargs={
                        "year": self.kwargs["year"],
                        "month": self.kwargs["month"],
                    },
                )
            )
        elif "month" in self.kwargs:
            return redirect(
                reverse_lazy(
                    "production:historical-data:list-year",
                    kwargs={"year": self.kwargs["year"],},
                )
            )
        elif "year" in self.kwargs:
            return redirect(reverse_lazy("production:historical-data:list"))
