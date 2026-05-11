#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # (Note: This line was used to run the tests on my end due to lack of perms. Not needed for final
    # project, but kept here as comment for future reference): 
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportunity_app.test_settings_local')
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportunity_app.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
