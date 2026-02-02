from django.urls import path, re_path
from .views import preview_itinerary
import uuid

urlpatterns = [
    re_path(r'itinerary/(?P<itinerary_id>[A-Z0-9_]+)/preview/', preview_itinerary, name='preview_itinerary'),
]
