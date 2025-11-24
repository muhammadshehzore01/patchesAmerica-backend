from rest_framework import serializers
from .models import (
    SliderItem, PageContent, BlogPost, PatchRequest, PatchArtwork,
    ChatMessage, Service, ServiceImage, ContactMessage, UploadedImage
)
from .consumers import get_media_url

# ---------------------------
# Slider
# ---------------------------
class SliderSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SliderItem
        fields = ["id", "title", "subtitle", "cta_text", "cta_url", "image_url"]

    def get_image_url(self, obj):
        return get_media_url(obj.image.name if obj.image else None)


# ---------------------------
# Blog
# ---------------------------
class BlogPostSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ["id", "title", "slug", "excerpt", "content", "published", "published_at", "cover_image_url"]

    def get_cover_image_url(self, obj):
        return get_media_url(obj.cover_image.name if obj.cover_image else None)


# ---------------------------
# Page Content
# ---------------------------
class PageContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageContent
        fields = "__all__"


# ---------------------------
# Patch Artwork / Request
# ---------------------------
class PatchArtworkSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PatchArtwork
        fields = ['id', 'file_url', 'uploaded_at']

    def get_file_url(self, obj):
        return get_media_url(obj.file.name if obj.file else None)


class PatchRequestSerializer(serializers.ModelSerializer):
    artworks = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = PatchRequest
        fields = [
            'id', 'name', 'email', 'phone', 'patch_type', 'embroidery_coverage',
            'unit', 'width', 'height', 'shape', 'backing', 'border', 'thread',
            'quantity', 'custom_qty', 'message', 'created_at', 'artworks'
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        quantity = attrs.get('quantity')
        custom_qty = attrs.get('custom_qty')

        if not quantity and not custom_qty:
            raise serializers.ValidationError({
                'quantity': 'You must provide either a quantity choice or a custom quantity.'
            })

        # If custom_qty exists, override quantity
        if custom_qty:
            attrs['quantity'] = str(custom_qty)
        return attrs

    def create(self, validated_data):
        artworks_data = validated_data.pop('artworks', [])
        patch_request = PatchRequest.objects.create(**validated_data)

        for file in artworks_data:
            PatchArtwork.objects.create(request=patch_request, file=file)

        return patch_request

# ---------------------------
# Chat
# ---------------------------
class ChatMessageSerializer(serializers.ModelSerializer):
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = "__all__"

    def get_attachment_url(self, obj):
        return get_media_url(obj.attachment.name if obj.attachment else None)


# ---------------------------
# Services
# ---------------------------
class ServiceImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceImage
        fields = ["id", "image_url"]

    def get_image_url(self, obj):
        return get_media_url(obj.image.name if obj.image else None)


class ServiceSerializer(serializers.ModelSerializer):
    gallery = ServiceImageSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ["id", "title", "slug", "description", "image_url", "gallery"]

    def get_image_url(self, obj):
        # Use first image from gallery if exists
        first_image = obj.gallery.all()[0] if hasattr(obj, 'gallery') and obj.gallery.exists() else None
        return get_media_url(first_image.image.name) if first_image else None


# ---------------------------
# Contact Messages
# ---------------------------
class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = "__all__"


# ---------------------------
# Uploaded Images
# ---------------------------
class UploadedImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedImage
        fields = ["id", "image_url", "uploaded_at"]

    def get_image_url(self, obj):
        return get_media_url(obj.image.name if obj.image else None)
