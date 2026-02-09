import json
import re
import aiohttp
import base64
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings

# -------------------- GLOBALS --------------------
online_admins = set()
online_users = set()
online_user_meta = {}  # username -> {country: "..."}

# -------------------- HELPERS --------------------
def pick_primary_admin():
    if not online_admins:
        return None
    return sorted(list(online_admins))[0]

def get_media_url(path):
    """Return correct URL for frontend, prevent double /media/ in Docker/local."""
    if not path:
        return None
    path = path.lstrip("/")
    base = getattr(settings, "NEXT_PUBLIC_MEDIA_BASE", getattr(settings, "MEDIA_URL", "/media/"))
    return f"{base}/{path}".replace("//", "/").replace(":/", "://")

async def save_base64_image(base64_data, filename_prefix="chat"):
    """Save base64 image and return relative file path."""
    try:
        if not base64_data.startswith("data:image/"):
            return None
        fmt, imgstr = base64_data.split(";base64,")
        ext = fmt.split("/")[-1]
        file_name = f"{filename_prefix}_{os.urandom(8).hex()}.{ext}"
        file_path = os.path.join(settings.MEDIA_ROOT, "chat_attachments", file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(imgstr))
        return f"chat_attachments/{file_name}"
    except Exception as e:
        print("⚠️ Image save failed:", e)
        return None

# -------------------- USER CONSUMER --------------------
class UserChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import ChatRoom, ChatMessage

        self.username = self.scope['url_route']['kwargs'].get('username')
        if not self.username or not re.match(r'^[\w-]+$', self.username):
            await self.close()
            return

        # Geo IP lookup
        country = "Unknown"
        try:
            ip = self.scope.get('client')[0]
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://ip-api.com/json/{ip}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        country = data.get("country", "Unknown")
        except Exception:
            pass

        # Join user room
        self.room_group_name = f"user_{self.username}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        room, _ = await database_sync_to_async(ChatRoom.objects.get_or_create)(user_name=self.username)

        newly_added = self.username not in online_users
        online_users.add(self.username)
        online_user_meta[self.username] = {"country": country}

        primary_admin = pick_primary_admin()
        if primary_admin and not room.assigned_admin:
            room.assigned_admin = primary_admin
            await database_sync_to_async(room.save)()

        # Send welcome message only once per session
        if newly_added:
            welcome_text = f"Welcome {self.username}!"
            if primary_admin:
                welcome_text += f" You're connected — Admin: {primary_admin}"
            else:
                welcome_text += " No admins online. We'll notify you when someone joins."

            await database_sync_to_async(ChatMessage.objects.create)(
                room=room,
                sender="admin",
                sender_name=primary_admin or "system",
                message=welcome_text
            )

            await self.send(json.dumps({
                "type": "welcome",
                "message": welcome_text,
                "assigned_admin": primary_admin
            }))

            # Notify admin group
            await self.channel_layer.group_send(
                "admin_group",
                {"type": "user_joined", "username": self.username, "country": country}
            )

        # Send updated user list to admins
        users_payload = [
            {"username": u, "country": online_user_meta.get(u, {}).get("country", "Unknown")}
            for u in online_users
        ]
        await self.channel_layer.group_send(
            "admin_group",
            {"type": "online_users", "users": users_payload}
        )

    async def disconnect(self, close_code):
        username = getattr(self, "username", None)
        if username and username in online_users:
            online_users.discard(username)
            online_user_meta.pop(username, None)
            users_payload = [
                {"username": u, "country": online_user_meta.get(u, {}).get("country", "Unknown")}
                for u in online_users
            ]
            await self.channel_layer.group_send(
                "admin_group",
                {"type": "online_users", "users": users_payload}
            )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        from .models import ChatRoom, ChatMessage

        # Production-safe JSON parsing
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            await self.send(json.dumps({"type": "error", "error": "Invalid JSON"}))
            return

        action = data.get("action")
        if action == "reply":
            message = data.get("message", "").strip()
            attachment = data.get("attachment")
            temp_id = data.get("tempId")

            if not message and not attachment:
                await self.send(json.dumps({"type": "error", "error": "Empty message"}))
                return

            room = await database_sync_to_async(ChatRoom.objects.get)(user_name=self.username)
            saved_file_path = None
            if attachment:
                saved_file_path = await save_base64_image(attachment, filename_prefix=self.username)

            msg_obj = await database_sync_to_async(ChatMessage.objects.create)(
                room=room,
                sender="user",
                sender_name=self.username,
                message=message or "",
                attachment=saved_file_path or None
            )

            # Send back to user
            await self.send(json.dumps({
                "type": "sent",
                "message": message,
                "attachment": get_media_url(saved_file_path),
                "from_admin": False,
                "tempId": temp_id,
                "timestamp": msg_obj.timestamp.isoformat()
            }))

            # Send to admin group
            await self.channel_layer.group_send(
                "admin_group",
                {
                    "type": "user_message",
                    "username": self.username,
                    "message": message,
                    "attachment": get_media_url(saved_file_path),
                    "timestamp": msg_obj.timestamp.isoformat()
                }
            )

    # ---------------- EVENT HANDLERS ----------------
    async def admin_message_to_user(self, event):
        await self.send(json.dumps({
            "type": "sent",
            "message": event.get("message"),
            "attachment": event.get("attachment"),
            "from_admin": True,
            "timestamp": event.get("timestamp")
        }))

    async def user_joined(self, event):
        await self.send(json.dumps(event))

    async def online_users(self, event):
        await self.send(json.dumps(event))

    async def admin_list(self, event):
        await self.send(json.dumps(event))


# -------------------- ADMIN CONSUMER --------------------
class AdminChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import ChatRoom

        self.admin_name = (
            self.scope['url_route']['kwargs'].get("admin_name")
            or self.scope['query_string'].decode().split("username=")[-1]
        )
        if not self.admin_name:
            await self.close()
            return

        self.group_name = "admin_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        online_admins.add(self.admin_name)

        # Send initial lists
        await self.send(json.dumps({
            "type": "online_users",
            "users": [
                {"username": u, "country": online_user_meta.get(u, {}).get("country", "Unknown")}
                for u in online_users
            ]
        }))
        await self.send(json.dumps({
            "type": "admin_list",
            "admins": list(online_admins)
        }))

    async def disconnect(self, close_code):
        if getattr(self, "admin_name", None) in online_admins:
            online_admins.discard(self.admin_name)
        await self.channel_layer.group_send(
            "admin_group",
            {"type": "admin_list", "admins": list(online_admins)}
        )
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        from .models import ChatRoom, ChatMessage

        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            await self.send(json.dumps({"type": "error", "error": "Invalid JSON"}))
            return

        action = data.get("action")
        if action == "reply":
            to_user = data.get("to")
            message = data.get("message", "").strip()
            attachment = data.get("attachment")
            temp_id = data.get("tempId")

            if not to_user or (not message and not attachment):
                await self.send(json.dumps({"type": "error", "error": "Invalid reply"}))
                return

            room = await database_sync_to_async(ChatRoom.objects.get)(user_name=to_user)
            saved_file_path = None
            if attachment:
                saved_file_path = await save_base64_image(attachment, filename_prefix=self.admin_name)

            msg_obj = await database_sync_to_async(ChatMessage.objects.create)(
                room=room,
                sender="admin",
                sender_name=self.admin_name,
                message=message or "",
                attachment=saved_file_path or None
            )

            await self.channel_layer.group_send(
                f"user_{to_user}",
                {
                    "type": "admin_message_to_user",
                    "message": message,
                    "attachment": get_media_url(saved_file_path),
                    "admin": self.admin_name,
                    "timestamp": msg_obj.timestamp.isoformat(),
                    "tempId": temp_id
                }
            )

            await self.send(json.dumps({
                "type": "sent_admin",
                "to": to_user,
                "message": message,
                "attachment": get_media_url(saved_file_path),
                "timestamp": msg_obj.timestamp.isoformat()
            }))

    # ---------------- EVENT HANDLERS ----------------
    async def user_message(self, event):
        await self.send(json.dumps(event))

    async def user_joined(self, event):
        await self.send(json.dumps(event))

    async def online_users(self, event):
        await self.send(json.dumps(event))

    async def admin_list(self, event):
        await self.send(json.dumps(event))
