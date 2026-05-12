import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def reconcile_schema(apps, schema_editor):
    """Reconcile schema - SQLite-compatible version."""
    connection = schema_editor.connection
    introspection = connection.introspection

    with connection.cursor() as cursor:
        existing_tables = set(introspection.table_names())

        # Create StudentOpportunity if missing
        so_table = 'pages_studentopportunity'
        if so_table not in existing_tables:
            StudentOpportunity = apps.get_model('pages', 'StudentOpportunity')
            schema_editor.create_model(StudentOpportunity)
        else:
            so_cols = {col.name for col in introspection.get_table_description(cursor, so_table)}
            if 'date_pending' not in so_cols:
                cursor.execute("ALTER TABLE pages_studentopportunity ADD COLUMN date_pending datetime NULL")

        # Create Notification if missing
        notif_table = 'pages_notification'
        if notif_table not in existing_tables:
            Notification = apps.get_model('pages', 'Notification')
            schema_editor.create_model(Notification)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0008_merge_20260427_2024'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(reconcile_schema, noop_reverse),
    ]
