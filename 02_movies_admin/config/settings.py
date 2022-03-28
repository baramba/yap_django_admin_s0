import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parent.parent


# Load variables from .env
load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", False) == "True"

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

include(
    "components/appdef.py",
)

include(
    "components/database.py",
)

include(
    "components/auth_password_validators.py",
)


# debug sql
if DEBUG:
    include(
        "components/logging.py",
    )

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOCALE_PATH = ["movies/locale"]

STATIC_URL = "static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
