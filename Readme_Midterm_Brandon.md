# Midterm Implementation — Search & Filter Volunteer/Internship Opportunities
### Brandon Jachera | Spring 2026

---

## Overview

This document describes the new code written to implement the volunteer/internship opportunity search and filter feature for the Opportunity App. The feature allows student users to search for opportunities by keyword and narrow results using filters such as location, cause, duration, skills, and opportunity type.

---

## Files Written / Modified

### 1. `pages/models.py` — Opportunity Model

**What was added:**

```python
class Opportunity(models.Model):
    class OpportunityType(models.TextChoices):
        VOLUNTEER = 'volunteer', 'Volunteer'
        INTERNSHIP = 'internship', 'Internship'

    title = models.CharField(max_length=200)
    organization = models.ForeignKey(...)
    description = models.TextField()
    cause = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    duration = models.CharField(max_length=100)
    skills_required = models.TextField(blank=True)
    opportunity_type = models.CharField(max_length=20, choices=OpportunityType.choices, ...)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**What it does:**

A new `Opportunity` database model was created to store volunteer and internship listings. Before this, the app had no data structure to hold opportunities — there was nothing to search or display.

- `title` — the name of the opportunity (e.g., "Food Bank Volunteer")
- `organization` — a foreign key linking the opportunity to the organization user that posted it. Only users with `user_type = 'organization'` can be assigned here
- `description` — a full text description of the role
- `cause` — the category or cause area (e.g., Education, Environment, Health)
- `location` — where the opportunity takes place (e.g., "Chicago, IL" or "Remote")
- `duration` — how long the commitment lasts (e.g., "3 months", "Ongoing")
- `skills_required` — a text field listing skills that are useful or required
- `opportunity_type` — either `volunteer` or `internship`, enforced with a `TextChoices` enum
- `is_active` — a boolean flag that controls whether an opportunity appears in search results. Inactive opportunities are hidden from students
- `created_at` — automatically records the date and time the opportunity was created

A migration file (`pages/migrations/0002_opportunity.py`) was also generated and applied to create the corresponding `pages_opportunity` table in the PostgreSQL database.

---

### 2. `pages/admin.py` — Admin Registration

**What was added:**

```python
from .models import Opportunity

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'opportunity_type', 'cause', 'location', 'duration', 'is_active', 'created_at')
    list_filter = ('opportunity_type', 'is_active', 'cause')
    search_fields = ('title', 'description', 'location', 'skills_required')
```

**What it does:**

Registers the `Opportunity` model with the Django admin interface so that administrators can create, edit, and delete opportunity listings through the `/admin/` panel without needing to write code or use the database directly.

- `list_display` — controls which columns are shown in the admin list view, giving a quick overview of each opportunity
- `list_filter` — adds a sidebar in the admin panel to filter by type, active status, or cause
- `search_fields` — enables a search bar inside the admin panel that searches across title, description, location, and skills

This is the primary way to seed test data into the application during development.

---

### 3. `pages/views.py` — Updated `screen1` View

**What was added:**

```python
from django.db.models import Q
from .models import Achievement, Opportunity

@login_required
def screen1(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'

    opportunities = Opportunity.objects.filter(is_active=True)

    query    = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    cause    = request.GET.get('cause', '').strip()
    duration = request.GET.get('duration', '').strip()
    skills   = request.GET.get('skills', '').strip()
    opp_type = request.GET.get('type', '').strip()

    if query:
        opportunities = opportunities.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(cause__icontains=query) |
            Q(location__icontains=query) |
            Q(skills_required__icontains=query)
        )
    if location:
        opportunities = opportunities.filter(location__icontains=location)
    if cause:
        opportunities = opportunities.filter(cause__icontains=cause)
    if duration:
        opportunities = opportunities.filter(duration__icontains=duration)
    if skills:
        opportunities = opportunities.filter(skills_required__icontains=skills)
    if opp_type:
        opportunities = opportunities.filter(opportunity_type=opp_type)

    context = {
        'role': role,
        'opportunities': opportunities,
        'query': query,
        'filters': { 'location': location, 'cause': cause, 'duration': duration, 'skills': skills, 'type': opp_type },
    }
    return render(request, 'pages/screen1.html', context)
```

**What it does:**

The `screen1` view (the "Volunteer Opportunities" page at `/screen1/`) was updated to handle search and filter logic. Previously it only passed the user's role to the template and rendered placeholder content.

- **Baseline query** — The view starts by fetching all active opportunities (`is_active=True`). Only visible listings are ever returned to the user
- **Keyword search (`q`)** — When the user types in the search bar, the view uses Django's `Q` objects to search across five fields at once: `title`, `description`, `cause`, `location`, and `skills_required`. `Q` objects allow OR logic — a match in any one of these fields returns the opportunity. `icontains` makes the search case-insensitive
- **Individual filters** — Each filter (`location`, `cause`, `duration`, `skills`, `type`) is read from the GET request and applied as an additional AND condition on top of whatever the keyword search already narrowed down. Filters chain together so a user can combine any number of them simultaneously
- **Context** — The matched opportunities, the current search query string, and all active filter values are passed to the template so the UI can display results and re-populate the form fields without resetting

---

### 4. `templates/pages/partials/s1_student.html` — Search UI & Results Template

**What was added:**

A full replacement of the previous placeholder content (a simple welcome message and link) with a functional search interface and results display.

**Search bar form:**
```html
<form class="search-form" method="get" action="{% url 'screen1' %}">
  <!-- hidden inputs preserve active filters when submitting a new keyword search -->
  <input type="text" name="q" value="{{ query }}" placeholder="Search by keyword, cause, location, or skill...">
  <button type="submit" class="btn">Search</button>
  <a href="{% url 'screen1' %}" class="btn btn-clear">Clear</a>  <!-- only shown when filters are active -->
</form>
```

**Filter form:**
```html
<form class="filter-form" method="get" action="{% url 'screen1' %}">
  <input type="hidden" name="q" value="{{ query }}">  <!-- preserves keyword when applying filters -->
  <input type="text" name="location" ...>
  <input type="text" name="cause" ...>
  <input type="text" name="duration" ...>
  <input type="text" name="skills" ...>
  <select name="type">...</select>
  <button type="submit" class="btn">Apply Filters</button>
</form>
```

**Results loop:**
```html
{% for opp in opportunities %}
  <div class="opportunity-card">
    <h3>{{ opp.title }}</h3>
    <span class="opp-badge">{{ opp.get_opportunity_type_display }}</span>
    <!-- cause, location, duration, skills, description, posted by -->
  </div>
{% endfor %}
```

**What it does:**

- The **search bar** submits to `/screen1/` using a GET request. Using GET (not POST) means the search query appears in the URL, making results shareable and bookmark-able
- Hidden inputs in each form carry over the other form's values so that using the search bar doesn't wipe out applied filters and vice versa
- The **"Clear" button** only appears when at least one filter or keyword is active, giving the user a one-click reset back to all results
- Each opportunity renders as a **card** showing its title, a color-coded volunteer/internship badge, cause, location, duration, skills, full description, and the name of the posting organization
- If no results match, a friendly message is shown instead of an empty page — with context-aware text that changes depending on whether a search/filter is active or the database simply has no listings yet
- Filter fields **re-populate** with their current values after submission so the user can see what filters are applied and adjust them without starting over

---

### 5. `static/css/styles.css` — Styles for Search UI and Cards

**What was added:**

```css
/* Search & Filter */
.search-section { ... }
.search-form { display:flex; gap:.5rem; align-items:center; flex-wrap:wrap; ... }
.filter-form { display:flex; gap:.5rem; align-items:center; flex-wrap:wrap; }
.btn-clear { background:#6b7280; }

/* Opportunity Cards */
.opportunity-card { background:#fff; border:1px solid #e5e7eb; border-radius:.75rem; padding:1.25rem; }
.opp-badge--volunteer  { background:#dcfce7; color:#166534; }
.opp-badge--internship { background:#dbeafe; color:#1e40af; }
.opp-meta { display:flex; gap:1.25rem; flex-wrap:wrap; font-size:.875rem; color:#475569; }
```

**What it does:**

New CSS rules were appended to the existing stylesheet to style the search interface and opportunity cards:

- `.search-form` and `.filter-form` use flexbox with `flex-wrap` so the inputs and buttons stack gracefully on smaller screens
- `.btn-clear` styles the "Clear" button in a neutral grey to visually distinguish it from the primary action buttons
- `.opportunity-card` gives each result a white rounded card with a subtle border, consistent with the existing `.dash-card` style used elsewhere in the app
- `.opp-badge--volunteer` renders as a green pill badge and `.opp-badge--internship` as a blue pill badge, giving users an immediate visual cue about the type of listing
- `.opp-meta` arranges the cause, location, and duration fields in a horizontal row that wraps on narrow viewports

---

## Migration

A new database migration was generated and applied:

- **File:** `pages/migrations/0002_opportunity.py`
- **Operation:** `CreateModel` — creates the `pages_opportunity` table in PostgreSQL with all defined fields
- **Applied with:** `python manage.py migrate`

---

## How to Test

1. Log in as an admin and go to `/admin/`
2. Under **Pages > Opportunities**, create several test opportunities with different causes, locations, types, and skills
3. Log in as a student and navigate to `/screen1/` (Volunteer Opportunities)
4. Type a keyword in the search bar and click **Search** — only matching opportunities appear
5. Use the filter row to narrow results further by location, cause, duration, skills, or type
6. Click **Clear** to reset back to all results
