import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def reconcile_schema(apps, schema_editor):
    """
    Bring the database in line with the current model definitions regardless of
    which migration branches were applied (or faked) on this database.

    Handles:
      - Opportunity table: upgrade schema-1 columns to schema-2
      - StudentOpportunity table: create it if it was never written to the DB
      - Notification table: create it if missing
      - Message table: add is_read if the table was created before that column existed
    """
    connection = schema_editor.connection
    introspection = connection.introspection

    with connection.cursor() as cursor:
        existing_tables = set(introspection.table_names())

        # ── 1. Fix Opportunity ──────────────────────────────────────────────
        opp_table = 'pages_opportunity'
        if opp_table in existing_tables:
            opp_cols = {col.name for col in introspection.get_table_description(cursor, opp_table)}

            # Add missing schema-2 columns
            schema2_cols = {
                'cause':            "ALTER TABLE pages_opportunity ADD COLUMN cause varchar(200) NOT NULL DEFAULT ''",
                'location':         "ALTER TABLE pages_opportunity ADD COLUMN location varchar(200) NOT NULL DEFAULT ''",
                'duration':         "ALTER TABLE pages_opportunity ADD COLUMN duration varchar(200) NOT NULL DEFAULT ''",
                'skills_required':  "ALTER TABLE pages_opportunity ADD COLUMN skills_required text NOT NULL DEFAULT ''",
                'opportunity_type': "ALTER TABLE pages_opportunity ADD COLUMN opportunity_type varchar(200) NOT NULL DEFAULT ''",
                'is_active':        "ALTER TABLE pages_opportunity ADD COLUMN is_active boolean NOT NULL DEFAULT TRUE",
            }
            for col, sql in schema2_cols.items():
                if col not in opp_cols:
                    cursor.execute(sql)

            if 'created_at' not in opp_cols:
                cursor.execute("ALTER TABLE pages_opportunity ADD COLUMN created_at timestamp with time zone")
                if 'date_posted' in opp_cols:
                    cursor.execute("UPDATE pages_opportunity SET created_at = date_posted")
                cursor.execute("UPDATE pages_opportunity SET created_at = NOW() WHERE created_at IS NULL")
                cursor.execute("ALTER TABLE pages_opportunity ALTER COLUMN created_at SET NOT NULL")
                cursor.execute("ALTER TABLE pages_opportunity ALTER COLUMN created_at SET DEFAULT NOW()")

            # Drop schema-1 / leftover columns
            for col in ('status', 'date_posted', 'date_updated', 'application_deadline', 'required_skills'):
                if col in opp_cols:
                    cursor.execute(f"ALTER TABLE pages_opportunity DROP COLUMN {col}")

        # ── 2. Create StudentOpportunity if missing ─────────────────────────
        so_table = 'pages_studentopportunity'
        if so_table not in existing_tables:
            StudentOpportunity = apps.get_model('pages', 'StudentOpportunity')
            schema_editor.create_model(StudentOpportunity)
        else:
            so_cols = {col.name for col in introspection.get_table_description(cursor, so_table)}
            if 'date_pending' not in so_cols:
                cursor.execute("ALTER TABLE pages_studentopportunity ADD COLUMN date_pending timestamp with time zone NULL")
            if 'denial_reason' not in so_cols:
                cursor.execute("ALTER TABLE pages_studentopportunity ADD COLUMN denial_reason text NULL")

        # ── 3. Create Notification if missing ──────────────────────────────
        notif_table = 'pages_notification'
        if notif_table not in existing_tables:
            Notification = apps.get_model('pages', 'Notification')
            schema_editor.create_model(Notification)

        # ── 4. Fix Message table ───────────────────────────────────────────
        msg_table = 'pages_message'
        if msg_table in existing_tables:
            msg_cols = {col.name for col in introspection.get_table_description(cursor, msg_table)}
            if 'is_read' not in msg_cols:
                cursor.execute("ALTER TABLE pages_message ADD COLUMN is_read boolean NOT NULL DEFAULT FALSE")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0008_merge_20260427_2024'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField('opportunity', 'application_deadline'),
                migrations.RemoveField('opportunity', 'required_skills'),
            ],
            database_operations=[],
        ),
        migrations.RunPython(reconcile_schema, noop_reverse),
    ]
