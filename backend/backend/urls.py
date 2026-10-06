"""
URL configuration for backend project.
"""

from django.contrib import admin
from django.urls import path
from api.views import (
    get_recommendations,
    get_system_status,
    trigger_s3_sync,
    browser_test_page,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/recommend/", get_recommendations),
    path("api/status/", get_system_status),
    path("api/sync-s3/", trigger_s3_sync),
    path("", browser_test_page),
]
