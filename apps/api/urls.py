from django.urls import path
from apps.api.views.llm_views_simple import (
    ProcessRequirementView,
    ProviderInfoView,
    RateLimitStatsView,
    CacheStatsView,
    ClearCacheView,
    ReloadConfigView,
    HealthCheckView
)

urlpatterns = [
    path('process/', ProcessRequirementView.as_view(), name='process_requirement'),
    path('provider-info/', ProviderInfoView.as_view(), name='provider_info'),
    path('rate-limit-stats/', RateLimitStatsView.as_view(), name='rate_limit_stats'),
    path('cache-stats/', CacheStatsView.as_view(), name='cache_stats'),
    path('cache/clear/', ClearCacheView.as_view(), name='clear_cache'),
    path('config/reload/', ReloadConfigView.as_view(), name='reload_config'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
]
