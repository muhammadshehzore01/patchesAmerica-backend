# api/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.utils.timezone import now
from django.utils import timezone


# ---------------------------
# Slider iteam model
# ---------------------------
class SliderItem(models.Model):
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='sliders/')
    cta_text = models.CharField(max_length=80, blank=True)
    cta_url = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title or f"Slide {self.pk}"

    class Meta:
        ordering = ['order']


# ---------------------------
# Page content model
# ---------------------------
class PageContent(models.Model):
    key = models.SlugField(unique=True)
    title = models.CharField(max_length=250, blank=True)
    body = models.TextField(blank=True)
    extra = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.key


# ---------------------------
# Blog Model
# ---------------------------
class BlogPost(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=500,unique=True, blank=True)
    excerpt = models.TextField(blank=True, help_text="Short summary, used for SEO and previews.")
    content = models.TextField()
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='blogs/', null=True, blank=True)

    # SEO fields – auto-enhanced on save if empty
    meta_title = models.CharField(max_length=500, blank=True, help_text="Auto-generated if blank")
    meta_description = models.CharField(max_length=500, blank=True, help_text="Auto-generated if blank")
    meta_keywords = models.CharField(max_length=1500, blank=True, help_text="Auto-generated if blank")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-generate SEO fields only if they are still empty
        if not self.meta_title:
            self.meta_title = f"{self.title} | Northern Patches USA – Custom Patches 2026"

        if not self.meta_description:
            source = self.excerpt or self.content
            clean_text = strip_tags(source)[:140].strip()
            self.meta_description = f"{clean_text} – Premium custom patches USA with no minimum order & fast shipping."

        if not self.meta_keywords:
            base = [self.title.lower(), "custom patches USA", "no minimum custom patches"]
            slug_words = self.slug.replace('-', ' ').split()[:5]
            self.meta_keywords = ", ".join(base + slug_words)

        if self.published and not self.published_at:
            self.published_at = now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_related_services(self):
        """Suggest up to 3 related services based on keyword or title match – improved logic"""
        from .models import Service
        from django.db.models import Q

        search_term = self.title.lower()

        # Split title into meaningful words for broader matching
        words = [word for word in search_term.split() if len(word) > 3]

        # Build flexible OR conditions
        q_objects = Q()
        for word in words:
            q_objects |= Q(title__icontains=word) | Q(meta_keywords__icontains=word)

        # Also match if service title appears anywhere in blog title
        q_objects |= Q(title__icontains=search_term)

        return Service.objects.filter(q_objects).distinct()[:3]



# ---------------------------
# Patch Request Model
# ---------------------------

class PatchRequest(models.Model):
    PATCH_TYPES = [
        ('embroidered', 'Embroidered'),
        ('leather', 'Leather'),
        ('chenille', 'Chenille'),
        ('printed', 'Printed'),
        ('pvc', 'PVC'),
        ('woven', 'Woven'),
        ('custom', 'Custom / Stickers'),
    ]
    COVERAGE_CHOICES = [
        ('50%', '50% Embroidered'),
        ('75%', '75% Embroidered'),
        ('100%', '100% Embroidered'),
    ]
    DIMENSIONS = [
        ('2D', '2D Mold'),
        ('3D', '3D Mold'),
    ]
    LEATHER_TYPES = [
        ('genuine', 'Genuine Leather'),
        ('faux', 'Faux Leather'),
        ('suede', 'Suede Finish'),
        ('rustic', 'Rustic / Polished'),
    ]
    FINISH_EFFECTS = [
        ('embossed', 'Embossed'),
        ('debossed', 'Debossed'),
        ('engraving', 'Engraving'),
        ('printed', 'Printed'),
    ]
    UNITS = [
        ('inches', 'Inches'),
        ('mm', 'Millimeters'),
        ('cm', 'Centimeters'),
    ]
    SHAPES = [
        ('custom', 'Custom Shape'),
        ('circle', 'Circle'),
        ('square', 'Square'),
        ('h-oval', 'Horizontal Oval'),
        ('h-rect', 'Horizontal Rectangle'),
        ('v-rect', 'Vertical Rectangle'),
        ('diamond', 'Diamond'),
        ('v-oval', 'Vertical Oval'),
        ('shield-a', 'Shield A'),
        ('shield-b', 'Shield B'),
        ('shield-c', 'Shield C'),
        ('shield-d', 'Shield D'),
    ]
    BACKINGS = [
        ('none', 'No Backing'),
        ('iron', 'Iron-on'),
        ('adhesive', 'Adhesive'),
        ('plastic', 'Plastic'),
        ('velcro-hook', 'Velcro Hook'),
        ('velcro-loop', 'Velcro Loop'),
        ('velcro-both', 'Velcro Hook & Loop'),
        ('safety-pin', 'Safety Pin'),
    ]
    BORDERS = [
        ('merrow', 'Merrow'),
        ('heat-cut', 'Heat Cut'),
        ('laser-cut', 'Laser Cut'),
    ]
    THREADS = [
        ('normal', 'Normal'),
        ('gold', 'Gold Metallic'),
        ('silver', 'Silver Metallic'),
        ('glow', 'Glow in the Dark'),
    ]
    QUANTITY_CHOICES = [
        ('10','10'),('25','25'),('50','50'),('75','75'),('100','100'),
        ('150','150'),('300','300'),('500','500'),('1000','1000'),('3000','3000'),
        ('5000+','5000+'),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)

    patch_type = models.CharField(max_length=50, choices=PATCH_TYPES)
    embroidery_coverage = models.CharField(max_length=10, choices=COVERAGE_CHOICES, blank=True, null=True)
    dimension = models.CharField(max_length=2, choices=DIMENSIONS, blank=True, null=True)
    unit = models.CharField(max_length=20, choices=UNITS, default='inches')
    width = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    shape = models.CharField(max_length=30, choices=SHAPES, default='custom')
    backing = models.CharField(max_length=30, choices=BACKINGS, default='none')
    border = models.CharField(max_length=30, choices=BORDERS, blank=True, null=True)
    thread = models.CharField(max_length=20, choices=THREADS, default='normal')
    leather_type = models.CharField(max_length=20, choices=LEATHER_TYPES, blank=True, null=True)
    finish_effect = models.CharField(max_length=20, choices=FINISH_EFFECTS, blank=True, null=True)

    quantity = models.CharField(max_length=20, choices=QUANTITY_CHOICES, blank=True, null=True)
    custom_qty = models.PositiveIntegerField(blank=True, null=True)
    message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        qty = self.quantity or self.custom_qty
        return f"{self.name} — {self.patch_type} — {qty}"

# ---------------------------
# Patch Artwork model
# ---------------------------

class PatchArtwork(models.Model):
    request = models.ForeignKey(PatchRequest, on_delete=models.CASCADE, related_name='artworks')
    file = models.FileField(upload_to='artwork/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Artwork for {self.request.id} - {self.file.name}"

# ---------------------------
# Services  Modele
# ---------------------------

class Service(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    description = models.TextField()

    # SEO fields – auto-enhanced on save if empty
    meta_title = models.CharField(max_length=500, blank=True, help_text="Auto-generated if blank")
    meta_description = models.CharField(max_length=500, blank=True, help_text="Auto-generated if blank")
    meta_keywords = models.CharField(max_length=1500, blank=True, help_text="Auto-generated if blank")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-enhance SEO fields only if they are still empty
        if not self.meta_title:
            self.meta_title = f"{self.title} | Northern Patches USA – Custom Patches No Minimum"

        if not self.meta_description:
            clean = strip_tags(self.description)[:140].strip()
            self.meta_description = f"{clean} – Premium custom patches USA with no minimum order & fast shipping."

        if not self.meta_keywords:
            words = [self.title.lower(), "custom patches USA", "no minimum custom patches"]
            slug_words = self.slug.replace('-', ' ').split()[:5]
            self.meta_keywords = ", ".join(words + slug_words)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_related_blogs(self):
        """Suggest up to 3 related published blogs based on keyword or title match"""
        from .models import BlogPost
        return BlogPost.objects.filter(
            models.Q(meta_keywords__icontains=self.title.lower()) |
            models.Q(title__icontains=self.title.lower())
        ).order_by('-published_at')[:3]


class ServiceImage(models.Model):
    service = models.ForeignKey(Service, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='service_images/')

    def __str__(self):
        return f"{self.service.title} Image"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject or 'No Subject'}"


# ────────────────────────────────────────────────
# CHAT MODELS
# ────────────────────────────────────────────────
class ChatRoom(models.Model):
    user_name = models.CharField(max_length=150, unique=True)
    assigned_admin = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_name


class ChatMessage(models.Model):
    SENDER_CHOICES = (("user", "User"), ("admin", "Admin"))
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    sender_name = models.CharField(max_length=150, blank=True, null=True)
    message = models.TextField(blank=True)
    attachment = models.FileField(upload_to="chat_attachments/", blank=True, null=True)
    is_read_by_admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.room.user_name} | {self.sender} | {self.timestamp}"


# ────────────────────────────────────────────────
# CHAT UPLOAD MODELS
# ────────────────────────────────────────────────
class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"


class ChatFile(models.Model):
    room = models.CharField(max_length=100)
    file = models.FileField(upload_to='uploads/chat_files/')
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatFile {self.id} ({self.room})"


# ────────────────────────────────────────────────
# SEO KEYWORD TRACKER
# ────────────────────────────────────────────────
class Keyword(models.Model):
    """
    Tracks target keywords for SEO content planning.
    Pillars = main topics (e.g. Embroidered Patches)
    Clusters = supporting long-tail articles
    """
    PILLAR_CHOICES = [
        ('general', 'General / Core Keywords'),
        ('embroidered', 'Embroidered Patches'),
        ('pvc', 'PVC Patches'),
        ('leather', 'Leather Patches'),
        ('chenille', 'Chenille Patches'),
        ('guides', 'Design & Buying Guides'),
    ]

    INTENT_CHOICES = [
        ('informational', 'Informational'),
        ('commercial', 'Commercial'),
        ('transactional', 'Transactional'),
    ]

    term = models.CharField(max_length=255, unique=True)
    volume = models.PositiveIntegerField(default=0, help_text="Monthly USA search volume estimate")
    competition = models.FloatField(default=0.0, help_text="0–1 scale (lower = easier to rank)")
    intent = models.CharField(max_length=20, choices=INTENT_CHOICES, default='commercial')
    pillar = models.CharField(max_length=50, choices=PILLAR_CHOICES, blank=True)
    cluster_of = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='clusters')
    target_url = models.CharField(max_length=500, blank=True, help_text="Internal URL this keyword should target")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-volume', 'term']
        verbose_name_plural = "Keywords"

    def __str__(self):
        pillar_name = dict(self.PILLAR_CHOICES).get(self.pillar, 'No Pillar')
        return f"{self.term} ({pillar_name})"

    def save(self, *args, **kwargs):
        if not self.target_url and self.pillar:
            base = f"/{self.pillar.replace('_', '-')}/"
            self.target_url = f"{base}{slugify(self.term)}/"
        super().save(*args, **kwargs)