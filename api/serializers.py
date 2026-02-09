# api/serializers.py
from rest_framework import serializers
from .models import (
    SliderItem, PageContent, BlogPost, PatchRequest, PatchArtwork,
    ChatMessage, Service, ServiceImage, ContactMessage, UploadedImage,
    Keyword
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
    related_services = serializers.SerializerMethodField()  # New

    class Meta:
        model = BlogPost
        fields = [
            "id", "title", "slug", "excerpt", "content", "published", "published_at",
            "cover_image_url", "meta_title", "meta_description", "meta_keywords",
            "related_services"
        ]

    def get_cover_image_url(self, obj):
        return get_media_url(obj.cover_image.name if obj.cover_image else None)

    def get_related_services(self, obj):
        related = obj.get_related_services()
        return [{"title": s.title, "slug": s.slug, "description": s.description[:100]} for s in related]


# ---------------------------
# Page Content
# ---------------------------
class PageContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageContent
        fields = "__all__"


# ---------------------------
# Patch Artwork Serializer
# ---------------------------
class PatchArtworkSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PatchArtwork
        fields = ['id', 'file_url', 'uploaded_at']

    def get_file_url(self, obj):
        return get_media_url(obj.file.name if obj.file else None)


# ---------------------------
# Patch Request Serializer
# ---------------------------
class PatchRequestSerializer(serializers.ModelSerializer):
    artworks = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = PatchRequest
        fields = [
            'id', 'name', 'email', 'phone',
            'patch_type', 'embroidery_coverage', 'dimension',
            'unit', 'width', 'height', 'shape', 'backing', 'border', 'thread',
            'leather_type', 'finish_effect',
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
    schema = serializers.SerializerMethodField()
    related_blogs = serializers.SerializerMethodField()  # New

    class Meta:
        model = Service
        fields = [
            "id", "title", "slug", "description",
            "created_at", "updated_at",
            "image_url", "gallery",
            "meta_title", "meta_description", "meta_keywords",
            "schema", "related_blogs"
        ]

    def get_image_url(self, obj):
        first_image = obj.gallery.first()
        return get_media_url(first_image.image.name) if first_image else None

    def get_schema(self, obj):
        return {
            "@context": "https://schema.org",
            "@type": "Service",
            "serviceType": obj.title,
            "provider": {
                "@type": "Organization",
                "name": "Northern Patches USA",
                "url": "https://northernpatches.com"
            },
            "areaServed": "US",
            "description": obj.description[:300],
            "offers": {
                "@type": "Offer",
                "priceCurrency": "USD",
                "price": "Contact for quote",
                "itemOffered": {"@type": "Service", "name": obj.title}
            }
        }

    def get_related_blogs(self, obj):
        related = obj.get_related_blogs()
        return [{"title": b.title, "slug": b.slug, "excerpt": b.excerpt[:100]} for b in related]


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


# ---------------------------
# Keyword Serializer
# ---------------------------
class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = [
            'id', 'term', 'volume', 'competition', 'intent',
            'pillar', 'cluster_of', 'target_url', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 