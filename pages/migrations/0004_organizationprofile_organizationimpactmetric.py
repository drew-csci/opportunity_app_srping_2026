from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def sync_legacy_organization_tables(apps, schema_editor):
    """Align pre-existing organization profile tables with current model columns."""
    connection = schema_editor.connection
    introspection = connection.introspection

    OrganizationProfile = apps.get_model('pages', 'OrganizationProfile')
    OrganizationImpactMetric = apps.get_model('pages', 'OrganizationImpactMetric')

    existing_tables = set(introspection.table_names())
    profile_table = OrganizationProfile._meta.db_table
    metric_table = OrganizationImpactMetric._meta.db_table

    # Create missing profile table on fresh databases.
    if profile_table not in existing_tables:
        schema_editor.create_model(OrganizationProfile)
        existing_tables.add(profile_table)
    else:
        with connection.cursor() as cursor:
            profile_desc = introspection.get_table_description(cursor, profile_table)
        existing_columns = {col.name for col in profile_desc}
        table_q = schema_editor.quote_name(profile_table)

        # Legacy schema used `user_id`; current model expects `organization_id`.
        if 'organization_id' not in existing_columns and 'user_id' in existing_columns:
            with connection.cursor() as cursor:
                cursor.execute(f"ALTER TABLE {table_q} RENAME COLUMN user_id TO organization_id")
            existing_columns.remove('user_id')
            existing_columns.add('organization_id')

        # Ensure expected profile content columns exist.
        with connection.cursor() as cursor:
            if 'organization_name' not in existing_columns:
                cursor.execute(f"ALTER TABLE {table_q} ADD COLUMN organization_name varchar(200) NULL")
                existing_columns.add('organization_name')
            if 'mission' not in existing_columns:
                cursor.execute(f"ALTER TABLE {table_q} ADD COLUMN mission text NULL")
                existing_columns.add('mission')
            if 'location' not in existing_columns:
                cursor.execute(f"ALTER TABLE {table_q} ADD COLUMN location varchar(200) NULL")
                existing_columns.add('location')
            if 'contact_info' not in existing_columns:
                cursor.execute(f"ALTER TABLE {table_q} ADD COLUMN contact_info text NULL")

    # Create missing impact metrics table on legacy databases.
    if metric_table not in existing_tables:
        schema_editor.create_model(OrganizationImpactMetric)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_sync_legacy_application_schema'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='OrganizationProfile',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('organization_name', models.CharField(blank=True, max_length=200)),
                        ('mission', models.TextField(blank=True)),
                        ('location', models.CharField(blank=True, max_length=200)),
                        ('contact_info', models.TextField(blank=True)),
                        (
                            'organization',
                            models.OneToOneField(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name='organization_profile',
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                ),
                migrations.CreateModel(
                    name='OrganizationImpactMetric',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title', models.CharField(max_length=200)),
                        ('value', models.CharField(max_length=200)),
                        ('description', models.TextField(blank=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        (
                            'organization_profile',
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name='impact_metrics',
                                to='pages.organizationprofile',
                            ),
                        ),
                    ],
                    options={
                        'ordering': ['-created_at'],
                    },
                ),
            ],
            database_operations=[],
        ),
        migrations.RunPython(sync_legacy_organization_tables, noop_reverse),
    ]
