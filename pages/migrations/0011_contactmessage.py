from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0010_merge_20260512_1507'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('role', models.CharField(choices=[('student', 'Volunteer / Student'), ('organization', 'Organization')], max_length=20)),
                ('inquiry_type', models.CharField(choices=[('general', 'General Inquiry'), ('technical', 'Technical Support'), ('organization', 'Organization Support')], max_length=20)),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
