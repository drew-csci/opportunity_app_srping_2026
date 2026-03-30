#!/usr/bin/env python
"""
Run Test #1 Integration Tests: End-to-End Student Message Flow
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
django.setup()

import unittest
from django.test.utils import get_runner
from django.conf import settings

if __name__ == '__main__':
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    failures = test_runner.run_tests(['pages.tests.EndToEndStudentMessageFlowTest'])
    exit(0 if not failures else 1)
