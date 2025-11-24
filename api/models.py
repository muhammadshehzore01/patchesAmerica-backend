from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


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

class PageContent(models.Model):
    key = models.SlugField(unique=True)
    title = models.CharField(max_length=250, blank=True)
    body = models.TextField(blank=True)
    extra = models.JSONField(default=dict, blank=True)
    def __str__(self):
        return self.key

class BlogPost(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='blogs/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)  # ✅ this should always run

    def __str__(self):
        return self.title

class PatchRequest(models.Model):
    PATCH_TYPES = [
        ('embroidered', 'Embroidered'),
        ('leather', 'Leather'),
        ('chenille', 'Chenille'),
        ('printed', 'Printed'),
        ('pvc', 'PVC'),
        ('woven', 'Woven'),
        ('custom', 'Custom/Stickers'),
    ]

    COVERAGE_CHOICES = [
        ('50%', '50% Embroidered'),
        ('75%', '75% Embroidered'),
        ('100%', '100% Embroidered'),
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
        ('iron', 'Iron on'),
        ('adhesive', 'Adhesive'),
        ('plastic', 'Plastic'),
        ('velcro-hook', 'Velcro Hook Backing'),
        ('velcro-loop', 'Velcro Loop Backing'),
        ('velcro-both', 'Velcro Hook & Loop Backing'),
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
        ('10', '10'),('25','25'),('50','50'),('75','75'),('100','100'),
        ('150','150'),('300','300'),('500','500'),('1000','1000'),('3000','3000'),
        ('5000+','5000+'),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    patch_type = models.CharField(max_length=50, choices=PATCH_TYPES)
    embroidery_coverage = models.CharField(max_length=10, choices=COVERAGE_CHOICES, blank=True, null=True)
    unit = models.CharField(max_length=20, choices=UNITS, default='inches')
    width = models.CharField(max_length=40, blank=True)
    height = models.CharField(max_length=40, blank=True)
    shape = models.CharField(max_length=30, choices=SHAPES, default='custom')
    backing = models.CharField(max_length=30, choices=BACKINGS, default='none')
    border = models.CharField(max_length=30, choices=BORDERS, blank=True, null=True)
    thread = models.CharField(max_length=20, choices=THREADS, default='normal')
    quantity = models.CharField(max_length=20, choices=QUANTITY_CHOICES, blank=True, null=True)
    custom_qty = models.PositiveIntegerField(blank=True, null=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.patch_type} — {self.quantity or self.custom_qty}"
    
class PatchArtwork(models.Model):
    request = models.ForeignKey(PatchRequest, on_delete=models.CASCADE, related_name='artworks')
    file = models.FileField(upload_to='artwork/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Artwork for {self.request.id} - {self.file.name}"

class Service(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

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


# ============================
# CHAT  MODELS
# ============================
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
    


# ============================
# CHAT UPLOAD MODELS
# ============================

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
