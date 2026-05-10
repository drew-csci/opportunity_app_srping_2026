# Generated migration for adding pending status to StudentOpportunity

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_opportunity_studentopportunity'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentopportunity',
            name='date_pending',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='studentopportunity',
            name='status',
            field=models.CharField(
                choices=[
                    ('not_started', 'Not Started'),
                    ('in_progress', 'In Progress'),
                    ('pending', 'Pending Approval'),
                    ('completed', 'Completed'),
                ],
                default='not_started',
                max_length=20,
            ),
        ),
    ]
