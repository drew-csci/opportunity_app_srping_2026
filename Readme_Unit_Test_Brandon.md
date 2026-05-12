# Unit Test Documentation — Search & Filter Feature
### Brandon Jachera | Spring 2026

---

## Test Overview

**Test Name:** `test_no_query_returns_all_active_opportunities`
**Class:** `Screen1NoQueryReturnsAllActiveOpportunitiesTest`
**File:** `pages/tests.py`
**Command to run:** `python manage.py test pages.tests --verbosity=2`

**What it tests:**
When a logged-in student visits the Volunteer Opportunities page (`/screen1/`) without entering any search keyword or applying any filters, the page should return every opportunity that is marked as active in the database — no more, no less.

---

## How the Test Works — Step by Step

### Step 1 — Imports

```python
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User
from .models import Opportunity
```

| Import | Purpose |
|---|---|
| `TestCase` | The base class for all Django unit tests. It wraps each test in a database transaction that is rolled back after the test finishes, so test data never pollutes the real database |
| `Client` | A test HTTP client that simulates a browser making requests to the app without needing a real server running |
| `reverse` | Converts a URL name (e.g., `'screen1'`) into its actual path (`/screen1/`), so the test doesn't break if the URL path ever changes |
| `User` | The custom user model from the accounts app, used to create test users |
| `Opportunity` | The opportunity model, used to create test opportunity records |

---

### Step 2 — The `setUp` Method

```python
def setUp(self):
    ...
```

`setUp` runs automatically **before every test method** in the class. Its job is to build the test data that the test will run against. Think of it as the preparation stage — it creates a clean, known state in the test database before anything is checked.

#### Creating the Organization User

```python
self.org_user = User.objects.create_user(
    username='testorg@example.com',
    email='testorg@example.com',
    password='testpass123',
    user_type='organization',
)
```

The `Opportunity` model requires a ForeignKey to an organization user. This creates a dummy organization account in the test database purely to satisfy that relationship. Its credentials are never used to log in.

#### Creating the Student User

```python
self.student_user = User.objects.create_user(
    username='teststudent@example.com',
    email='teststudent@example.com',
    password='testpass123',
    user_type='student',
)
```

The `/screen1/` view is protected by `@login_required`. A student user is created so the test can log in and access the page. Without this, every request would be redirected to the login page and the test would fail.

#### Creating Two Active Opportunities

```python
self.opp1 = Opportunity.objects.create(
    title='Park Cleanup Volunteer',
    ...
    is_active=True,
)
self.opp2 = Opportunity.objects.create(
    title='Coding Bootcamp Internship',
    ...
    is_active=True,
)
```

Two distinct opportunities are created with `is_active=True`. They are intentionally different — one is a volunteer listing in Chicago and one is an internship that is remote — to confirm the view returns all active listings regardless of their content.

#### Creating One Inactive Opportunity

```python
self.opp_inactive = Opportunity.objects.create(
    title='Inactive Listing',
    ...
    is_active=False,
)
```

This is the most important piece of test data. It is created with `is_active=False`, which means the view's baseline query (`Opportunity.objects.filter(is_active=True)`) should exclude it. If this listing shows up in the results, the test will fail — which is exactly what we want. A test that can only pass should also be able to fail for the right reason.

#### Logging In

```python
self.client = Client()
self.client.login(email='teststudent@example.com', password='testpass123')
```

A `Client` instance is created and the student user logs in. From this point forward, any requests made through `self.client` will behave as if that student is logged into the app in a browser.

---

### Step 3 — The Test Method

```python
def test_no_query_returns_all_active_opportunities(self):
    response = self.client.get(reverse('screen1'))
    ...
```

The actual test method. Django recognizes any method whose name starts with `test_` as a test case to run automatically.

#### Making the Request

```python
response = self.client.get(reverse('screen1'))
```

The test client sends a plain GET request to `/screen1/` with no query parameters at all — no `?q=`, no `?location=`, nothing. This simulates a student simply landing on the opportunities page for the first time, before they have typed anything into the search bar.

#### Assertion 1 — The page loaded successfully

```python
self.assertEqual(response.status_code, 200)
```

Checks that the server responded with HTTP 200 OK. If the view crashed, returned a 404, or redirected to login, this assertion would fail immediately and tell us the page didn't load at all — before we even check the data.

#### Assertion 2 — Reading the context

```python
opportunities = response.context['opportunities']
```

Django's test client gives access to the template context that the view passed to the page. Rather than parsing HTML to find opportunity titles, the test reads the `opportunities` queryset directly from the context. This is cleaner and more reliable — it tests what the view computed, not how the template happened to render it.

#### Assertion 3 — Both active opportunities are present

```python
self.assertIn(self.opp1, opportunities)
self.assertIn(self.opp2, opportunities)
```

Confirms that each of the two active opportunities created in `setUp` is included in the results. `assertIn` checks that the object is a member of the queryset. If either is missing, the test fails and reports which one was absent.

#### Assertion 4 — The inactive opportunity is excluded

```python
self.assertNotIn(self.opp_inactive, opportunities)
```

Confirms that the inactive listing is **not** in the results. This is the core behavioral check — it proves the `is_active=True` filter in the view is actually working. Without this assertion, a bug that returned all opportunities (including inactive ones) would go undetected.

#### Assertion 5 — Exact count check

```python
self.assertEqual(opportunities.count(), 2)
```

Confirms the total number of results is exactly 2. This catches an edge case that the `assertIn` checks alone would miss: if somehow extra unexpected opportunities appeared in the results, the count would be wrong. Together with the previous assertions, this ensures the result set is exactly `{opp1, opp2}` — nothing more, nothing less.

---

## Why a Separate Test Database is Used

The project's main database is a cloud-hosted PostgreSQL server. Django needs to create and destroy a fresh database for each test run, and the database user (`oppo_app`) does not have permission to create databases on that server.

To solve this, `settings.py` was updated to detect when tests are running and automatically switch to a local SQLite database:

```python
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'test_db.sqlite3',
        }
    }
```

This means:
- Running `python manage.py runserver` → uses the cloud PostgreSQL database (normal operation)
- Running `python manage.py test` → uses a temporary local SQLite database (test isolation)

The test database is created fresh at the start of the test run, all migrations are applied to it automatically, and it is destroyed when the tests finish. No test data ever touches the real database.

---

## Test Output

When run with `--verbosity=2`, a passing test looks like this:

```
Creating test database for alias 'default'...
Found 1 test(s).
...
test_no_query_returns_all_active_opportunities
  (pages.tests.Screen1NoQueryReturnsAllActiveOpportunitiesTest) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.378s

OK
Destroying test database for alias 'default'...
```

---

## Summary of What Is Being Proved

| Assertion | What it proves |
|---|---|
| `status_code == 200` | The page loads without errors when no search is submitted |
| `assertIn(opp1, ...)` | Active opportunity #1 appears in the unfiltered results |
| `assertIn(opp2, ...)` | Active opportunity #2 appears in the unfiltered results |
| `assertNotIn(opp_inactive, ...)` | Inactive opportunities are correctly hidden from students |
| `count() == 2` | No unexpected extra results appear; the result set is exactly the two active listings |
