# Midterm Dev README

## Feature Summary

This branch adds a complete organization-side opportunity posting flow to the Opportunity App.

The new feature allows an authenticated organization user to:
- open the organization dashboard
- click `Post New Opportunity`
- fill out a dedicated form for a volunteer or internship role
- submit the opportunity with validation
- see a confirmation message
- view the newly created opportunity in the organization opportunities list

This work directly supports the user story for posting new volunteer or internship opportunities from the organization dashboard.

---

## Newly Written And Updated Code

### [pages/models.py](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/pages/models.py)

Updated the `Opportunity` model with new fields:
- `required_skills`
- `application_deadline`

What this code does:
- stores the skills or qualifications required for the role
- stores the deadline for applying
- supports saving the additional issue requirements in the database

---

### [pages/forms.py](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/pages/forms.py)

Added a new `OpportunityForm`.

What this code does:
- builds the Django form used on the new opportunity posting page
- exposes fields for title, category, type, description, required skills, location, duration, hours per week, and deadline
- adds user-friendly placeholders and date input widgets
- validates:
- required skills must be filled in
- deadline cannot be in the past
- hours per week must be greater than zero if entered

---

### [pages/views.py](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/pages/views.py)

Added the `organization_post_opportunity` view and connected it to the existing organization flow.

What this code does:
- restricts the page to logged-in organization users only
- displays the blank form on `GET`
- processes form submission on `POST`
- saves the new opportunity with `organization=request.user`
- shows success or error messages
- redirects the user to the organization opportunities page after a successful post

This file already contained the organization dashboard and opportunities list logic, so the new view fits into the existing organization feature set.

---

### [pages/urls.py](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/pages/urls.py)

Added a new route:
- `/org/opportunities/new/`

What this code does:
- gives the organization user a dedicated URL for creating new opportunities
- connects that URL to the new posting view in `pages/views.py`

---

### [templates/pages/organization_dashboard.html](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/templates/pages/organization_dashboard.html)

Updated the quick action button on the organization dashboard.

What this code does:
- changes the dashboard action from a generic opportunities page link to the real posting flow
- makes the acceptance criteria visible on the dashboard by giving the organization user a clear `Post New Opportunity` path

---

### [templates/pages/organization_post_opportunity.html](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/templates/pages/organization_post_opportunity.html)

New template added for the opportunity creation page.

What this code does:
- renders the new posting form UI
- provides a styled page for organizations to enter role information
- displays field-level validation errors
- includes navigation links back to the dashboard and posted opportunities
- supports desktop and mobile layout

This is the main new page for the feature.

---

### [templates/pages/organization_opportunities.html](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/templates/pages/organization_opportunities.html)

Reworked the organization opportunities listing page.

What this code does:
- shows posted opportunities in a cleaner management view
- displays the newly added fields such as required skills and application deadline
- shows role metadata like category, location, duration, hours per week, and application count
- gives the user a direct way to post another opportunity

This page is where the user sees the result after submitting the new form.

---

### [templates/accounts/login.html](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/templates/accounts/login.html)

Updated the login template to show non-field authentication errors.

What this code does:
- displays the real Django login error when authentication fails
- prevents the login page from appearing to “do nothing” after a failed attempt
- helps users understand whether the email/password is incorrect

This was added during debugging so the login behavior is easier to understand during testing.

---

### [pages/migrations/0003_opportunity_application_deadline_and_more.py](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/pages/migrations/0003_opportunity_application_deadline_and_more.py)

New Django migration file.

What this code does:
- updates the database schema for the new `Opportunity` fields
- keeps the database structure in sync with the updated model

---

### [pages/tests.py](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/pages/tests.py)

Added automated tests for the new posting feature.

What this code does:
- verifies organization users can access the post form
- verifies non-organization users are blocked from the route
- verifies a valid form submission creates a new opportunity
- verifies a past deadline is rejected

This helps confirm the new feature works correctly and protects against regressions.

---

### [opportunity_app/settings_test.py](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/opportunity_app/settings_test.py)

Added a local test settings file using SQLite.

What this code does:
- allows migrations and tests to run locally without depending on the remote PostgreSQL database
- gives a reliable development and verification environment

This was useful because the default app settings use a remote database that may not always be reachable during local testing.

---

### [Readme_Plan_Dev.md](/Users/devhirpara/Opportunity/opportunity_app_srping_2026/Readme_Plan_Dev.md)

Added the planning document for this task.

What this code does:
- records the implementation plan
- explains the design and testing approach used for the feature

---

## How The New Code Works Together

The flow of the new feature is:

1. An organization user logs in.
2. The organization dashboard loads from `organization_dashboard`.
3. The dashboard button sends the user to `/org/opportunities/new/`.
4. `organization_post_opportunity` loads `OpportunityForm`.
5. The form validates the input.
6. If valid, a new `Opportunity` is saved with the current organization as the owner.
7. A success message is shown.
8. The user is redirected to the organization opportunities page.
9. The new opportunity appears in the posted opportunities list.

This means the model, form, view, route, and templates all work together as one complete organization posting workflow.

---

## What Was Verified

The feature was verified in a local test setup using SQLite.

Verified behavior:
- the new page loads correctly
- organization login can reach the form page
- successful form submission creates an opportunity
- validation catches invalid deadlines
- the app boots successfully in the local development environment

---

## How To Run This Feature Locally

Use the local test settings:

```bash
cd /Users/devhirpara/Opportunity/opportunity_app_srping_2026
/Users/devhirpara/Opportunity/venv/bin/python manage.py migrate --settings=opportunity_app.settings_test
/Users/devhirpara/Opportunity/venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=opportunity_app.settings_test
```

Then open:

```text
http://127.0.0.1:8000/
```

To test the organization feature:
- create an organization account
- log in as that organization
- open the dashboard
- click `Post New Opportunity`

---

## Final Result

The new code adds a real, usable organization opportunity posting feature to the app. It moves the project from a placeholder organization opportunity page to a complete create-and-view workflow with validation, feedback, and automated test coverage.
