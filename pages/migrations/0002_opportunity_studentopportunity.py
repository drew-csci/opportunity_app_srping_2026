# Generated migration for StudentOpportunity model

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_opportunity'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentOpportunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='not_started', max_length=20)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('date_completed', models.DateTimeField(blank=True, null=True)),
                ('opportunity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_participants', to='pages.opportunity')),
                ('student', models.ForeignKey(limit_choices_to={'user_type': 'student'}, on_delete=django.db.models.deletion.CASCADE, related_name='student_opportunities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date_completed', '-date_joined'],
                'unique_together': {('student', 'opportunity')},
            },
        ),
    ]