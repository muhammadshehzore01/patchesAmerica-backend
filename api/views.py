import os
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework.decorators import (
    api_view, permission_classes, parser_classes
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.models import Token

from .models import (
    SliderItem, PageContent, BlogPost,
    PatchRequest, PatchArtwork, ChatMessage,
    Service, UploadedImage, ChatFile, ContactMessage
)
from .serializers import (
    SliderSerializer, PageContentSerializer,
    BlogPostSerializer, PatchRequestSerializer, PatchArtworkSerializer,
    ChatMessageSerializer, ServiceSerializer, ServiceImageSerializer,
    ContactMessageSerializer
)


# ==========================================================
# CHAT FUNCTIONS
# ==========================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_file_upload(request):
    file_obj = request.FILES.get('file')
    room = request.data.get('room')
    if not file_obj or not room:
        return Response({"error": "File and room are required"}, status=400)

    chat_file = ChatFile.objects.create(
        room=room,
        file=file_obj,
        uploaded_by=request.user
    )

    return Response({
        "message": "File uploaded successfully",
        "file_url": chat_file.file.url,
        "uploaded_at": chat_file.created_at
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_chat_messages(request, room):
    messages = ChatMessage.objects.filter(room=room).order_by('-timestamp')[:50]

    data = [{
        "id": msg.id,
        "room": msg.room.user_name if msg.room else None,
        "sender": msg.sender,
        "sender_name": msg.sender_name,
        "message": msg.message,
        "attachment": msg.attachment.url if msg.attachment else None,
        "timestamp": msg.timestamp
    } for msg in messages]

    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    image = request.FILES.get('image')
    if not image:
        return Response({"error": "Image file is required"}, status=400)

    uploaded = UploadedImage.objects.create(image=image)
    return Response({
        "message": "Image uploaded successfully",
        "url": uploaded.image.url
    })


# ==========================================================
# PUBLIC APIs
# ==========================================================

@api_view(["GET"])
def api_home(request):
    slider_qs = SliderItem.objects.filter(active=True).order_by("order")
    slider_ser = SliderSerializer(slider_qs, many=True, context={"request": request})

    hero = PageContent.objects.filter(key="home_hero").first()
    hero_ser = PageContentSerializer(hero, context={"request": request}) if hero else {}

    features_qs = PageContent.objects.filter(key__startswith="home_feature_")
    features_ser = PageContentSerializer(features_qs, many=True, context={"request": request})

    services_qs = Service.objects.prefetch_related("gallery").all()
    services_ser = ServiceSerializer(services_qs, many=True, context={"request": request})

    blogs_qs = BlogPost.objects.filter(published=True).order_by("-published_at")
    blogs_ser = BlogPostSerializer(blogs_qs, many=True, context={"request": request})

    return Response({
        "sliders": slider_ser.data,
        "hero": hero_ser.data if hero_ser else {},
        "features": features_ser.data,
        "services": services_ser.data,
        "blogs": blogs_ser.data,
    })


@api_view(["GET"])
def services_list(request):
    qs = Service.objects.prefetch_related("gallery").all()
    ser = ServiceSerializer(qs, many=True, context={"request": request})
    return Response(ser.data)


@api_view(["GET"])
def service_detail(request, slug):
    service = get_object_or_404(Service.objects.prefetch_related("gallery"), slug=slug)
    ser = ServiceSerializer(service, context={"request": request})
    return Response(ser.data)


@api_view(["GET"])
def blogs_list(request):
    qs = BlogPost.objects.filter(published=True).order_by("-published_at")
    ser = BlogPostSerializer(qs, many=True, context={"request": request})
    return Response(ser.data)


@api_view(["GET"])
def blog_detail(request, slug):
    blog = get_object_or_404(BlogPost, slug=slug, published=True)
    ser = BlogPostSerializer(blog, context={"request": request})
    return Response(ser.data)


# ==========================================================
# PATCH REQUESTS
# ==========================================================
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def create_patch_request(request):
    data = {k: request.data.get(k) for k in [
        "name","email","phone","patch_type","embroidery_coverage","unit",
        "width","height","shape","backing","border","thread","quantity","custom_qty","message"
    ]}
    
    serializer = PatchRequestSerializer(data=data, context={"request": request})
    
    if serializer.is_valid():
        print(serializer.errors) 
        patch_req = serializer.save()
        for f in request.FILES.getlist("artworks"):
            PatchArtwork.objects.create(request=patch_req, file=f)
        out_ser = PatchRequestSerializer(patch_req, context={"request": request})
        return Response({"status": "ok", "data": out_ser.data}, status=status.HTTP_201_CREATED)
    
    # Log the errors
    print("Serializer errors:", serializer.errors)
    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



# ==========================================================
# CONTACT FORM
# ==========================================================

@api_view(["POST"])
def contact_message_create(request):
    serializer = ContactMessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Thank you! Your message has been received."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================================
# ADMIN AUTH
# ==========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def obtain_admin_token(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if not username or not password:
        return Response({"detail": "username and password required"}, status=400)

    user = authenticate(username=username, password=password)
    if user and user.is_staff:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
    return Response({"detail": "invalid credentials or not admin"}, status=401)


# ==========================================================
# ADMIN PANEL
# ==========================================================

def check_admin(user):
    return user.is_authenticated and user.is_staff


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_create_service(request):
    if not check_admin(request.user):
        return Response({"error": "Admin access required"}, status=403)
    serializer = ServiceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Service created successfully"}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PUT','PATCH'])
@permission_classes([IsAuthenticated])
def admin_update_service(request, pk):
    if not check_admin(request.user):
        return Response({"error": "Admin access required"}, status=403)
    service = get_object_or_404(Service, pk=pk)
    serializer = ServiceSerializer(service, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Service updated successfully"}, status=200)
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_service(request, pk):
    if not check_admin(request.user):
        return Response({"error": "Admin access required"}, status=403)
    service = get_object_or_404(Service, pk=pk)
    service.delete()
    return Response({"message": "Service deleted successfully"}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_create_slider(request):
    if not check_admin(request.user):
        return Response({"error": "Admin access required"}, status=403)
    image = request.FILES.get("image")
    if not image:
        return Response({"error": "Slider image required"}, status=400)
    slider = SliderItem.objects.create(
        title=request.data.get("title"),
        subtitle=request.data.get("subtitle"),
        image=image,
        cta_text=request.data.get("cta_text"),
        cta_url=request.data.get("cta_url"),
        order=request.data.get("order", 0),
        active=request.data.get("active", True),
    )
    return Response({"message": "Slider created", "id": slider.id}, status=201)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def admin_update_pagecontent(request):
    if not check_admin(request.user):
        return Response({"error": "Admin access required"}, status=403)
    page_key = request.data.get("key")
    if not page_key:
        return Response({"error": "Page key required"}, status=400)
    page, _ = PageContent.objects.get_or_create(key=page_key)
    page.title = request.data.get("title", page.title)
    page.subtitle = request.data.get("subtitle", page.subtitle)
    page.description = request.data.get("description", page.description)
    if "image" in request.FILES:
        page.image = request.FILES["image"]
    page.save()
    return Response({"message": "Page content updated"}, status=200)
