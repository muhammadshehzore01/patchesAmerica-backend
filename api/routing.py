from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Optional trailing slash
    re_path(r"ws/user/(?P<username>[^/]+)/?$", consumers.UserChatConsumer.as_asgi()),
    re_path(r"ws/admin-chat/(?P<admin_name>[^/]+)/?$", consumers.AdminChatConsumer.as_asgi()),
]
