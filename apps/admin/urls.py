from django.urls import path, re_path
from .views import preview_itinerary
import uuid

urlpatterns = [
    re_path(r'itinerary/(?P<itinerary_id>[0-9a-f-]+)/preview/', preview_itinerary, name='preview_itinerary'),
]
