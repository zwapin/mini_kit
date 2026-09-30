# IMPORTING STANDARD PACKAGES
import os

# IMPORTING LOCAL PACKAGES
from mini_kit.settings import REST_FRAMEWORK  # noqa: F401

SECRET_KEY = "mini-kit-tests"
DEBUG = False
ALLOWED_HOSTS = ["*"]
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = ["rest_framework", "mini_kit", "tests.sample_app"]
MIDDLEWARE = []
ROOT_URLCONF = "tests.urls"

SQLITE_DATABASE = {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
POSTGRES_DATABASE = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.getenv("DB_NAME", "mini_kit"),
    "USER": os.getenv("DB_USER", "postgres"),
    "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
    "HOST": os.getenv("DB_HOST", "localhost"),
    "PORT": os.getenv("DB_PORT", "5432"),
}
DATABASES = {"default": POSTGRES_DATABASE if os.getenv("DB_HOST") else SQLITE_DATABASE}

MINI_KIT_JWT_SECRET = "mini-kit-tests-secret-at-least-32-bytes-long"
