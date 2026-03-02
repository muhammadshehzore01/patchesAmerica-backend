# api/urls.py
from django.urls import path, re_path
from django.views.generic.base import RedirectView
from django.http import HttpResponseGone, HttpResponseNotFound
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # optional for JWT if you switch later

from . import views
from . import autocomplete
from .views import us_states  # import the us_states view

urlpatterns = [
    # ==========================
    # CSRF (keep for safety)
    # ==========================
    path('csrf/', views.csrf, name='csrf'),

    # health check backend 
    path('health/', views.health_check, name='health_check'),

    # ==========================
    # Auto complete cities
    # ==========================
    path('city-autocomplete/', autocomplete.CityAutocomplete.as_view(), name='city-autocomplete'),

    # ==========================
    # PUBLIC ENDPOINTS
    # ==========================
    path('home/', views.api_home, name='api_home'),
    path('contact/', views.contact_message_create, name='contact'),

    # Services
    path('services/', views.services_list, name='services_list'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),

    # Blogs
    path('blogs/', views.blogs_list, name='blogs_list'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),

    # Patch Requests (quote form)
    path('patch-requests/', views.create_patch_request, name='create_patch_request'),
    path('patch-requests-json/', views.patch_requests_json),

    # ==========================
    # CHAT RELATED
    # ==========================
    path('chat/<str:room>/', views.recent_chat_messages, name='recent_chat_messages'),
    path('chat/upload/', views.chat_file_upload, name='chat_file_upload'),
    path('upload/image/', views.upload_image, name='upload_image'),

    # ==========================
    # ADMIN AUTH (consider moving to JWT later)
    # ==========================
    path('admin-token/', views.obtain_admin_token, name='admin_token'),

    # ==========================
    # ADMIN PANEL ENDPOINTS
    # ==========================
    # Services CRUD
    path('admin-chat/services/create/', views.admin_create_service, name='admin_create_service'),
    path('admin-chat/services/<int:pk>/update/', views.admin_update_service, name='admin_update_service'),
    path('admin-chat/services/<int:pk>/delete/', views.admin_delete_service, name='admin_delete_service'),

    # Slider (only create for now — add update/delete if needed)
    path('admin-chat/slider/create/', views.admin_create_slider, name='admin_create_slider'),

    # Page Content
    # path('admin-chat/pages/<str:key>/update/', views.admin_update_pagecontent, name='admin_update_pagecontent'),

    # ==========================
    # BLOCK COMMON PROBES / SCANNER PATHS (reduces log noise)
    # ==========================
    # Return 404 silently for bots looking for vulnerabilities
    path("swagger.json", lambda r: HttpResponseNotFound()),
    path("swagger-ui/", lambda r: HttpResponseNotFound()),
    path("graphql", lambda r: HttpResponseNotFound()),
    path("gql", lambda r: HttpResponseNotFound()),
    path(".env", lambda r: HttpResponseNotFound()),
    path("wp-login.php", lambda r: HttpResponseNotFound()),
    path("xmlrpc.php", lambda r: HttpResponseNotFound()),

    # ==========================
    # 301 REDIRECTS
    # ==========================
    # Old service URLs
    path('services/printed-patches/', RedirectView.as_view(url='/services/sublimation-patches/', permanent=True)),
    path('services/custom-leather-patches/', RedirectView.as_view(url='/services/leather-patch/', permanent=True)),
    path('services/premium-leather-custom-patches-usa-patches-usa/', RedirectView.as_view(url='/services/leather-patch/', permanent=True)),
    path('services/woven-custom-patches/', RedirectView.as_view(url='/services/wowen-patch/', permanent=True)),
    path('services/high-quality-woven-custom-patches-usa/', RedirectView.as_view(url='/services/wowen-patch/', permanent=True)),

    # Old blog URLs
    path('blog/custom-patches-usa/', RedirectView.as_view(url='/blog/', permanent=True)),
    path('blog/custom-chenille-patches-usa-premium-varsity-style/', RedirectView.as_view(url='/blog/', permanent=True)),

    # Keywords list
    path('keywords/', views.keyword_list, name='keyword_list'),

    # Fetch US states and city
    path("us-states/", us_states, name="us-states"),
    path("city/<int:city_id>/", views.city_detail, name="city_detail"),

    # Junk/test post - 410 Gone (tells Google to drop it permanently)
    re_path(r'^blog/hglkjgjhgjhgjhgjhh/?$', lambda request: HttpResponseGone()),
]