# project/backend/backend/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv
import urllib.parse
from django.http.request import split_domain_port, HttpRequest

# ---------------------------
# Load environment
# ---------------------------
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
DOCKER_ENV = os.getenv("DOCKER_ENV", "false").lower() == "true"

# ---------------------------
# Hosts and CSRF
# ---------------------------
if DOCKER_ENV or DEBUG:
    ALLOWED_HOSTS = ["*"]
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "http://backend:8000",
        "http://django_backend:8000",
	"http://admin.northernpatches.com",
        "http://localhost:3000",
        "http://nextjs_frontend:3000",
    ]
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
else:
    ALLOWED_HOSTS = os.getenv(
        "DJANGO_ALLOWED_HOSTS", "admin.northernpatches.com,northernpatches.com,www.northernpatches.com"
    ).split(",")
    CSRF_TRUSTED_ORIGINS = os.getenv(
        "DJANGO_CSRF_TRUSTED_ORIGINS", "https://northernpatches.com,https://admin.northernpatches.com,https://www.northernpatches.com"
    ).split(",")
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CORS_ALLOW_ALL_ORIGINS = False
    # allow origins from env
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "https://admin.northernpatches.com,https://northernpatches.com,https://www.northernpatches.com").split(",")

# If behind a proxy that terminates TLS (Caddy), set this so Django knows original scheme
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ---------------------------
# Docker get_host patch for internal requests
# ---------------------------
if DOCKER_ENV or DEBUG:
    def patched_get_host(self):
        host = self.META.get("HTTP_HOST", "")
        if host:
            try:
                domain, _ = split_domain_port(host)
                if domain:
                    return domain
            except Exception:
                pass
        get_raw = getattr(self, "get_raw_uri", None)
        if callable(get_raw):
            try:
                return get_raw().split("/")[2].split(":")[0]
            except Exception:
                pass
        return "localhost"

    HttpRequest.get_host = patched_get_host

# ---------------------------
# Static / Media
# ---------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Production-ready full URL for frontend
MEDIA_FULL_URL = os.getenv("MEDIA_FULL_URL", "https://northernpatches.com/media")
NEXT_PUBLIC_MEDIA_BASE = os.getenv("NEXT_PUBLIC_MEDIA_BASE", MEDIA_FULL_URL)


# ---------------------------
# Database
# ---------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST', 'postgres_db'),
        'PORT': os.getenv('POSTGRES_PORT', 5432),
    }
}

# ---------------------------
# Redis / Channels
# ---------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "redis_server")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
parsed_url = urllib.parse.urlparse(REDIS_URL)

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [(parsed_url.hostname, parsed_url.port)]},
    }
}

# ---------------------------
# Installed Apps
# ---------------------------
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'dal',
    'dal_select2',
    'channels',
    'rest_framework',
    'corsheaders',
    'rest_framework.authtoken',
    # 'django.contrib.sitemaps',
]

# ---------------------------
# Middleware
# ---------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ---------------------------
# CORS
# ---------------------------
CORS_ALLOW_CREDENTIALS = True

# ---------------------------
# REST Framework
# ---------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny' if (DOCKER_ENV or DEBUG) 
        else 'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
}

# ---------------------------
# Templates
# ---------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ---------------------------
# Security / HTTPS
# ---------------------------
if not (DEBUG or DOCKER_ENV):
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    X_FRAME_OPTIONS = 'SAMEORIGIN'

# ---------------------------
# ASGI / WSGI
# ---------------------------
ROOT_URLCONF = 'backend.urls'
ASGI_APPLICATION = 'backend.asgi.application'
WSGI_APPLICATION = 'backend.wsgi.application'

# ---------------------------
# Localization
# ---------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------
# JAZZMIN_SETTINGS
# ---------------------------

JAZZMIN_SETTINGS = {

    "site_title": "Northern Patches Admin",
    "site_header": "Northern Patches",
    "site_brand": "Northern Patches",

    "welcome_sign": "Welcome to Northern Patches Admin",

    "icons": {
        "api.Country": "fas fa-flag-usa",
        "api.State": "fas fa-map",
        "api.City": "fas fa-city",
        "api.Service": "fas fa-cogs",
        "api.BlogPost": "fas fa-blog",
        "api.Keyword": "fas fa-search",
    },

    "navigation_expanded": True,

    "order_with_respect_to": [
        "api.Country",
        "api.State",
        "api.City",
        "api.Service",
        "api.BlogPost",
        "api.Keyword",
    ],
}
