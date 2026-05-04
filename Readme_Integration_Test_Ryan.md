# Integration Test Explanation: test_complete_password_reset_flow_returns_to_login

## Overview

This document explains how the integration test named `test_complete_password_reset_flow_returns_to_login` works in `accounts/tests.py`.

This test validates the full password reset journey across multiple layers of the app:

- URL routing
- View logic
- Form handling
- Email dispatch
- Token generation and validation
- Password persistence in the database
- Authentication with the new password
- Access to a protected page after login

Because it exercises many components together, it is an integration test, not just a unit test.

## Where the test lives

- File: `accounts/tests.py`
- Class: `AuthFlowTests`
- Method: `test_complete_password_reset_flow_returns_to_login`

## What this test verifies end to end

The method checks this real user flow:

1. User requests a password reset using their email.
2. App redirects to the password-reset confirmation screen.
3. App sends a reset email.
4. User opens the reset link.
5. User submits a new valid password.
6. Password in the database is updated.
7. User can log in with the new password.
8. User can access the dashboard while authenticated.

If any one of those breaks, the test fails.

## Step-by-step explanation of the method

### Step 1: Create a user for the scenario

The test creates a user with a known old password so it can later confirm that password changed.

- Email: `complete@example.com`
- Old password: `OldPassword123!`

This gives a clean and isolated test identity.

### Step 2: Submit password reset request

The test sends a POST to the password reset endpoint with that user email.

Expected result:

- Redirect to `password_reset_done`

This validates request handling and URL wiring for reset initiation.

### Step 3: Confirm reset email was generated

It checks the in-memory test mailbox and verifies:

- Exactly one email exists
- Subject includes `Opportunity App password reset`

This confirms email integration is functioning.

### Step 4: Build and open reset confirm URL

The test generates:

- `uidb64` for the user
- reset token for that user
- URL for `password_reset_confirm`

Then it performs a GET on that URL and expects HTTP 200.

This validates token-based link access and confirm-page rendering.

### Step 5: Submit new password on confirm page

The test posts matching values for:

- `new_password1`
- `new_password2`

Expected result:

- Redirect to `password_reset_complete`

This validates form processing and successful reset completion flow.

### Step 6: Verify database actually changed password

After `refresh_from_db`, the test asserts:

- new password is valid for user
- old password is no longer valid

This is a critical persistence check. It ensures real state change, not just a redirect.

### Step 7: Verify login works with new password

The test uses `client.login` with the new password and expects success.

This proves reset output is usable in authentication.

### Step 8: Verify authenticated access to dashboard

The test requests the dashboard route and expects:

- HTTP 200
- user in response context is authenticated

This confirms session auth is active after login and protected page access works.

## Why this is one of the highest-value tests

This single method catches regressions across the entire reset stack:

- Broken URL names
- View misconfiguration
- Email dispatch failure
- Token issues
- Password write failures
- Authentication mismatch after reset

It is high value because it mirrors the exact path a real user takes.

## Important implementation detail

The current method checks that email was sent, but it does not parse the link out of the email body. Instead, it generates `uidb64` and token directly using Django utilities.

That is still valid for an integration test of reset mechanics.

## How to run this specific test

Run only this method:

```bash
python manage.py test accounts.tests.AuthFlowTests.test_complete_password_reset_flow_returns_to_login
```

Run the full auth test class:

```bash
python manage.py test accounts.tests.AuthFlowTests
```

Run all account tests:

```bash
python manage.py test accounts
```

## Expected success output pattern

You should see the method reported as `ok` in Django test output.
If it fails, the assertion message tells you which stage of the end-to-end flow broke.

## Summary

The integration test `test_complete_password_reset_flow_returns_to_login` is a full-flow safety net that validates the complete password reset user journey, from request to authenticated access after reset. It is one of the best tests to keep for preventing high-impact regressions.
