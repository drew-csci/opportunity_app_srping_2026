"""
Test settings for Django tests.
Uses SQLite instead of PostgreSQL for easier testing.
"""
import os
from pathlib import Path

# Import all settings from base settings
from .settings import *

# Override database settings for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Use in-memory database for faster tests
    }
}

# Disable migrations for faster tests (optional)
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Disable password validation for tests (speeds up user creation)
AUTH_PASSWORD_VALIDATORS = []

# Use simple password hasher for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
