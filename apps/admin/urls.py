from django.urls import path, re_path
from .views import preview_itinerary, get_filtered_resources
import uuid

urlpatterns = [
    re_path(r'itinerary/(?P<itinerary_id>[A-Z0-9_]+)/preview/', preview_itinerary, name='preview_itinerary'),
    path('get_filtered_resources/', get_filtered_resources, name='get_filtered_resources'),
]
