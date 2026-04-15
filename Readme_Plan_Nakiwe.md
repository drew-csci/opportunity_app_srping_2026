# Volunteer Application Tracking Plan

## Overview
This plan adds volunteer application submission and tracking features so student volunteers can apply for an opportunity, save drafts, avoid duplicate applications, and track status changes (accepted, denied, or under review).

## Goals
- Allow volunteer students to fill out and submit applications for opportunities.
- Prevent duplicate applications to the same opportunity.
- Provide a clear success message when an application is submitted.
- Display application status on a student tracking page.
- Update application status when the organization accepts or denies.
- Enable students to save draft applications and resume later.

## Implementation Steps
1. Add data models in `pages/models.py`:
   - `Opportunity` with title, description, organization foreign key, posted date, and active flag.
   - `Application` with student foreign key, opportunity foreign key, motivation/statement fields, status choices (`draft`, `pending`, `accepted`, `denied`), submit timestamp, and save timestamp.
   - Enforce unique student/opportunity application constraint with `UniqueConstraint`.
2. Update admin registration in `pages/admin.py`:
   - Register `Opportunity` and `Application` models for backend management.
3. Create application forms in `pages/forms.py`:
   - `ApplicationForm` with fields for motivation and optional resume text.
   - Support draft save and final submit actions.
4. Implement views in `pages/views.py`:
   - `opportunity_list` to show all available opportunities.
   - `opportunity_detail` to show opportunity details and the student's existing application state.
   - `apply_to_opportunity` to create or resume a draft and submit the application.
   - `my_applications` to list all student applications and show placeholder text when none exist.
   - `application_detail` for the student to view their application tracking record.
5. Add organization review views in `pages/views.py`:
   - `organization_applications` to list applications for opportunities owned by that organization.
   - `review_application` to update application status to accepted or denied.
   - Enforce role restrictions so only organization users access review pages.
6. Add URLs in `pages/urls.py` for all new routes:
   - opportunity list, opportunity detail, apply, my applications, application detail, organization application review.
7. Create templates under `templates/pages/`:
   - `opportunity_list.html`
   - `opportunity_detail.html`
   - `application_form.html`
   - `my_applications.html`
   - `application_detail.html`
   - `organization_applications.html`
8. Update navigation/UI:
   - Add a `My Applications` link to the authenticated navbar in `templates/base.html` for students.
   - Add student dashboard links in `templates/pages/partials/s1_student.html` for browsing opportunities and tracking applications.
9. Add validation and messages:
   - Prevent duplicate applications in both view/form logic and via database constraint.
   - Show success messages on submission and save messages on draft saves.
10. Verify role access and user flow:
   - Redirect non-students away from student-specific pages.
   - Redirect non-organizations away from organization review pages.

## Verification Checklist
- Student logs in and opens `My Applications`.
- If there are no applications, the page shows "No current applications."
- Student can navigate to an opportunity, save a draft, resume later, and submit.
- Only one application can exist per student per opportunity.
- Submission shows a confirmation message.
- Student tracking page displays status: pending, accepted, denied, or draft.
- Organization can update status through the app and student tracking updates accordingly.
- Role-based access is enforced.

## Notes
- This plan uses the existing `pages` app to keep opportunity/application logic with current student pages.
- Draft save support is implemented through a `draft` application status.
- Organization decision workflow is supported through a UI rather than relying solely on Django admin.
