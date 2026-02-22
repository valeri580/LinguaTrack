"""
URL configuration for linguatrack project.
"""
from django.contrib import admin
from django.urls import path, include

from core.views import register

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
]
