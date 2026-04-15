# Readme_Unit_Test_Nakiwe

## Purpose
This document explains the unit tests created in `pages/tests.py` for application tracking and status transitions in the Django app. It focuses on the behavior of the application flow and how each test verifies key functionality.

## Test file location
- `pages/tests.py`

## Test class
- `ApplicationTrackingTests(TestCase)`

### setUp
- Creates:
  - a student user (`user_type='student'`)
  - an organization user (`user_type='organization'`)
  - an opportunity (active) owned by the organization

## Tests
1. `test_application_auto_responded_date_on_accept_and_deny`
   - Creates an application in `PENDING` status with no `responded_date`
   - Updates the status to `ACCEPTED` and saves
   - Asserts `status` becomes `accepted` and `responded_date` is set automatically by model `save()`
   - Repeats for `DENIED` status path

2. `test_apply_to_opportunity_submits_pending_and_save_draft`
   - Logs in as student
   - POSTs to `apply_to_opportunity` with `action='submit'`
   - Checks redirect to `application_detail` and database entry with `pending` status
   - Creates another opportunity and tests `action='save_draft'`
   - Asserts status is `draft`

3. `test_prevent_duplicate_apply_for_non_draft`
   - Creates a `PENDING` application
   - GETs `apply_to_opportunity` again
   - Expects redirect to existing application detail and warning message

4. `test_my_applications_student_only`
   - Creates two applications for student
   - GETs `my_applications` as student, expects both in context and status 200
   - GETs as organization, expects redirect to `screen1`

5. `test_organization_applications_filters_and_permission`
   - Creates draft/pending/accepted applications
   - GETs `organization_applications` as organization, expects only pending+accepted in context
   - GETs as student, expects redirect to `screen1`

6. `test_review_application_status_change`
   - Creates pending application
   - Posts decision `accepted` as organization
   - Asserts redirect to organization page, status==accepted, responded_date set
   - Posts invalid decision and asserts error message

7. `test_opportunity_detail_shows_application_and_permission`
   - Creates application and GETs opportunity detail as student
   - Asserts opportunity and application in context
   - As organization, expects redirect to `screen1`

## Running tests
From project root:

```bash
source venv/bin/activate
python manage.py test pages
```
