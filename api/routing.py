# backend\api\routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # users connect using path like: ws://host/ws/user/<username>/
    re_path(r"ws/user/(?P<username>[^/]+)/$", consumers.UserChatConsumer.as_asgi()),

    # admins connect using: ws://host/ws/admin/<admin_name>/
    re_path(r"ws/admin/(?P<admin_name>[^/]+)/$", consumers.AdminChatConsumer.as_asgi()),
]
