from django.urls import path

from .views import LocationCreateView, LocationListView, LocationUpdateView

app_name = "location"

urlpatterns = [
    path("", LocationListView.as_view(), name="list"),
    path("new/", LocationCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", LocationUpdateView.as_view(), name="update"),
]
