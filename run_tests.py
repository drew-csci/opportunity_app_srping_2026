#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportunity_app.settings')
sys.path.insert(0, r'c:\Users\ravio\opportunity_2026\opportunity_app_srping_2026')

django.setup()

# Now run tests
from django.test.utils import get_runner
from django.conf import settings

TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=2, interactive=False, keepdb=True)

# Run only messaging tests
failures = test_runner.run_tests(['pages.test_messaging'])

sys.exit(bool(failures))
