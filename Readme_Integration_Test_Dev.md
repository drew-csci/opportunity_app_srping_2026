# Integration Test README

## Purpose

This document explains the integration tests added for the new organization opportunity posting feature.

The selected integration test area is:
- successful submission shows a success message after redirect
- invalid submission shows an error message and does not redirect
- failed login shows the authentication error on the login page

These tests check how multiple parts of the application work together, including forms, views, templates, redirects, authentication, and Django messages.

---

## Integration Tests Added

File:
[pages/tests.py](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/pages/tests.py)

Test names:
- `test_successful_submission_shows_success_message_after_redirect`
- `test_invalid_submission_shows_error_message_and_does_not_redirect`
- `test_failed_login_shows_authentication_error_on_login_page`

---

## Why These Are Integration Tests

These are integration tests because they do not test just one isolated function.

Instead, they verify that several parts of the system work together:
- Django routing
- form validation
- view logic
- database writes
- redirect behavior
- template rendering
- Django messages framework
- authentication flow

This makes them stronger than a simple unit test for one method.

---

## Test 1: Successful Submission Shows A Success Message After Redirect

Test name:
`test_successful_submission_shows_success_message_after_redirect`

### What it checks

This test verifies the full success path for posting a new opportunity.

It confirms that:
- an organization user can submit a valid opportunity form
- the form creates a new `Opportunity` record
- the response redirects to the organization opportunities page
- a success message is attached and shown to the user

### How it works

1. The test logs in as an organization user.
2. It sends a valid `POST` request to the new opportunity route.
3. It uses `follow=True` so Django follows the redirect automatically.
4. It checks that the redirect ends at the organization opportunities page.
5. It reads Django messages from `response.wsgi_request`.
6. It verifies that the success message contains:
`has been posted successfully`

### Why it matters

This confirms the complete happy path of the new feature and proves the form submission flow works end to end.

---

## Test 2: Invalid Submission Shows An Error Message And Does Not Redirect

Test name:
`test_invalid_submission_shows_error_message_and_does_not_redirect`

### What it checks

This test verifies the failure path when the submitted form is invalid.

It confirms that:
- an invalid submission does not create an `Opportunity`
- the user stays on the posting page
- an error message is shown
- field-level validation appears in the rendered page

### How it works

1. The test logs in as an organization user.
2. It submits the form with invalid data by leaving `required_skills` empty.
3. It uses `follow=True` so the full response can be inspected.
4. It checks that the response remains on the posting page instead of redirecting.
5. It checks that no new `Opportunity` was created.
6. It reads Django messages and verifies the message:
`Please correct the highlighted fields and try again.`
7. It checks that the page shows the validation text:
`This field is required.`

### Why it matters

This confirms the app behaves safely when form data is incomplete and gives the user visible feedback instead of failing silently.

---

## Test 3: Failed Login Shows The Authentication Error On The Login Page

Test name:
`test_failed_login_shows_authentication_error_on_login_page`

### What it checks

This test verifies the login failure flow.

It confirms that:
- the login page returns successfully even when authentication fails
- the failed login error is shown to the user

### How it works

1. The test creates an organization user in the test database.
2. It submits a login request with the correct email but the wrong password.
3. It checks that the login page returns status `200` instead of redirecting.
4. It verifies that the page shows Django’s authentication error:
`Please enter a correct email and password. Note that both fields may be case-sensitive.`

### Why it matters

This confirms that failed authentication is visible to the user and that the login template correctly renders non-field form errors.

---

## Related Files

These tests are connected to the following files:

- [pages/tests.py](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/pages/tests.py)
Contains the integration tests.

- [pages/forms.py](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/pages/forms.py)
Contains `OpportunityForm` validation rules.

- [pages/views.py](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/pages/views.py)
Handles opportunity creation, success messages, and invalid form behavior.

- [templates/pages/organization_post_opportunity.html](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/templates/pages/organization_post_opportunity.html)
Displays the opportunity form and field-level validation messages.

- [templates/accounts/login.html](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/templates/accounts/login.html)
Displays authentication errors during failed login.

- [templates/base.html](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/templates/base.html)
Displays Django messages after redirects.

---

## How To Run The Integration Tests

Run the full `pages` test suite:

```bash
cd /Users/devhirpara/Opportunity/opportunity_app_srping_2026
/Users/devhirpara/Opportunity/venv/bin/python manage.py test pages --settings=opportunity_app.settings_test
```

Run only the message and redirect tests:

```bash
cd /Users/devhirpara/Opportunity/opportunity_app_srping_2026
/Users/devhirpara/Opportunity/venv/bin/python manage.py test \
pages.tests.OrganizationPostOpportunityTests.test_successful_submission_shows_success_message_after_redirect \
pages.tests.OrganizationPostOpportunityTests.test_invalid_submission_shows_error_message_and_does_not_redirect \
pages.tests.AuthenticationIntegrationTests.test_failed_login_shows_authentication_error_on_login_page \
--settings=opportunity_app.settings_test
```

---

## Expected Result

When these tests pass, they confirm that:
- valid opportunity creation gives the user a success message after redirect
- invalid submissions stay on the form and show an error
- failed login attempts show a visible authentication message

Together, these tests confirm that the new feature gives correct user feedback during both success and failure flows.
