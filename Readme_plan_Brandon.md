# Search & Filter Volunteer/Internship Opportunities
### User Story: Brandon Jachera | Spring 2026 | Story Points: 3

---

## User Story

> As a volunteer, I want to be able to search and filter volunteer and internship opportunities using keywords that apply the filters (such as location, cause, duration, skills) so that I can quickly find positions that would match my interests.

### Acceptance Criteria

- **Given** I am on the opportunities page
- **When** I enter a keyword in the search bar
- **Then** the system displays opportunities that match the keyword

---

## Current State

The app has no `Opportunity` model yet. Screen 1 (`/screen1/`) is labeled "Volunteer Opportunities" in the nav but currently renders role-based placeholder partials (`s1_student.html`, etc.) with no real data. There is no search or filter functionality anywhere in the codebase.

---

## Implementation Plan

### Phase 1 — Build the `Opportunity` Model (`pages/models.py`)

Add a new `Opportunity` model to represent volunteer and internship listings.

**Fields:**
| Field | Type | Notes |
|---|---|---|
| `title` | CharField (200) | Name of the opportunity |
| `organization` | ForeignKey → User | Must be `user_type = ORGANIZATION` |
| `description` | TextField | Full description of the role |
| `cause` | CharField (100) | e.g., Education, Environment, Health |
| `location` | CharField (200) | City, State or "Remote" |
| `duration` | CharField (100) | e.g., "3 months", "Ongoing" |
| `skills_required` | TextField | Comma-separated or plain text list |
| `opportunity_type` | CharField | Choices: `volunteer`, `internship` |
| `is_active` | BooleanField | Default `True`; controls visibility |
| `created_at` | DateTimeField | Auto-set on creation |

**Migration steps:**
1. Define the model in `pages/models.py`
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Register the model in `pages/admin.py` for easy data entry during development

---

### Phase 2 — Build the Search Input & Handling (`pages/views.py`)

Update the existing `screen1` view (the "Volunteer Opportunities" page) to support keyword search and field-based filtering via GET parameters.

**View logic:**
```python
def screen1(request):
    opportunities = Opportunity.objects.filter(is_active=True)

    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    cause = request.GET.get('cause', '').strip()
    duration = request.GET.get('duration', '').strip()
    skills = request.GET.get('skills', '').strip()
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
        'opportunities': opportunities,
        'query': query,
        'filters': {
            'location': location,
            'cause': cause,
            'duration': duration,
            'skills': skills,
            'type': opp_type,
        }
    }
    return render(request, 'pages/screen1.html', context)
```

**Notes:**
- Use `django.db.models.Q` for multi-field keyword matching
- All filters use `icontains` for case-insensitive partial matching
- Filters chain/stack — a user can combine a keyword search with a location filter simultaneously
- No URL changes needed; the existing `/screen1/` route handles GET parameters naturally

---

### Phase 3 — Update the Template (`templates/pages/screen1.html`)

Replace the placeholder role-based partial includes in `s1_student.html` with a real search UI and results list. The student view should show the search bar and results; organization/admin views can remain separate.

**Template structure for `templates/pages/partials/s1_student.html`:**

```html
<!-- Search Bar -->
<form method="get" action="{% url 'screen1' %}">
  <input type="text" name="q" value="{{ query }}" placeholder="Search opportunities...">
  <button type="submit">Search</button>
</form>

<!-- Filter Controls -->
<form method="get" action="{% url 'screen1' %}">
  <input type="hidden" name="q" value="{{ query }}">
  <input type="text" name="location" value="{{ filters.location }}" placeholder="Location">
  <input type="text" name="cause" value="{{ filters.cause }}" placeholder="Cause">
  <input type="text" name="duration" value="{{ filters.duration }}" placeholder="Duration">
  <input type="text" name="skills" value="{{ filters.skills }}" placeholder="Skills">
  <select name="type">
    <option value="">All Types</option>
    <option value="volunteer" {% if filters.type == 'volunteer' %}selected{% endif %}>Volunteer</option>
    <option value="internship" {% if filters.type == 'internship' %}selected{% endif %}>Internship</option>
  </select>
  <button type="submit">Apply Filters</button>
  <a href="{% url 'screen1' %}">Clear</a>
</form>

<!-- Results -->
{% if opportunities %}
  {% for opp in opportunities %}
    <div class="opportunity-card">
      <h3>{{ opp.title }}</h3>
      <p><strong>Type:</strong> {{ opp.get_opportunity_type_display }}</p>
      <p><strong>Cause:</strong> {{ opp.cause }}</p>
      <p><strong>Location:</strong> {{ opp.location }}</p>
      <p><strong>Duration:</strong> {{ opp.duration }}</p>
      <p><strong>Skills:</strong> {{ opp.skills_required }}</p>
      <p>{{ opp.description }}</p>
    </div>
  {% endfor %}
{% else %}
  <p>No opportunities found matching your search.</p>
{% endif %}
```

**Notes:**
- Two forms are used: one for the keyword search bar, one for the filter dropdowns/inputs. Both submit to the same URL. Alternatively, these can be merged into one `<form>` for a simpler UX.
- The "Clear" link resets all filters by navigating back to the base `/screen1/` URL.
- Persisting search state (re-populating fields with current query/filter values) is handled by passing `query` and `filters` through the view context.

---

## File Checklist

| File | Change |
|---|---|
| `pages/models.py` | Add `Opportunity` model |
| `pages/admin.py` | Register `Opportunity` in admin |
| `pages/views.py` | Update `screen1` view with search/filter logic |
| `templates/pages/partials/s1_student.html` | Replace placeholder with search UI + results |
| `pages/migrations/` | New migration file (auto-generated) |

---

## Out of Scope (for this story)

- Pagination of results
- Saving/bookmarking opportunities
- Organization ability to post/manage opportunities (separate story)
- Advanced filter UI (dropdowns populated from DB values)
- Relevance ranking / full-text search

---

## Risks & Notes

- The `Opportunity` model does not exist yet — seeding test data via Django admin or a fixture will be needed before the search can be manually tested.
- The `screen1` view currently uses a `user_type` branch to select partials. The context dict passed to the template needs to include `opportunities`, `query`, and `filters` regardless of user type so the student partial can access them.
- `Q` objects must be imported at the top of `views.py`: `from django.db.models import Q`
