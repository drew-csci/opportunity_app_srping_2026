# Midterm Code Explanation

## Feature Implemented
I implemented the **"Remind About Me"** feature for pending volunteer applications.

## Purpose
The purpose of this feature is to allow a student volunteer to send a reminder to an organization when their application is still waiting for review.

## What I Changed
I updated the student dashboard so that the **"Remind About Me"** button only appears for applications that are still in the **Applied** status.

I also updated the backend reminder view so that:
- it only accepts reminder requests for eligible applications,
- it checks the application status before sending the reminder,
- and it redirects the user back to the dashboard after processing the request.

## Files Updated
- `dashboard.html`
- `views.py`
- `tests.py`

## How the Feature Works
1. A student logs into the dashboard.
2. In the **Your Applications** section, the system checks each application.
3. If the application is still pending, the page shows the **"Remind About Me"** button.
4. When the student clicks the button, a POST request is sent to the backend.
5. The backend verifies that the application can still receive a reminder.
6. The system processes the reminder and redirects the user back to the dashboard.

## Rules Enforced
- The reminder button appears only for applications in **Applied** status.
- The reminder button does not appear for **Accepted** or **Declined** applications.
- Unauthorized users cannot send reminders.
- The request is handled using standard Django form submission and redirect behavior.

## Example
If a student has submitted an application and the status is still **Applied**, they can click **"Remind About Me"** to notify the organization to review the application sooner.
