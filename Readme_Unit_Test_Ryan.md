## Unit Test Explanation: test_custom_set_password_form_requires_matching_passwords

### Overview

This unit test validates that the `CustomSetPasswordForm` class correctly rejects password reset attempts where the user enters two different passwords. It's a critical security and UX test that ensures users cannot accidentally set passwords they cannot use to log in.

---

### Test Location

**File:** [accounts/tests.py](accounts/tests.py)  
**Class:** `AuthFlowTests`  
**Method:** `test_custom_set_password_form_requires_matching_passwords`

---

### What This Test Does (High Level)

The test verifies that Django's built-in form validation—inherited by our custom `CustomSetPasswordForm`—correctly detects and rejects form submissions where the two password fields don't match.

**In plain English:**
- A user tries to set a new password during password reset
- They enter "NewPassword123!" in the first field
- They enter "DifferentPassword456!" in the second field (typo or mistake)
- The form should detect this mismatch and reject the submission
- An error message should appear on the second password field mentioning the passwords don't match

---

### Step-by-Step Breakdown

#### Step 1: Import Required Form Class
```python
from accounts.forms import CustomSetPasswordForm
```
This imports our custom form class that we created to extend Django's built-in `SetPasswordForm`. The custom class adds placeholder text to enhance the user experience.

---

#### Step 2: Create a Test User
```python
test_user = self.user_model.objects.create_user(
    email='mismatch@example.com',
    username='mismatch@example.com',
    password='OldPassword123!'
)
```

**What happens:**
- Creates a new user in the test database
- Email: `mismatch@example.com`
- Username: `mismatch@example.com` (for compatibility with Django's auth system)
- Initial password: `OldPassword123!` (this is what they're trying to change)

**Why this matters:**
- `CustomSetPasswordForm` requires a `user` parameter in its constructor
- We need an actual user instance to test against
- The test database is separate from production, so we can safely create/delete test users

---

#### Step 3: Instantiate Form with Mismatched Passwords
```python
form = CustomSetPasswordForm(user=test_user, data={
    'new_password1': 'NewPassword123!',
    'new_password2': 'DifferentPassword456!'  # Doesn't match
})
```

**What happens:**
- Creates an instance of `CustomSetPasswordForm`
- Passes the test user so the form knows whose password we're changing
- Passes form data (what the user submitted):
  - `new_password1`: The first password field
  - `new_password2`: The confirmation password field (intentionally different)

**Why this setup:**
- This simulates a user submitting the password reset form with mismatched passwords
- The form doesn't know yet if it's valid—validation happens next

---

#### Step 4: Assert Form is Invalid
```python
self.assertFalse(form.is_valid())
```

**What happens:**
- Calls Django's form validation machinery
- The form checks all its fields and rules
- Returns `False` because passwords don't match
- Test passes if `form.is_valid()` returns `False`

**Why this matters:**
- This is the core assertion—if the form were valid with mismatched passwords, the test would fail
- It verifies that Django's password-matching validator is working

---

#### Step 5: Assert Error is on Correct Field
```python
self.assertIn('new_password2', form.errors)
```

**What happens:**
- `form.errors` is a dictionary where keys are field names and values are lists of error messages
- This assertion checks that the key `'new_password2'` exists in the errors dictionary
- Test passes if the error is on the second password field (where the mismatch occurred)

**Why this matters:**
- We want the error on `new_password2`, not on `new_password1` or as a general form error
- This tells the user exactly which field has the problem
- If the error were general, the user might be confused

**Example of what `form.errors` looks like:**
```python
{
    'new_password2': ["The two password fields didn't match."]
}
```

---

#### Step 6: Assert Error Message Mentions "Match"
```python
error_msg = str(form.errors['new_password2'][0]).lower()
self.assertIn('match', error_msg)
```

**What happens:**
1. `form.errors['new_password2']` gets the list of error messages for that field
2. `[0]` gets the first error message
3. `str()` converts it to a string (it's already a string, but this ensures it)
4. `.lower()` converts to lowercase for case-insensitive comparison
5. `self.assertIn('match', error_msg)` checks if the word "match" appears in the error

**Why this matters:**
- Ensures the error message is user-friendly and explains the problem
- Users see something like: "The two password fields didn't match."
- If we don't check the message, the field could have an error, but it could be misleading

**Example:**
```python
# Good error message (test passes):
"The two password fields didn't match."

# Bad error message (test fails):
"Invalid field"  # Doesn't explain the actual problem
```

---

### Why This Test Matters (Security & UX Perspective)

#### Security Risk Without This Test
If this validation were broken:
1. User tries to reset password with mismatched entries
2. Form doesn't reject it
3. First password is saved (the second is ignored), but user doesn't realize it
4. User tries to log in with the password they thought they set (the second one)
5. Login fails because that password was never saved
6. User is now locked out of their account

#### How This Test Prevents It
By testing that mismatched passwords always fail validation, we guarantee:
- Users cannot accidentally set an unusable password
- The form provides clear feedback on exactly what went wrong
- The error is user-friendly and actionable

---

### How to Run This Test

#### Run Just This One Test
```bash
python manage.py test accounts.tests.AuthFlowTests.test_custom_set_password_form_requires_matching_passwords
```

#### Run All Tests in the AuthFlowTests Class
```bash
python manage.py test accounts.tests.AuthFlowTests
```

#### Run All Tests in the Accounts App
```bash
python manage.py test accounts
```

#### Run with Verbose Output (Shows Each Test)
```bash
python manage.py test accounts -v 2
```

---

### Test Output Explanation

**If the test passes:**
```
test_custom_set_password_form_requires_matching_passwords (accounts.tests.AuthFlowTests) ... ok
```

**If the test fails:**
```
FAIL: test_custom_set_password_form_requires_matching_passwords (accounts.tests.AuthFlowTests)
AssertionError: False is not true
```

This would mean `form.is_valid()` returned `True` when it should return `False`, indicating the validation is broken.

---

### What This Test Relies On

1. **Django's Built-in Form Validation**
   - `SetPasswordForm` from `django.contrib.auth.forms`
   - Contains the password-matching validator

2. **Our Custom Form Class**
   - `CustomSetPasswordForm` in [accounts/forms.py](accounts/forms.py)
   - Extends `SetPasswordForm` and adds UI enhancements

3. **Test Database**
   - Isolated from production database
   - Cleaned up after each test runs

4. **Django's Test Client**
   - Provides the `self.assertFalse()`, `self.assertIn()` methods
   - Manages test setup/teardown

---

### What This Test Does NOT Check

- **Password strength validation** (that's a separate test)
- **Whether the password actually gets saved to the database** (that's tested in `test_password_reset_confirm_with_valid_token_updates_password`)
- **CSRF token presence** (tested separately)
- **Email sending** (tested in other password reset tests)

This test is narrowly focused on form-level validation.

---

### Real-World Scenario

Imagine a user on the password reset page:

```
Current page: Set Your New Password

Password: [NewPassword123!____________]
Confirm:  [Different12345____________]

[Set Password]
```

**Without this test passing:**
- User clicks "Set Password"
- Form accepts the mismatched passwords
- User redirected to success page
- User tries to log in with "Different12345"
- Login fails: "Invalid email or password"
- User thinks their account is broken

**With this test passing:**
- User clicks "Set Password"
- Form validation catches the mismatch
- User sees: "The two password fields didn't match."
- User corrects the typo
- User tries again with matching passwords
- Reset succeeds
- User can log in

---

### Summary

This test ensures that our password reset form is robust and prevents a common user error (mistyped password confirmation). By validating that Django's form validation is working correctly, we protect users from accidentally locking themselves out of their accounts after a password reset.

---

**Test Written By:** Ryan DeVita  
**Date:** March 2026  
**Related Issue:** #22 - Password Reset Implementation

For more information on the complete password reset implementation, see [Readme_Midterm_Ryan.md](Readme_Midterm_Ryan.md).
