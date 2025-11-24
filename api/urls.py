from django.urls import path
from . import views

urlpatterns = [
    # ==========================
    # PUBLIC
    # ==========================
    path('home/', views.api_home, name='api_home'),
    path('contact/', views.contact_message_create, name='contact'),

    # Services
    path('services/', views.services_list, name='services_list'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),

    # Blogs
    path('blogs/', views.blogs_list, name='blogs_list'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),

    # Patch Requests
    path('patch-requests/', views.create_patch_request, name='create_patch_request'),

    # ==========================
    # CHAT
    # ==========================
    path('chat/<str:room>/', views.recent_chat_messages, name='recent_chat_messages'),
    path('chat/upload/', views.chat_file_upload, name='chat_file_upload'),
    path('upload/image/', views.upload_image, name='upload_image'),

    # ==========================
    # ADMIN AUTH
    # ==========================
    path('admin-token/', views.obtain_admin_token, name='obtain_admin_token'),

    # ==========================
    # ADMIN - SERVICES
    # ==========================
    path('admin/services/create/', views.admin_create_service, name='admin_create_service'),
    path('admin/services/<int:pk>/update/', views.admin_update_service, name='admin_update_service'),
    path('admin/services/<int:pk>/delete/', views.admin_delete_service, name='admin_delete_service'),

    # ==========================
    # ADMIN - SLIDER
    # ==========================
    path('admin/slider/create/', views.admin_create_slider, name='admin_create_slider'),

    # ==========================
    # ADMIN - PAGE CONTENT
    # ==========================
    path('admin/pages/<str:key>/update/', views.admin_update_pagecontent, name='admin_update_pagecontent'),
]
