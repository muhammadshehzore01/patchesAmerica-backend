import os
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Prefetch
from rest_framework.decorators import (
    api_view, permission_classes, parser_classes
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.models import Token

from .models import (
    SliderItem, BlogPost,
    PatchRequest, PatchArtwork, ChatMessage,
    Service, UploadedImage, ChatFile, ContactMessage, Keyword,
    Country, State, City

)
from .serializers import (
    SliderSerializer, 
    BlogPostSerializer, PatchRequestSerializer, PatchArtworkSerializer,
    ChatMessageSerializer, ServiceSerializer, ServiceImageSerializer,
    ContactMessageSerializer,KeywordSerializer
)
from .consumers import get_media_url

# ---------------------------
# CSRF Endpoint
# ---------------------------
@api_view(['GET'])
@ensure_csrf_cookie
def csrf(request):
    """
    Call this endpoint from the browser to set the CSRF cookie.
    Example: fetch('/api/csrf/')
    """
    return Response({"detail": "CSRF cookie set"})


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
    return Response({"message": "Image uploaded successfully", "url": uploaded.image.url})


# ==========================================================
# PUBLIC APIs
# ==========================================================
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

@api_view(["GET"])
def api_home(request):
    # Slider items
    slider_qs = SliderItem.objects.filter(active=True).order_by("order")
    slider_ser = SliderSerializer(slider_qs, many=True, context={"request": request})

    # # Hero content
    # hero = PageContent.objects.filter(key="home_hero").first()
    # hero_ser = PageContentSerializer(hero, context={"request": request}) if hero else {}

    # # Features content
    # features_qs = PageContent.objects.filter(key__startswith="home_feature_")
    # features_ser = PageContentSerializer(features_qs, many=True, context={"request": request})

    # Services
    services_qs = Service.objects.prefetch_related("gallery").all()
    services_ser = ServiceSerializer(services_qs, many=True, context={"request": request})

    # Blogs
    blogs_qs = BlogPost.objects.filter(published=True).order_by("-published_at")
    blogs_ser = BlogPostSerializer(blogs_qs, many=True, context={"request": request})

    # Return all home page data in one response
    return Response({
        "sliders": slider_ser.data,
        # "hero": hero_ser.data if hero_ser else {},
        # "features": features_ser.data,
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
# CREATE PATCH REQUEST
# ==========================================================
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def create_patch_request(request):
    # ---------------------------
    # Extract data from request
    # ---------------------------
    fields = [
        "name", "email", "phone",
        "patch_type", "embroidery_coverage", "dimension",
        "unit", "width", "height", "shape", "backing", "border", "thread",
        "leather_type", "finish_effect",
        "quantity", "custom_qty", "message"
    ]
    
    data = {k: request.data.get(k) for k in fields}

    # ---------------------------
    # Serialize & Validate
    # ---------------------------
    serializer = PatchRequestSerializer(data=data, context={"request": request})
    
    if serializer.is_valid():
        patch_req = serializer.save()

        # ---------------------------
        # Handle multiple artwork uploads
        # ---------------------------
        for f in request.FILES.getlist("artworks"):
            PatchArtwork.objects.create(request=patch_req, file=f)
        
        out_ser = PatchRequestSerializer(patch_req, context={"request": request})
        return Response({"status": "ok", "data": out_ser.data}, status=status.HTTP_201_CREATED)
    
    # ---------------------------
    # Return validation errors
    # ---------------------------
    print("Serializer errors:", serializer.errors)
    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



# ==========================================================
# GET PATCH REQUEST
# ==========================================================


@api_view(['GET'])
@permission_classes([AllowAny])  # public access
def patch_requests_json(request):
    qs = PatchRequest.objects.prefetch_related('artworks').all()
    serializer = PatchRequestSerializer(qs, many=True, context={"request": request})
    return Response(serializer.data)


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




@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def keyword_list(request):
    qs = Keyword.objects.all().order_by('-volume')
    ser = KeywordSerializer(qs, many=True)
    return Response(ser.data) 



@api_view(['GET'])
def us_states(request):
    try:
        country = Country.objects.get(code="US")
    except Country.DoesNotExist:
        return Response({"error": "US country not found"}, status=404)

    # Prefetch cities properly using related_name
    states_qs = State.objects.filter(country=country).prefetch_related(
        Prefetch('cities', queryset=City.objects.all())
    )

    states_data = []
    for state in states_qs:
        # Access cities via 'cities' related_name
        cities = [city.name for city in state.cities.all()]
        states_data.append({
            "code": state.code,
            "name": state.name,
            "cities": cities
        })

    return Response(states_data)


@api_view(["GET"])
def city_detail(request, city_id):
    city = get_object_or_404(City, pk=city_id)
    return Response({
        "name": city.name,
        "state": city.state.name,
        "country": city.state.country.name,
        "population": city.population
    })


# ==========================================================
# Backend health check
# ==========================================================

def health_check(request):
    """
    Simple health check endpoint for Docker healthcheck.
    Returns 200 OK with JSON if app is running.
    """
    return JsonResponse({
        "status": "healthy",
        "message": "Django backend is running",
        "timestamp": timezone.now().isoformat()
    })
