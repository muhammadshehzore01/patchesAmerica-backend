# api/admin.py

from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from dal import autocomplete

from .models import (
    SliderItem,
    ContactMessage,
    BlogPost,
    PatchRequest,
    PatchArtwork,
    ChatMessage,
    Service,
    ServiceImage,
    Keyword,
    Country,
    State,
    City,
)


# =====================================================
# COUNTRY ADMIN
# =====================================================
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_default")
    search_fields = ("name", "code")
    list_editable = ("is_default",)
    ordering = ("name",)


# =====================================================
# STATE ADMIN
# =====================================================
@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "country", "population")
    search_fields = ("name", "code")
    list_filter = ("country",)
    autocomplete_fields = ("country",)
    ordering = ("name",)


# =====================================================
# CITY ADMIN
# =====================================================
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "population")
    search_fields = ("name",)
    list_filter = ("state",)
    autocomplete_fields = ("state",)
    ordering = ("-population",)


# =====================================================
# SLIDER ADMIN
# =====================================================
@admin.register(SliderItem)
class SliderItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "subtitle",
        "order",
        "active",
        "preview_image",
    )
    list_editable = ("order", "active")
    search_fields = ("title", "subtitle")
    ordering = ("order",)

    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" style="border-radius:6px"/>',
                obj.image.url
            )
        return "-"


# =====================================================
# SERVICE IMAGE INLINE
# =====================================================
class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    readonly_fields = ("preview",)
    fields = ("image", "preview")

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="90" style="border-radius:6px"/>',
                obj.image.url
            )
        return "-"


# =====================================================
# SERVICE ADMIN
# =====================================================
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "country",
        "state",
        "city",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "meta_title",
        "meta_keywords",
    )
    list_filter = (
        "country",
        "state",
        "city",
    )
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ServiceImageInline]
    readonly_fields = (
        "related_blogs_preview",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Basic Info", {
            "fields": ("title", "slug", "description",)
        }),
        ("Location Targeting", {
            "fields": ("country", "state", "city",)
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description", "meta_keywords",)
        }),
        ("Related Blogs", {
            "fields": ("related_blogs_preview",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at",),
            "classes": ("collapse",)
        }),
    )

    # DAL autocomplete for City
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "city":
            kwargs["widget"] = autocomplete.ModelSelect2(
                url='city-autocomplete',
                forward=['state'],
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def related_blogs_preview(self, obj):
        blogs = obj.get_related_blogs()
        if not blogs.exists():
            return "No related blogs"
        return format_html_join(
            mark_safe("<br>"),
            '<a href="/admin/api/blogpost/{}/change/" target="_blank">{}</a>',
            ((b.id, b.title) for b in blogs)
        )


# =====================================================
# BLOG ADMIN
# =====================================================
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "country",
        "state",
        "city",
        "published",
        "published_at",
    )
    search_fields = (
        "title",
        "content",
        "meta_title",
        "meta_keywords",
    )
    list_filter = (
        "published",
        "country",
        "state",
        "city",
    )
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = (
        "related_services_preview",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Blog Content", {
            "fields": ("title", "slug", "excerpt", "content", "cover_image", "published", "published_at",)
        }),
        ("Location Targeting", {
            "fields": ("country", "state", "city",)
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description", "meta_keywords",)
        }),
        ("Related Services", {
            "fields": ("related_services_preview",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at",),
            "classes": ("collapse",)
        }),
    )

    # DAL autocomplete for City
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "city":
            kwargs["widget"] = autocomplete.ModelSelect2(
                url='city-autocomplete',
                forward=['state'],
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def related_services_preview(self, obj):
        services = obj.get_related_services()
        if not services.exists():
            return "No related services"
        return format_html_join(
            mark_safe("<br>"),
            '<a href="/admin/api/service/{}/change/" target="_blank">{}</a>',
            ((s.id, s.title) for s in services)
        )


# =====================================================
# PATCH REQUEST ADMIN
# =====================================================
@admin.register(PatchRequest)
class PatchRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "patch_type", "quantity", "created_at",)
    search_fields = ("name", "email",)
    list_filter = ("patch_type", "created_at",)
    ordering = ("-created_at",)


# =====================================================
# PATCH ARTWORK ADMIN
# =====================================================
@admin.register(PatchArtwork)
class PatchArtworkAdmin(admin.ModelAdmin):
    list_display = ("request", "file", "uploaded_at",)


# =====================================================
# CHAT ADMIN
# =====================================================
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("room", "sender", "timestamp",)
    search_fields = ("room",)


# =====================================================
# CONTACT ADMIN
# =====================================================
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at",)
    search_fields = ("name", "email")


# =====================================================
# KEYWORD ADMIN
# =====================================================
@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ("term", "volume", "intent", "target_url",)
    search_fields = ("term",)
    list_filter = ("intent",)
    ordering = ("-volume",)
