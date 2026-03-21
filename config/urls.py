"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from apps.admin import admin_site
from apps.views import test_itinerary_save_logs

urlpatterns = [
    path('admin/', include('apps.admin.urls')),
    path('admin/', admin_site.urls),
    path('api/', include('apps.api.urls')),
    path('api/llm/', include('apps.api.urls')),
    #path('api/webhook/', include('apps.api.urls')),
    path('test_save_logs/', test_itinerary_save_logs, name='test_save_logs'),
]
