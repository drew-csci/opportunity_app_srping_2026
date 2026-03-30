# Plan: Build Organization Inbox with Student Messaging

## TL;DR
Create a one-way messaging system where students send messages to organizations through a dedicated form, and organizations view all received messages in an inbox sorted by date. Implement by adding a `Message` model, creating views for message creation and inbox display, and adding corresponding templates and URLs. This follows existing role-based patterns in the Django app.

---

## Steps

### Phase 1: Database & Core Model (Foundation)
1. **Create `Message` model** in pages/models.py
   - Fields: `sender` (FK to User, filtered to students only), `recipient` (FK to User, filtered to organizations only), `subject` (CharField), `body` (TextField), `created_at` (DateTimeField auto_now_add), `updated_at` (DateTimeField auto_now)
   - Meta: ordering by `-created_at` (newest first)
   - `__str__` method returning `f"{self.sender.display_name} to {self.recipient.display_name}: {self.subject}"`

2. **Create Django migration** for the new `Message` model
   - Run `python manage.py makemigrations` and apply `python manage.py migrate`

### Phase 2: Forms & Views (Business Logic)
3. **Create `MessageForm`** in pages/forms.py
   - Fields: `recipient` (ModelChoiceField filtering to user_type='organization'), `subject` (CharField), `body` (CharField with Textarea widget)
   - Auto-exclude: sender (will be set in view), created_at, updated_at

4. **Create `send_message` view** in pages/views.py
   - Method: GET displays form, POST saves message from authenticated student
   - Route: accessible only to students (`@login_required`, check `user_type == 'student'`)
   - Success: redirect to confirmation page or back to dashboard with message feedback
   - Recipient queryset: organizations only

5. **Create `organization_inbox` view** in pages/views.py
   - Retrieves all messages where `recipient == request.user` (only for organizations)
   - Queryset: `Message.objects.filter(recipient=request.user)` — auto-sorted by `-created_at`
   - *depends on step 4* (after view patterns established)
   - Pass context: `messages`, `sender_info`, `message_count`
   - Route: accessible only to organizations (`@login_required`, check `user_type == 'organization'`)

### Phase 3: URLs & Routing
6. **Add URL patterns** in pages/urls.py
   - Add path for `send_message` view: `/send-message/` → `send_message` view
   - Add path for `organization_inbox` view: `/inbox/` → `organization_inbox` view

### Phase 4: Templates & UI
7. **Create message send form template** at templates/pages/send_message.html
   - Extend `base.html`
   - Form with CSRF token, POST method
   - Fields: recipient dropdown, subject input, body textarea
   - Include cancel/back link
   - Follow existing Achievement form pattern from templates/pages/student_achievements.html

8. **Create inbox display template** at templates/pages/inbox.html
   - Extend `base.html`
   - Display list of messages in table or card layout
   - Columns: Sender name, Subject, Date received (formatted), Message preview
   - Clickable rows to view full message (or inline expansion)
   - Empty state message if no messages: "You have no messages yet."
   - Message count badge in header

9. **Create message detail view (optional modal/page)** at templates/pages/message_detail.html
   - Display full message (sender, subject, body, date received)
   - Back to inbox link
   - Include view for detail in views.py if creating separate page

10. **Update dashboard partial** templates/pages/s1_organization.html
    - Add navigation link to inbox (e.g., "View Inbox" or message icon with count)
    - Link to `/inbox/` with unread or total message count badge

11. **Update dashboard partial** templates/pages/s1_student.html
    - Add navigation link to send message page (e.g., "Send Feedback to Organization")
    - Link to `/send-message/`

### Phase 5: Integration & Polish
12. **Update base navigation** in templates/base.html (optional)
    - Add conditional navigation item for inbox (visible to organizations only)

13. **Add message feedback messages** using Django's messages framework in views
    - On successful message send: "Message sent successfully!"
    - On inbox load: optionally show "You have X messages"

---

## Relevant Files

**To Create:**
- pages/models.py — Add `Message` model class
- pages/forms.py — Add `MessageForm` class
- pages/views.py — Add `send_message` and `organization_inbox` views
- pages/urls.py — Add URL patterns for new views
- templates/pages/send_message.html — Messaging form template
- templates/pages/inbox.html — Inbox display template
- templates/pages/message_detail.html — Message detail view (optional)

**To Modify:**
- pages/models.py — Import User model if not present
- pages/forms.py — Import User model if not present, import Message model
- templates/pages/s1_student.html — Add link to send-message
- templates/pages/s1_organization.html — Add link to inbox with message count
- templates/base.html — (optional) Add conditional nav link to inbox

**Reference Patterns (Do Not Modify):**
- templates/pages/student_achievements.html — Follow form submission pattern for send_message template
- accounts/views.py — Reference `@login_required` decorator pattern
- pages/views.py existing `student_achievements` view — Reference queryset filtering, role-based access, and context passing

---

## Verification

1. **Model & Migration**
   - Run `python manage.py makemigrations` — should create migration without errors
   - Run `python manage.py migrate` — should apply without errors
   - Open Django shell: `python manage.py shell` → `from pages.models import Message` → verify no import errors

2. **Forms & Validation**
   - Test `MessageForm` with valid data (all fields filled) — should be valid
   - Test with missing recipient — form should show error
   - Test recipient dropdown only shows organizations — verify queryset filtering in db

3. **Views & Access Control**
   - As anonymous user: visit `/send-message/` → should redirect to login
   - As student user: visit `/send-message/` → should display form
   - As organization user: visit `/send-message/` → should be forbidden or redirect
   - As organization user: visit `/inbox/` → should display inbox
   - As student user: visit `/inbox/` → should be forbidden or redirect

4. **Functionality - Send Message**
   - Student fills out form with valid data and submits
   - Message appears in database (check Django admin or shell)
   - Recipient organization sees message in their inbox within 1-2 seconds

5. **Functionality - Inbox Display**
   - Organization user visits `/inbox/`
   - All messages sent to that organization are listed
   - Messages are ordered newest-to-oldest (by created_at descending)
   - Clicking message shows full details (if using detail view)
   - Empty state displays correctly if no messages

6. **UI/UX**
   - Dashboard shows "Send Feedback" link for students
   - Dashboard shows "View Inbox" link with message count for organizations
   - Forms are styled consistently with existing Achievement form
   - Navigation links work and are role-appropriate

---

## Decisions

1. **One-way messaging** — Students can send, organizations can receive. No reply functionality included per requirements.

2. **Dedicated messaging page** — Message form is a separate page (`/send-message/`), not embedded in profiles.

3. **Minimal message fields** — Only subject and body; no categories, priorities, or attachments. This reduces complexity and aligns with MVP approach.

4. **Basic inbox** — Sorted by date only; no search, filtering, or unread tracking at this stage.

5. **Role-based access** — Both send and inbox views check `user_type` to restrict access, consistent with existing patterns in app.

6. **Auto-timestamps** — `created_at` and `updated_at` fields use Django's auto_now_add and auto_now to eliminate manual timestamp management.

7. **User filtering** — Message model uses ForeignKey with `limit_choices_to` on both sender and recipient to enforce student→organization messaging at the DB level.

---

## Further Considerations

1. **Future Enhancement: Message Detail View** — Currently, inbox displays preview. Could create a separate detail page/modal to show full message. Recommend implementing after basic inbox is working.

2. **Future Enhancement: Pagination** — If organizations receive many messages, add Django pagination (`Paginator`) to inbox template.

3. **Admin Interface** — Message model should be registered with Django admin for staff/superusers to manage messages. Consider adding in a follow-up task.