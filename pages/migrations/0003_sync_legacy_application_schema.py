import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def sync_legacy_tables(apps, schema_editor):
    """Align legacy pages tables with current model columns without data loss."""
    connection = schema_editor.connection
    introspection = connection.introspection

    Opportunity = apps.get_model('pages', 'Opportunity')
    Application = apps.get_model('pages', 'Application')

    existing_tables = set(introspection.table_names())

    # Create missing tables for fresh databases.
    if Opportunity._meta.db_table not in existing_tables:
        schema_editor.create_model(Opportunity)
        existing_tables.add(Opportunity._meta.db_table)

    if Application._meta.db_table not in existing_tables:
        schema_editor.create_model(Application)
        return

    with connection.cursor() as cursor:
        app_desc = introspection.get_table_description(cursor, Application._meta.db_table)

    existing_columns = {col.name for col in app_desc}

    # Add columns required by the current model if they are missing.
    table_q = schema_editor.quote_name(Application._meta.db_table)
    with connection.cursor() as cursor:
        if 'applied_date' not in existing_columns:
            cursor.execute(f"ALTER TABLE {table_q} ADD COLUMN applied_date timestamp with time zone NULL")
            existing_columns.add('applied_date')
        if 'responded_date' not in existing_columns:
            cursor.execute(f"ALTER TABLE {table_q} ADD COLUMN responded_date timestamp with time zone NULL")
            existing_columns.add('responded_date')
        if 'message' not in existing_columns:
            cursor.execute(f"ALTER TABLE {table_q} ADD COLUMN message text NULL")
            existing_columns.add('message')
        if 'opportunity_id' not in existing_columns:
            cursor.execute(f"ALTER TABLE {table_q} ADD COLUMN opportunity_id bigint NULL")
            existing_columns.add('opportunity_id')

    # Backfill from legacy columns when present.
    table = Application._meta.db_table
    opp_table = Opportunity._meta.db_table

    with connection.cursor() as cursor:
        if 'applied_at' in existing_columns and 'applied_date' in existing_columns:
            cursor.execute(
                f"""
                UPDATE {table}
                SET applied_date = COALESCE(applied_date, applied_at)
                WHERE applied_date IS NULL
                """
            )

        if 'cover_letter' in existing_columns and 'message' in existing_columns:
            cursor.execute(
                f"""
                UPDATE {table}
                SET message = COALESCE(message, cover_letter)
                WHERE message IS NULL
                """
            )

        if (
            'opportunity_title' in existing_columns
            and 'organization_id' in existing_columns
            and 'opportunity_id' in existing_columns
        ):
            cursor.execute(
                f"""
                UPDATE {table}
                SET opportunity_id = (
                    SELECT o.id
                    FROM {opp_table} o
                    WHERE o.title = {table}.opportunity_title
                      AND o.organization_id = {table}.organization_id
                    ORDER BY o.id
                    LIMIT 1
                )
                WHERE opportunity_id IS NULL
                """
            )

        if 'applied_date' in existing_columns:
            cursor.execute(
                f"""
                UPDATE {table}
                SET applied_date = CURRENT_TIMESTAMP
                WHERE applied_date IS NULL
                """
            )

        if 'message' in existing_columns:
            cursor.execute(
                f"""
                UPDATE {table}
                SET message = ''
                WHERE message IS NULL
                """
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_organizationfollow'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Opportunity',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title', models.CharField(max_length=200)),
                        ('description', models.TextField()),
                        ('cause', models.CharField(max_length=200)),
                        ('location', models.CharField(max_length=200)),
                        ('duration', models.CharField(max_length=200)),
                        ('skills_required', models.TextField()),
                        ('opportunity_type', models.CharField(max_length=200)),
                        ('is_active', models.BooleanField(default=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        (
                            'organization',
                            models.ForeignKey(
                                limit_choices_to={'user_type': 'organization'},
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name='opportunities',
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={'ordering': ['-created_at']},
                ),
                migrations.CreateModel(
                    name='Application',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        (
                            'status',
                            models.CharField(
                                choices=[
                                    ('draft', 'Draft'),
                                    ('pending', 'Pending'),
                                    ('accepted', 'Accepted'),
                                    ('denied', 'Denied'),
                                ],
                                default='draft',
                                max_length=20,
                            ),
                        ),
                        ('applied_date', models.DateTimeField(auto_now_add=True)),
                        ('responded_date', models.DateTimeField(blank=True, null=True)),
                        ('message', models.TextField()),
                        (
                            'opportunity',
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name='applications',
                                to='pages.opportunity',
                            ),
                        ),
                        (
                            'student',
                            models.ForeignKey(
                                limit_choices_to={'user_type': 'student'},
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name='applications',
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={'ordering': ['-applied_date']},
                ),
            ],
            database_operations=[],
        ),
        migrations.RunPython(sync_legacy_tables, noop_reverse),
    ]
