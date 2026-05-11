# Development Plan: Post New Volunteer or Internship Opportunities

## Goal
Implement issue `#2` so an authenticated organization user can create and publish a new opportunity from the organization dashboard by entering the role description, required skills, location, duration, and application deadline, then immediately see the new listing reflected in the organization opportunities view.

## Current Codebase Findings
- The project already has an `Opportunity` model in `pages/models.py`, but it is missing some fields required by the story, especially `required_skills` and `application_deadline`.
- The organization dashboard already exists in `templates/pages/organization_dashboard.html` and includes a "Post Opportunity" action that currently routes to the organization opportunities page instead of a real creation flow.
- The organization opportunities page exists in `templates/pages/organization_opportunities.html`, but it currently behaves like a listing page and does not include a working creation form.
- `pages/forms.py` only contains `AchievementForm`, so opportunity creation will need a new Django form.
- `pages/urls.py` and `pages/views.py` already contain organization-specific routes and views, which gives us a clean place to add the new feature.

## Implementation Plan

### Phase 1: Extend the data model
- Review the existing `Opportunity` schema and add the missing fields needed by the issue.
- Add fields for `required_skills` and `application_deadline`.
- Decide whether the existing `category`, `opportunity_type`, `duration`, and `hours_per_week` fields already cover the rest of the story or need small validation improvements.
- Create and run a Django migration so the database supports the new opportunity details.

### Phase 2: Build the creation form
- Add an `OpportunityForm` in `pages/forms.py` using Django `ModelForm`.
- Include user-facing form inputs for `title`, `description`, `required_skills`, `location`, `opportunity_type`, `duration`, `hours_per_week`, and `application_deadline`.
- Add widget choices for better usability, especially a date input for the deadline and helpful placeholders for longer text fields.
- Add server-side validation to prevent invalid submissions such as past deadlines or negative hours.

### Phase 3: Add the create view and route
- Create a dedicated organization-only view in `pages/views.py` for posting a new opportunity.
- Enforce access so only logged-in users with `user_type == 'organization'` can access the page and submit the form.
- On `GET`, render the empty form.
- On `POST`, validate and save the opportunity with `organization=request.user`.
- After a successful submission, redirect to the organization opportunities page or back to the form with a success message.

### Phase 4: Connect the dashboard flow
- Update the quick action in `templates/pages/organization_dashboard.html` so "Post Opportunity" points to the new creation route.
- Keep the dashboard behavior aligned with the acceptance criteria: the posting option must be clearly visible from the organization dashboard.
- If helpful, add a small supporting line of text or callout so the action is more obvious to the organization user.

### Phase 5: Update the organization opportunities experience
- Decide whether to keep a separate dedicated create page with the opportunities page as the listing screen, or embed the form into the existing opportunities page while preserving the list below it.
- Show the newly created opportunity in the organization listing after submission.
- Display the newly added fields, especially required skills and application deadline, so the listing reflects the full role details.
- Preserve existing management actions where possible, even if some are still placeholders.

### Phase 6: Add confirmation and feedback
- Add a success message after posting so the organization user knows the opportunity was published.
- Make sure validation errors appear clearly if required information is missing or invalid.
- If time permits, include an empty-state improvement that points users directly to the new posting form.

## Files Likely To Change
- `pages/models.py`
- `pages/forms.py`
- `pages/views.py`
- `pages/urls.py`
- `templates/pages/organization_dashboard.html`
- `templates/pages/organization_opportunities.html`
- Possibly a new template such as `templates/pages/organization_post_opportunity.html`
- A new migration file under `pages/migrations/`

## Testing Plan
- Verify an organization user can see the posting option from `/org/dashboard/`.
- Verify a non-organization user is blocked or redirected from the create route.
- Verify valid form submission creates a new `Opportunity` tied to the logged-in organization.
- Verify the new opportunity appears in the organization opportunities list immediately after submission.
- Verify required validation messages appear for missing fields.
- Verify deadline validation rejects past dates if that rule is implemented.
- Verify the layout remains usable on desktop and mobile widths.

## Risks And Notes
- The current `Opportunity` model already supports some opportunity metadata, so changes should reuse existing fields rather than duplicate them.
- If the team wants `required_skills` to support structured tags instead of plain text, that would expand scope beyond this issue.
- There is currently no existing messaging framework visible in the inspected files, so success feedback may require adding Django messages or rendering inline confirmation text.

## Definition Of Done
- Organization users can navigate from the dashboard to a working "Post New Opportunity" flow.
- They can enter all required details and submit successfully.
- The opportunity is stored in the database with the logged-in organization as owner.
- A confirmation is shown after submission.
- The new opportunity appears in the organization opportunities list with its key details.
