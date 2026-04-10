# Readme_Midterm_Nakiwe

## Overview
This update adds application tracking functionality for students and organizations in the Django project. It includes new models, forms, views, URLs, and templates to support student application submission, organization review, and status tracking.

## Newly written code (application tracking)
- `pages/models.py`
  - Added `OpportunityApplication` model (e.g., `student`, `opportunity`, `status`, `submitted_at`, `reviewed_at`, `reviewer`, etc.).
- `pages/forms.py`
  - Added `OpportunityApplicationForm` to capture student application entries. 
- `pages/views.py`
  - Added student flow views: `application_form`, `submit_application`, `my_applications`.
  - Added organization flow views: `organization_applications`, `review_application`.
- `pages/urls.py`
  - Added new routing for the views:
    - `/applications/new/`
    - `/applications/mine/`
    - `/applications/organization/`
    - `/applications/<int:pk>/review/`
- `templates/pages/application_form.html` and related page templates
  - Student application UI for submitting applications.
- `templates/pages/my_applications.html`
  - Student status tracking page.
- `templates/pages/organization_applications.html`
  - Organization dashboard showing received applications.
- `templates/pages/review_application.html`
  - Review form for approve/reject with comments.
- `templates/pages/partials/s1_*.html`, `s2_*.html`, `s3_*.html` (if role partials were used)
  - Role-based display segments for students/org/admin at various workflow steps (S1/S2/S3).

## What the new code does
- Adds persistence for opportunity applications via `OpportunityApplication` model.
- Validates and saves student-submitted applications through `OpportunityApplicationForm`.
- Provides an application submission route and view that creates model entries.
- Lists a students applications and current statuses on `my_applications`.
- Shows organization-specific incoming applications and filters by owner in `organization_applications`.
- Enables organization review and status updates (approve/reject/pending) in `review_application`.
- Template pages render forms, lists, and status UI so users can navigate the tracking workflow.

## Usage summary
1. Student logs in and submits application via `application_form`.
2. Data is saved in `OpportunityApplication`.
3. Student checks status on `my_applications`.
4. Org user checks `organization_applications`.
5. Org reviewer updates status in `review_application`.
6. Student sees updated status.
