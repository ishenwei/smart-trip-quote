from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from apps.api.views.webhook_views import (
    ItineraryWebhookView,
    RequirementWebhookView,
    ProcessRequirementViaN8nView
)

urlpatterns = [
    path('webhook/itinerary/', ItineraryWebhookView.as_view(), name='itinerary_webhook'),
    path('webhook/requirement/', csrf_exempt(ProcessRequirementViaN8nView.as_view()), name='process_requirement_via_n8n'),
    path('webhook/requirement/callback/', RequirementWebhookView.as_view(), name='requirement_webhook_callback'),
]
