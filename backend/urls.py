# project/backend/backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings




urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

# Serve static & media in development only
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Make sure MEDIA_URL always starts with a slash
    media_url = settings.MEDIA_URL
    if not media_url.startswith("/"):
        media_url = f"/{media_url.lstrip('/')}"
    urlpatterns += static(media_url, document_root=settings.MEDIA_ROOT)
