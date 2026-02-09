# api/admin.py
from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from .models import (
    SliderItem, ContactMessage, PageContent, BlogPost,
    PatchRequest, PatchArtwork, ChatMessage, Service,
    ServiceImage, Keyword
)


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


# ---------------------------
# Service Images Inline
# ---------------------------
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


# ---------------------------
# Service Admin (with related blogs preview)
# ---------------------------
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "short_description", "meta_title")
    search_fields = ("title", "description", "meta_title", "meta_description", "meta_keywords")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ServiceImageInline]
    readonly_fields = ('related_blogs_preview', 'created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('title', 'slug', 'description')}),
        ('SEO', {'fields': ('meta_title', 'meta_description', 'meta_keywords')}),
        ('Related Content', {'fields': ('related_blogs_preview',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def short_description(self, obj):
        return (obj.description[:50] + "...") if len(obj.description) > 50 else obj.description
    short_description.short_description = "Description"

    def related_blogs_preview(self, obj):
        related = obj.get_related_blogs()
        if not related.exists():
            return "No matching published blogs found yet."
        return format_html_join(
            mark_safe('<br>'),
            '<a href="/admin/api/blogpost/{}/change/" target="_blank">{}</a> – {}',
            ((b.id, b.title, b.excerpt[:50] + "...") for b in related)
        )
    related_blogs_preview.short_description = "Suggested Related Blogs"


# ---------------------------
# ServiceImage Admin
# ---------------------------
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


# ---------------------------
# BlogPost Admin (with related services preview)
# ---------------------------
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "published", "published_at", "cover_preview", "meta_title")
    list_filter = ("published", "published_at")
    search_fields = ("title", "excerpt", "content", "meta_title", "meta_description", "meta_keywords")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-published_at",)
    readonly_fields = ('related_services_preview', 'created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('title', 'slug', 'excerpt', 'content', 'cover_image', 'published', 'published_at')}),
        ('SEO', {'fields': ('meta_title', 'meta_description', 'meta_keywords')}),
        ('Related Content', {'fields': ('related_services_preview',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="100" style="border-radius:5px"/>', obj.cover_image.url)
        return "-"
    cover_preview.short_description = "Cover"

    def related_services_preview(self, obj):
        related = obj.get_related_services()
        if not related.exists():
            return "No matching services found yet."
        return format_html_join(
            mark_safe('<br>'),
            '<a href="/admin/api/service/{}/change/" target="_blank">{}</a> – {}',
            ((s.id, s.title, s.description[:50] + "...") for s in related)
        )
    related_services_preview.short_description = "Suggested Related Services"


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
    search_fields = ("room", "sender", "message")
    readonly_fields = ("timestamp",)

    def short_text(self, obj):
        return obj.message[:40] + ("..." if len(obj.message) > 40 else "")
    short_text.short_description = "Message"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('term', 'pillar', 'volume', 'competition', 'intent', 'target_url')
    list_filter = ('pillar', 'intent')
    search_fields = ('term', 'notes')
    ordering = ('-volume', 'term')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('term', 'volume', 'competition', 'intent', 'pillar', 'cluster_of', 'target_url')
        }),
        ('Notes & Timestamps', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )