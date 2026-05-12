from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0011_contactmessage'),
        ('pages', '0002_conversation_message_faqsuggestion'),
        ('pages', '0003_merge_0002_opportunity_0002_organizationfollow'),
        ('pages', '0005_merge_20260412_0001'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteerprofile',
            name='location',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='volunteerprofile',
            name='interests',
            field=models.TextField(blank=True),
        ),
    ]
