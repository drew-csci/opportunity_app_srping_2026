import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportunity_app.settings')

import django
django.setup()

from django.db import connection
from accounts.models import User
from pages.models import Opportunity

org = User.objects.get(email='org_oppo@drew.edu')
student = User.objects.get(email='student_oppo@drew.edu')
opp = Opportunity.objects.filter(organization=org, is_active=True).first()
print('opportunity:', opp, 'id:', opp.id)

with connection.cursor() as cursor:
    cursor.execute("""
        INSERT INTO pages_application
        (student_id, opportunity_id, organization_id, status, applied_date, applied_at, updated_at, cover_letter, message, opportunity_title)
        VALUES (%s, %s, %s, %s, NOW(), NOW(), NOW(), %s, %s, %s)
        RETURNING id
    """, [student.id, opp.id, org.id, 'pending', 'I want to help!', 'I want to help!', opp.title])
    app_id = cursor.fetchone()[0]
    
print('app_id:', app_id)
print('Done!')