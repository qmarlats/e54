from django.urls import include, path

from .views import (
    ProductionHistoricalDataCreateView,
    ProductionHistoricalDataDeleteView,
    ProductionHistoricalDataDetailView,
    ProductionHistoricalDataDownloadView,
    ProductionHistoricalDataImportView,
    ProductionHistoricalDataListView,
    ProductionHistoricalDataUpdateView,
)

app_name = "production"

historical_data = [
    path("", ProductionHistoricalDataListView.as_view(), name="list"),
    path(
        "<int:year>/", ProductionHistoricalDataListView.as_view(), name="list-year"
    ),
    path(
        "<int:year>-<int:month>/",
        ProductionHistoricalDataListView.as_view(),
        name="list-month",
    ),
    path("new/", ProductionHistoricalDataCreateView.as_view(), name="create"),
    path("download/", ProductionHistoricalDataDownloadView.as_view(), name="download"),
    path("import/", ProductionHistoricalDataImportView.as_view(), name="import"),
    path(
        "<int:year>-<int:month>-<int:day>/",
        ProductionHistoricalDataDetailView.as_view(),
        name="detail",
    ),
    path("<int:pk>/edit/", ProductionHistoricalDataUpdateView.as_view(), name="update"),
    path(
        "<int:year>/delete/",
        ProductionHistoricalDataDeleteView.as_view(),
        name="delete-year",
    ),
    path(
        "<int:year>-<int:month>/delete/",
        ProductionHistoricalDataDeleteView.as_view(),
        name="delete-month",
    ),
    path(
        "<int:year>-<int:month>-<int:day>/delete/",
        ProductionHistoricalDataDeleteView.as_view(),
        name="delete-day",
    ),
]

urlpatterns = [
    path("historical-data/", include((historical_data, "historical-data"))),
]
