"""
Test-only settings: inherits everything from settings.py but replaces
the remote PostgreSQL database with a local SQLite file so that the
test runner can create/destroy the test database without needing
CREATEDB privileges on the shared server.
"""
from .settings import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}
