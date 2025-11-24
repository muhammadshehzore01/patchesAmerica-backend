from django.contrib import admin
from django.utils.html import format_html
from .models import SliderItem, ContactMessage ,PageContent, BlogPost, PatchRequest,PatchArtwork ,ChatMessage, Service, ServiceImage


@admin.register(SliderItem)
class SliderItemAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle", "order", "active", "preview_image")
    list_editable = ("order", "active")
    search_fields = ("title", "subtitle")
    ordering = ("order",)

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="border-radius:5px"/>', obj.image.url)
        return "-"
    preview_image.short_description = "Image"


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ("key", "title")
    search_fields = ("key", "title")


class ServiceImageInline(admin.TabularInline):   
    model = ServiceImage
    extra = 1
    fields = ("image", "preview_image")
    readonly_fields = ("preview_image",)

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="border-radius:5px"/>', obj.image.url)
        return "-"
    preview_image.short_description = "Preview"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "short_description")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ServiceImageInline]

    def short_description(self, obj):
        return (obj.description[:50] + "...") if len(obj.description) > 50 else obj.description
    short_description.short_description = "Description"


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ("service", "preview_image")
    search_fields = ("service__title",)
    readonly_fields = ("preview_image",)

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="border-radius:5px"/>', obj.image.url)
        return "-"
    preview_image.short_description = "Image"


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "published", "published_at", "cover_preview")
    list_filter = ("published", "published_at")
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-published_at",)

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="100" style="border-radius:5px"/>', obj.cover_image.url)
        return "-"
    cover_preview.short_description = "Cover"


@admin.register(PatchRequest)
class PatchRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'patch_type', 'backing', 'quantity', 'created_at')
    list_filter = ('patch_type', 'backing', 'thread', 'border', 'shape')
    search_fields = ('name', 'email', 'phone')
    ordering = ('-created_at',)

@admin.register(PatchArtwork)
class PatchArtworkAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'file', 'uploaded_at')
    search_fields = ('request__name',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("room", "sender", "short_text", "timestamp")
    list_filter = ("room", "timestamp")
    search_fields = ("room", "sender", "text")
    readonly_fields = ("timestamp",)

    def short_text(self, obj):
        return obj.text[:40] + ("..." if len(obj.text) > 40 else "")
    short_text.short_description = "Message"



@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')