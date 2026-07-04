from pathlib import Path
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:5173,http://localhost:8000').split(',')]

INSTALLED_APPS = [
    'api',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# In development, allow all origins. In production, set CORS_ALLOWED_ORIGINS env var.
_cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
if _cors_origins:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in _cors_origins.split(',')]
else:
    CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
     'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Email Configuration
# Use SendGrid API backend only if EMAIL_BACKEND env var explicitly requests it.
# Otherwise, use standard Django SMTP backend (works with Gmail App Passwords, etc.)
_email_backend_env = os.getenv('EMAIL_BACKEND', '')
if _email_backend_env == 'sendgrid':
    EMAIL_BACKEND = 'api.email_backends.SendGridAPIBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

ADMINS = [('Admin', DEFAULT_FROM_EMAIL)]
MANAGERS = ADMINS

# Fall back to console email in development when no email host is configured
if not EMAIL_HOST and DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

JAZZMIN_SETTINGS = {
    "site_title": "Eternelle Aura Admin",
    "site_header": "Eternelle Aura",
    "site_brand": "Eternelle Aura",
    "site_logo": None,
    "welcome_sign": "Welcome to Eternelle Aura Management",
    "copyright": "Eternelle Aura Ltd",
    "index_url": "admin_analytics_view",
    "search_model": ["api.Product", "auth.User"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Home",  "url": "admin_analytics_view", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://eternelleaura.com/support", "new_window": True},
        {"model": "auth.User"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["api.Product", "api.Order", "api.Message", "api.NewsletterSubscriber"],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "api.Product": "fas fa-wine-bottle",
        "api.Customer": "fas fa-user-friends",
        "api.Order": "fas fa-shopping-cart",
        "api.Message": "fas fa-envelope",
        "api.NewsletterSubscriber": "fas fa-at",
        "api.Review": "fas fa-star",
        "api.FlashSale": "fas fa-bolt",
        "api.Coupon": "fas fa-ticket-alt",
        "api.Cart": "fas fa-shopping-basket",
    },
    "custom_links": {
        "api": [
            {
                "name": "📊 View Sales Analytics", 
                "url": "/api/admin/analytics-view/", 
                "icon": "fas fa-chart-line",
                "permissions": ["auth.view_user"]
            },
        ]
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
}

JAZZMIN_UI_CONFIG = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-orange",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_fixed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-orange",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_xl": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
# Payment Gateways
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')

# M-Pesa (Safaricom Daraja API)
MPESA_ENVIRONMENT = os.getenv('MPESA_ENVIRONMENT', 'sandbox')  # 'sandbox' or 'production'
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', '')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE', '')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', '')
MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL', 'https://yourdomain.com/api/payments/mpesa/callback/')
MPESA_INITIATOR_NAME = os.getenv('MPESA_INITIATOR_NAME', '')
MPESA_INITIATOR_PASSWORD = os.getenv('MPESA_INITIATOR_PASSWORD', '')

# External Services
MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY', '')
MAILCHIMP_LIST_ID = os.getenv('MAILCHIMP_LIST_ID', '')

# Production security settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'

