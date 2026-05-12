import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def sync_legacy_tables(apps, schema_editor):
    connection = schema_editor.connection
    introspection = connection.introspection
    Application = apps.get_model('pages', 'Application')
    existing_tables = set(introspection.table_names())
    if Application._meta.db_table not in existing_tables:
        schema_editor.create_model(Application)
        return
    with connection.cursor() as cursor:
        app_desc = introspection.get_table_description(cursor, Application._meta.db_table)
    existing_columns = {col.name for col in app_desc}
    Opportunity = apps.get_model('pages', 'Opportunity')
    table_q = schema_editor.quote_name(Application._meta.db_table)
    with connection.cursor() as cursor:
        if 'applied_date' not in existing_columns:
            cursor.execute(f'ALTER TABLE {table_q} ADD COLUMN applied_date timestamp with time zone NULL')
        if 'responded_date' not in existing_columns:
            cursor.execute(f'ALTER TABLE {table_q} ADD COLUMN responded_date timestamp with time zone NULL')
        if 'message' not in existing_columns:
            cursor.execute(f'ALTER TABLE {table_q} ADD COLUMN message text NULL')
        if 'opportunity_id' not in existing_columns:
            cursor.execute(f'ALTER TABLE {table_q} ADD COLUMN opportunity_id bigint NULL')
    table = Application._meta.db_table
    opp_table = Opportunity._meta.db_table
    with connection.cursor() as cursor:
        if 'applied_date' in existing_columns:
            cursor.execute(f'UPDATE {table} SET applied_date = CURRENT_TIMESTAMP WHERE applied_date IS NULL')
        if 'message' in existing_columns:
            cursor.execute(f"UPDATE {table} SET message = '' WHERE message IS NULL")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_organizationfollow'),
        ('pages', '0002_opportunity'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Application',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('status', models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending'), ('accepted', 'Accepted'), ('denied', 'Denied')], default='draft', max_length=20)),
                        ('applied_date', models.DateTimeField(auto_now_add=True)),
                        ('responded_date', models.DateTimeField(blank=True, null=True)),
                        ('message', models.TextField()),
                        ('opportunity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='pages.opportunity')),
                        ('student', models.ForeignKey(limit_choices_to={'user_type': 'student'}, on_delete=django.db.models.deletion.CASCADE, related_name='applications', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={'ordering': ['-applied_date']},
                ),
            ],
            database_operations=[],
        ),
        migrations.RunPython(sync_legacy_tables, noop_reverse),
    ]
