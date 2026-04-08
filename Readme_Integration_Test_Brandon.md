# Integration Test Documentation — Clear Button Visibility
### Brandon Jachera | Spring 2026

---

## Overview

**Test Class:** `ClearButtonVisibilityIntegrationTest`
**File:** `pages/tests.py`
**Command to run:** `python manage.py test pages.tests --verbosity=2`

**What it tests:**
The Clear button in the search bar should only appear on the Volunteer Opportunities page (`/screen1/`) when the user has an active keyword search or an active filter applied. When the page is loaded with no search parameters at all, the Clear button should be completely absent from the rendered HTML. This test verifies that conditional rendering logic in the template integrates correctly with the data passed down from the view.

---

## Unit Test vs. Integration Test — What Is the Difference?

Before diving into the code, it is important to understand why this is classified as an **integration test** rather than a unit test.

| | Unit Test | Integration Test |
|---|---|---|
| **Scope** | Tests one isolated piece of logic | Tests multiple components working together |
| **What it checks** | A function's return value or a model's behavior | How the request, view, database, and template all interact |
| **Example** | Does `Opportunity.objects.filter(is_active=True)` exclude inactive records? | Does the full rendered HTML page show the right button when a search query is in the URL? |

The Clear button test is an integration test because it exercises the entire request-response pipeline at once:

1. The test client sends an HTTP request with specific GET parameters
2. Django's URL router directs the request to the `screen1` view
3. The view reads the GET parameters and builds a context dictionary
4. The Django template engine renders `s1_student.html` using that context
5. The test inspects the final rendered HTML output

A failure at any one of those five steps — a wrong URL, a bug in the view, a missing context variable, or a broken template condition — would cause the test to fail. That is what makes it an integration test: it cannot pass unless all the components are working together correctly.

---

## How the Test Works — Step by Step

### The `setUp` Method

```python
def setUp(self):
    self.org_user = User.objects.create_user(
        username='testorg2@example.com',
        email='testorg2@example.com',
        password='testpass123',
        user_type='organization',
    )

    self.student_user = User.objects.create_user(
        username='teststudent2@example.com',
        email='teststudent2@example.com',
        password='testpass123',
        user_type='student',
    )

    Opportunity.objects.create(
        title='Health Clinic Volunteer',
        organization=self.org_user,
        ...
        is_active=True,
    )

    self.client = Client()
    self.client.login(email='teststudent2@example.com', password='testpass123')
```

`setUp` runs once before each test method and builds the minimum state needed for the tests to run.

**Organization user** — The `Opportunity` model has a required ForeignKey pointing to a user with `user_type='organization'`. Without this, creating an opportunity record would fail with a database constraint error.

**Student user** — The `screen1` view is protected with `@login_required`. If no user is logged in, every request gets redirected to the login page with a 302 status code, and `response.status_code` would equal 302 instead of 200, causing the first assertion in every test to fail before anything else is checked.

**One active opportunity** — A single opportunity is seeded so the page renders its full template including the results section. If the database were empty, the template would render the "no results" message branch instead, but the search form with the Clear button condition is always rendered regardless — this opportunity is here to ensure the page is in a realistic, non-empty state.

**Client login** — `self.client.login(...)` authenticates the student user so all subsequent requests in the test methods pass the `@login_required` check automatically.

---

### Test Method 1 — Clear Button Is Absent With No Query

```python
def test_clear_button_absent_with_no_query(self):
    response = self.client.get(reverse('screen1'))

    self.assertEqual(response.status_code, 200)
    self.assertNotContains(response, 'btn-clear')
```

**What happens:**

`self.client.get(reverse('screen1'))` sends a plain GET request to `/screen1/` with no query string. The URL looks exactly like a student just clicking the "Volunteer Opportunities" link in the navigation bar for the first time — no `?q=`, no `?location=`, nothing.

In the view, every GET parameter is read and stripped:
```python
query    = request.GET.get('q', '').strip()       # → ''
location = request.GET.get('location', '').strip() # → ''
cause    = request.GET.get('cause', '').strip()    # → ''
...
```

All values are empty strings. The view passes these into the template context under `query` and `filters`.

In the template, the Clear button is wrapped in this condition:
```html
{% if query or filters.location or filters.cause or filters.duration or filters.skills or filters.type %}
  <a href="{% url 'screen1' %}" class="btn btn-clear">Clear</a>
{% endif %}
```

Because every value is an empty string — which is falsy in Django's template language — the entire `{% if %}` block evaluates to false and the `<a>` tag is never written into the HTML output.

`self.assertNotContains(response, 'btn-clear')` scans the full rendered HTML of the response and confirms the string `btn-clear` does not appear anywhere in it. If the Clear button were accidentally rendered on an unfiltered page load, this assertion would fail.

---

### Test Method 2 — Clear Button Is Present With a Keyword Query

```python
def test_clear_button_present_with_keyword_query(self):
    response = self.client.get(reverse('screen1'), {'q': 'health'})

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'btn-clear')
```

**What happens:**

`self.client.get(reverse('screen1'), {'q': 'health'})` sends a GET request to `/screen1/?q=health`. The second argument is a dictionary that Django's test client automatically encodes as a URL query string.

In the view, `query` is now `'health'` — a non-empty string. When the template evaluates the `{% if query or ... %}` condition, `query` is truthy, so the condition passes and the Clear button `<a>` tag is written into the HTML.

`self.assertContains(response, 'btn-clear')` scans the full rendered HTML and confirms that `btn-clear` appears somewhere in it. This verifies the entire pipeline: the URL parameter was read by the view, the non-empty value was passed into the template context, and the template rendered the correct HTML branch.

---

### Test Method 3 — Clear Button Is Present With a Filter Only (No Keyword)

```python
def test_clear_button_present_with_filter_only(self):
    response = self.client.get(reverse('screen1'), {'location': 'Boston'})

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'btn-clear')
```

**What happens:**

This is the most important of the three methods. It proves that the Clear button is not exclusively tied to the keyword search bar — any active filter should also trigger it.

The request is sent as `/screen1/?location=Boston`. There is no `?q=` in the URL at all, so `query` is an empty string in the view. However, `location` is `'Boston'` — a non-empty string.

In the template, `{% if query or filters.location or ... %}` evaluates `query` first (empty string, falsy), then moves to `filters.location` (`'Boston'`, truthy) and the condition passes. The Clear button is rendered.

`self.assertContains(response, 'btn-clear')` confirms it is present.

Without this third test, a developer could introduce a bug where the Clear button only checks `query` and ignores all the filter fields — the first two tests would still pass, but this third test would fail and catch the regression.

---

## What `assertContains` and `assertNotContains` Do

These are built-in Django test assertion methods that are more powerful than a simple `assertIn`:

```python
self.assertContains(response, 'btn-clear')
# Equivalent to checking that 'btn-clear' is somewhere in response.content
# BUT also implicitly asserts response.status_code == 200
# Will show a clear failure message including the full response content if it fails

self.assertNotContains(response, 'btn-clear')
# Confirms 'btn-clear' does NOT appear anywhere in the rendered HTML
# Also implicitly asserts a successful response
```

They search the **fully rendered HTML** — not just the template source, and not just the context variables. This means the test only passes if the template engine actually wrote that string into the final page output that a browser would receive.

---

## The Full Integration Chain Being Tested

Every test method in this class exercises all of the following at once:

```
HTTP Request (GET parameters)
       ↓
Django URL Router (/screen1/ → screen1 view)
       ↓
screen1 view (reads GET params, builds context dict)
       ↓
Django Template Engine (renders screen1.html + s1_student.html partial)
       ↓
{% if %} condition in template (query or filters.*)
       ↓
Rendered HTML output (btn-clear present or absent)
       ↓
assertContains / assertNotContains (checks the final HTML)
```

If any single layer in this chain breaks — the URL mapping changes, the view stops passing `filters` to the context, the template condition is removed, or the CSS class name is renamed — at least one of these three tests will fail and immediately identify that something in the pipeline is broken.

---

## Test Output

When all 4 tests (unit + integration) are run together with `--verbosity=2`:

```
Found 4 test(s).
...
test_clear_button_absent_with_no_query
  (pages.tests.ClearButtonVisibilityIntegrationTest) ... ok
test_clear_button_present_with_filter_only
  (pages.tests.ClearButtonVisibilityIntegrationTest) ... ok
test_clear_button_present_with_keyword_query
  (pages.tests.ClearButtonVisibilityIntegrationTest) ... ok
test_no_query_returns_all_active_opportunities
  (pages.tests.Screen1NoQueryReturnsAllActiveOpportunitiesTest) ... ok

----------------------------------------------------------------------
Ran 4 tests in 1.478s

OK
```

---

## Summary

| Test Method | Request Sent | What Is Checked | Pass Condition |
|---|---|---|---|
| `test_clear_button_absent_with_no_query` | `GET /screen1/` | `btn-clear` is NOT in the HTML | No active search or filter → button hidden |
| `test_clear_button_present_with_keyword_query` | `GET /screen1/?q=health` | `btn-clear` IS in the HTML | Keyword search active → button visible |
| `test_clear_button_present_with_filter_only` | `GET /screen1/?location=Boston` | `btn-clear` IS in the HTML | Filter active (no keyword) → button still visible |
