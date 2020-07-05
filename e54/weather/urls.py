from django.urls import include, path

from .views import (
    WeatherHistoricalDataCreateView,
    WeatherHistoricalDataDeleteView,
    WeatherHistoricalDataDetailView,
    WeatherHistoricalDataDownloadView,
    WeatherHistoricalDataImportView,
    WeatherHistoricalDataListView,
    WeatherHistoricalDataUpdateView,
)

app_name = "weather"

historical_data = [
    path("", WeatherHistoricalDataListView.as_view(), name="list"),
    path("<int:year>/", WeatherHistoricalDataListView.as_view(), name="list-year"),
    path(
        "<int:year>-<int:month>/",
        WeatherHistoricalDataListView.as_view(),
        name="list-month",
    ),
    path(
        "<int:year>-<int:month>-<int:day>/",
        WeatherHistoricalDataDetailView.as_view(),
        name="detail",
    ),
    path("new/", WeatherHistoricalDataCreateView.as_view(), name="create"),
    path("download/", WeatherHistoricalDataDownloadView.as_view(), name="download"),
    path("import/", WeatherHistoricalDataImportView.as_view(), name="import"),
    path("<int:pk>/edit/", WeatherHistoricalDataUpdateView.as_view(), name="update"),
    path(
        "<int:year>/delete/",
        WeatherHistoricalDataDeleteView.as_view(),
        name="delete-year",
    ),
    path(
        "<int:year>-<int:month>/delete/",
        WeatherHistoricalDataDeleteView.as_view(),
        name="delete-month",
    ),
    path(
        "<int:year>-<int:month>-<int:day>/delete/",
        WeatherHistoricalDataDeleteView.as_view(),
        name="delete-day",
    ),
]

urlpatterns = [
    path("historical-data/", include((historical_data, "historical-data"))),
]
