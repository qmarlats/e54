from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from .forms import LocationCreateForm, LocationUpdateForm
from .models import Location


class LocationListView(ListView):
    context_object_name = "locations"
    model = Location
    template_name = "locations/list.html"


class LocationCreateView(CreateView):
    form_class = LocationCreateForm
    model = Location
    success_url = reverse_lazy("locations:list")
    template_name = "locations/form.html"


class LocationUpdateView(UpdateView):
    form_class = LocationUpdateForm
    model = Location
    success_url = reverse_lazy("locations:list")
    template_name = "locations/form.html"
