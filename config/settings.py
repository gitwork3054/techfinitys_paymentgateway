from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-before-deploy")
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"

render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")
default_hosts = "localhost,127.0.0.1"
if render_host:
    default_hosts += f",{render_host}"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", default_hosts).split(",") if h.strip()]

CSRF_TRUSTED_ORIGINS = []
if render_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_host}")
extra_csrf = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "")
if extra_csrf:
    CSRF_TRUSTED_ORIGINS.extend([v.strip() for v in extra_csrf.split(",") if v.strip()])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "portal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "APP_DIRS": True,
    "DIRS": [],
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]
    },
}]
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
TIME_ZONE = "Asia/Kolkata"
USE_TZ = True

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

COMPANY = {
    "name": "Techfinitys",
    "tagline": "Software engineered for infinite scale",
    "email": "hello@techfinitys.com",
    "phone": "+91 6356981879",
    "address": "Vadodara, Gujarat, India",
    "web": "https://techfinitys.com/",
    "gstin": "Not provided",
    "acc_no": "925020054181867",
    "ifsc": "UTIB0000383",
    "services": ["Brand Growth", "Performance Marketing", "Creative Production", "Web & Automation", "Maintenance & Support"],
}
UPI_ID = "6356981879@axisbank"
UPI_NAME = "Techfinitys"

CLIENT_BRAND = {
    "name": "Ashapura Rakhi",
    "headline": "Festive wholesale growth package",
    "about": "Ashapura Rakhi is a direct manufacturer, wholesaler, and designer brand specializing in Rakhi bracelets, festive accessories, and raw materials.",
    "location": "Opposite Old Laxmipura Police Station, Laxmipura Road, Laxmipura, Vadodara, Gujarat",
    "hours": "Monday to Sunday · 9:00 AM – 8:00 PM",
    "phone": "8401947462",
    "rating": "4.8/5 on Justdial",
    "wholesale": "Pan-India wholesale & reselling catalog via Instagram @ashapura_rakhi",
    "instagram": "https://www.instagram.com/ashapura_rakhi/",
    "justdial": "https://www.justdial.com/Vadodara/Ashapura-Rakhi-Opposite-Old-Laxmipura-Police-Station-Laxmipura/0265PX265-X265-210817133518-D6S5_BZDET",
}

PACKAGE_DETAILS = {
    "title": "Premium Brand Growth Plan",
    "monthly_price": "₹21,999 / Month* (₹25,900 Incl. GST)",
    "summary": "Designed for businesses aiming for aggressive digital growth and strong brand positioning.",
    "includes": [
        "Instagram + Facebook + Optional LinkedIn",
        "16–20 Premium Posts",
        "8 Reels",
        "Advanced Story Strategy (15+ Stories)",
        "Creative Direction",
        "Community Management",
        "Monthly Strategy Meeting",
        "Detailed Performance Analytics",
    ],
    "changes": [
        "Minor changes allowed: 5 per post",
        "Caption edits: Unlimited minor tweaks",
        "Design changes: Full flexibility before final approval",
        "Reel changes: 2–3 revisions per reel",
        "Strategy adjustments: Ongoing (monthly discussion)",
        "Priority handling",
    ],
    "pricing": [
        {"label": "3 Months", "actual": "₹78,000", "discounted": "₹74,880", "saved": "₹3,120"},
        {"label": "6 Months", "actual": "₹1,56,000", "discounted": "₹1,41,960", "saved": "₹14,040"},
        {"label": "12 Months", "actual": "₹3,12,000", "discounted": "₹2,55,840", "saved": "₹56,160"},
    ],
    "notes": [
        "Prices exclusive of GST (18%)",
        "All payment in advance required",
        "Bulk packages offer better savings & priority service",
    ],
    "proposal_math": [
        {"label": "Base package", "value": "₹2,50,000"},
        {"label": "Discount", "value": "− ₹50,000"},
        {"label": "Net creative package", "value": "₹2,00,000"},
        {"label": "Boosting & Meta ads", "value": "₹1,00,000"},
        {"label": "Recommended total payable", "value": "₹3,00,000", "highlight": True},
    ],
    "quick_amounts": [200000, 100000, 300000],
}

PAYMENT_PROVIDER = os.environ.get("PAYMENT_PROVIDER", "UPI Gateway")
PAYMENT_WEBHOOK_SECRET = os.environ.get("PAYMENT_WEBHOOK_SECRET", "")

CASHFREE_CLIENT_ID = os.environ.get("CASHFREE_CLIENT_ID", "")
CASHFREE_CLIENT_SECRET = os.environ.get("CASHFREE_CLIENT_SECRET", "")
CASHFREE_ENV = os.environ.get("CASHFREE_ENV", "sandbox").lower()
CASHFREE_FALLBACK_PHONE = os.environ.get("CASHFREE_FALLBACK_PHONE", "9999999999")
