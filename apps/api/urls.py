from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from apps.api.views.webhook_views import (
    ItineraryWebhookView,
    RequirementWebhookView,
    ProcessRequirementViaN8nView,
    ItineraryOptimizationCallbackView,
    ItineraryQuoteCallbackView
)
from apps.api.views.export_views import ItineraryPDFExportView, ItineraryWordExportView

urlpatterns = [
    path('webhook/itinerary/', ItineraryWebhookView.as_view(), name='itinerary_webhook'),
    path('webhook/itinerary/optimization/callback/', ItineraryOptimizationCallbackView.as_view(), name='itinerary_optimization_callback'),
    path('webhook/itinerary/quote/callback/', ItineraryQuoteCallbackView.as_view(), name='itinerary_quote_callback'),
    path('webhook/requirement/', csrf_exempt(ProcessRequirementViaN8nView.as_view()), name='process_requirement_via_n8n'),
    path('webhook/requirement/callback/', RequirementWebhookView.as_view(), name='requirement_webhook_callback'),
    path('export/pdf/<str:itinerary_id>/', ItineraryPDFExportView.as_view(), name='itinerary_pdf_export'),
    path('export/word/<str:itinerary_id>/', ItineraryWordExportView.as_view(), name='itinerary_word_export'),
]
