# Fix 1: replace raw SQL notification insert with ORM
content = open('pages/views.py', encoding='utf-8').read()

old = '''            from django.db import connection as db_conn
            with db_conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO pages_notification (recipient_id, message, is_read, created_at, notification_type) VALUES (%s, %s, %s, NOW(), %s)",
                    [application.student.id, f"Your application to '{application.opportunity.title}' has been {decision}.", False, decision]
                )'''

new = '''            from pages.models import Notification
            Notification.objects.create(
                recipient=application.student,
                message=f"Your application to '{application.opportunity.title}' has been {decision}.",
                is_read=False,
            )'''

content = content.replace(old, new)

# Fix 2: reminder message must contain 'only for pending'
content = content.replace(
    "messages.error(request, 'Reminders can only be sent for applications that are still pending.')",
    "messages.error(request, 'Reminders are only for pending applications.')"
)

open('pages/views.py', 'w', encoding='utf-8').write(content)
print('done')