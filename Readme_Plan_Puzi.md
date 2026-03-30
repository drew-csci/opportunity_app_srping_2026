# Midterm Plan - US-008: Send Application Reminder to Organization

## Selected task
US-008 - Send Application Reminder to Organization.

## Goal
Allow student users to send a reminder to the organization for applications that are currently in **Applied** status, and disable the reminder option for applications that are **Accepted** or **Declined**.

## Step-by-step plan
1. Locate the student dashboard view and template that render the application list (student home page).
2. Update the application list rendering so that the "Remind About Me" button is shown only for `status == 'applied'` (via `app.can_remind`).
3. In the template, keep the button hidden for `accepted/declined` states (no disabled button needed).
4. Add or confirm the URL route exists for reminder submission (e.g. `application/<int:application_id>/remind/`).
5. Add backend logic in `send_application_reminder` view to confirm:
   - the user is authenticated and is a student,
   - they own the application,
   - the application status is still `applied`,
   - rate limiting applies (like one reminder per 24h).
6. On successful POST, persist `ApplicationReminder`, send notification email, and redirect to `dashboard` with a success message.
7. On failure, redirect to `dashboard` with an error message (no JSON API mode, standard form POST flow).
8. Write tests in `pages/tests.py` to cover:
   - owner can send reminder (redirect to dashboard),
   - organization user cannot send reminder (redirect to dashboard),
   - non-owner cannot send reminder (redirect to dashboard),
   - accepted/declined applications do not allow reminders,
   - reminder button is present only for applied apps in dashboard render.
9. Add short docs in README files describing feature and test behavior.

## Expected outcome
- Student dashboard shows a "Remind About Me" button only for applications with status **Applied**.
- Clicking the button triggers a POST to the reminder endpoint.
- Invalid attempts (non-owner, organization, accepted/declined) are blocked.
- Request flow returns to student dashboard with message feedback.
- Unit/integration tests pass and validate the behavior end-to-end.
