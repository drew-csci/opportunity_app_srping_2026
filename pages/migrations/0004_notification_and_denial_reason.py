# Generated migration for Notification model and denial_reason field

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_add_pending_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentopportunity',
            name='denial_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(
                    choices=[
                        ('completion_denied', 'Completion Denied'),
                        ('completion_approved', 'Completion Approved'),
                    ],
                    max_length=30,
                )),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('student_opportunity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='pages.studentopportunity')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
