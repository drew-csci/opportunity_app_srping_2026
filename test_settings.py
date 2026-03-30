"""
Test settings for running tests with SQLite instead of PostgreSQL.
This allows tests to run without requiring database creation permissions.
"""
from opportunity_app.settings import *

# Use SQLite for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Use in-memory database for tests
    }
}
