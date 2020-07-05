from django.urls import include, path

urlpatterns = [
    path("", include("core.urls", namespace="core")),
    path("consumption/", include("consumption.urls", namespace="consumption")),
    path("locations/", include("locations.urls", namespace="locations")),
    path("production/", include("production.urls", namespace="production")),
    path("weather/", include("weather.urls", namespace="weather")),
]
