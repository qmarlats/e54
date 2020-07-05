from django.urls import include, path

from .views import (
    ConsumptionHistoricalDataCreateView,
    ConsumptionHistoricalDataDeleteView,
    ConsumptionHistoricalDataDetailView,
    ConsumptionHistoricalDataDownloadView,
    ConsumptionHistoricalDataImportView,
    ConsumptionHistoricalDataListView,
    ConsumptionHistoricalDataUpdateView,
    ConsumptionForecastCreateView,
    ConsumptionForecastDeleteView,
    ConsumptionForecastDetailView,
    ConsumptionForecastListView,
    ConsumptionForecastUpdateView,
)

app_name = "consumption"

historical_data = [
    path("", ConsumptionHistoricalDataListView.as_view(), name="list"),
    path(
        "<int:year>/", ConsumptionHistoricalDataListView.as_view(), name="list-year"
    ),
    path(
        "<int:year>-<int:month>/",
        ConsumptionHistoricalDataListView.as_view(),
        name="list-month",
    ),
    path("new/", ConsumptionHistoricalDataCreateView.as_view(), name="create"),
    path("download/", ConsumptionHistoricalDataDownloadView.as_view(), name="download"),
    path("import/", ConsumptionHistoricalDataImportView.as_view(), name="import"),
    path(
        "<int:year>-<int:month>-<int:day>/",
        ConsumptionHistoricalDataDetailView.as_view(),
        name="detail",
    ),
    path(
        "<int:pk>/edit/", ConsumptionHistoricalDataUpdateView.as_view(), name="update"
    ),
    path(
        "<int:year>/delete/",
        ConsumptionHistoricalDataDeleteView.as_view(),
        name="delete-year",
    ),
    path(
        "<int:year>-<int:month>/delete/",
        ConsumptionHistoricalDataDeleteView.as_view(),
        name="delete-month",
    ),
    path(
        "<int:year>-<int:month>-<int:day>/delete/",
        ConsumptionHistoricalDataDeleteView.as_view(),
        name="delete-day",
    ),
]

forecasts = [
    path("", ConsumptionForecastListView.as_view(), name="list"),
    path("<int:year>/", ConsumptionForecastListView.as_view(), name="list-year"),
    path(
        "<int:year>-<int:month>/",
        ConsumptionForecastListView.as_view(),
        name="list-month",
    ),
    path("new/", ConsumptionForecastCreateView.as_view(), name="create"),
    path(
        "<int:year>-<int:month>-<int:day>/",
        ConsumptionForecastDetailView.as_view(),
        name="detail",
    ),
    path("<int:pk>/edit/", ConsumptionForecastUpdateView.as_view(), name="update"),
    path(
        "<int:year>/delete/",
        ConsumptionForecastDeleteView.as_view(),
        name="delete-year",
    ),
    path(
        "<int:year>-<int:month>/delete/",
        ConsumptionForecastDeleteView.as_view(),
        name="delete-month",
    ),
    path(
        "<int:year>-<int:month>-<int:day>/delete/",
        ConsumptionForecastDeleteView.as_view(),
        name="delete-day",
    ),
]

urlpatterns = [
    path("historical-data/", include((historical_data, "historical-data"))),
    path("forecasts/", include((forecasts, "forecasts"))),
]
