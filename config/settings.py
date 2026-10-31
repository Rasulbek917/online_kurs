from pathlib import Path
import os
from importlib.util import find_spec
from django.core.exceptions import ImproperlyConfigured
BASE_DIR = Path(__file__).resolve().parent.parent
ON_VERCEL = bool(os.environ.get("VERCEL"))
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-local-development-only")
if ON_VERCEL and SECRET_KEY == "django-insecure-local-development-only":
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY in Vercel Environment Variables.")
DEBUG = os.environ.get("DJANGO_DEBUG", "false" if ON_VERCEL else "true").lower() in {"1", "true", "yes"}
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("ALLOWED_HOSTS", ".vercel.app,localhost,127.0.0.1").split(",") if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]
if ON_VERCEL:
    CSRF_TRUSTED_ORIGINS.append("https://*.vercel.app")
INSTALLED_APPS = (["jazzmin"] if find_spec("jazzmin") else []) + [ "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles", "academy"]
JAZZMIN_SETTINGS = {
    "site_title": "DarsHub Admin",
    "site_header": "DarsHub",
    "site_brand": "DarsHub",
    "welcome_sign": "DarsHub boshqaruv paneliga xush kelibsiz",
    "copyright": "DarsHub",
    "show_ui_builder": False,
    "custom_css": "academy/jazzmin.css",
}
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware"]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates", "DIRS":[BASE_DIR / "templates"], "APP_DIRS":True, "OPTIONS":{"context_processors":["django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "config.wsgi.application"
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    import dj_database_url
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=ON_VERCEL)}
elif ON_VERCEL:
    raise ImproperlyConfigured("Set DATABASE_URL to a persistent PostgreSQL database in Vercel.")
else:
    DATABASES = {"default":{"ENGINE":"django.db.backends.sqlite3", "NAME":BASE_DIR / "db.sqlite3"}}
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / ".vercel_static"
STATICFILES_DIRS = [BASE_DIR / "academy" / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "")
if AWS_STORAGE_BUCKET_NAME:
    if ON_VERCEL and not all(os.environ.get(name) for name in ("AWS_S3_ENDPOINT_URL", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")):
        raise ImproperlyConfigured("Set the S3 endpoint and credentials in Vercel Environment Variables.")
    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3.S3Storage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
    AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL")
    AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "auto")
    AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN") or None
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False
elif ON_VERCEL:
    raise ImproperlyConfigured("Set AWS_STORAGE_BUCKET_NAME and S3 credentials for persistent media storage on Vercel.")
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
