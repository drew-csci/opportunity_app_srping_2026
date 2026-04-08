# Established testing settings file that needed to be created to validate the tests on my end, since
# I do not have administrative access to the database.

from opportunity_app.settings import *  # absolute import on purpose

# Keep critical settings explicit for test runner stability
ROOT_URLCONF = "opportunity_app.urls"
WSGI_APPLICATION = "opportunity_app.wsgi.application"
AUTH_USER_MODEL = "accounts.User"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}