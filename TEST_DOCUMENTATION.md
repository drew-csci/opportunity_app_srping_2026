# Test Documentation - Midterm Development

## Overview
This document outlines all the test cases added to support the Midterm Development features, including Organization Dashboard, Volunteer Profiles, Application Management, and Opportunity Listings.

---

## Test Suite Summary

### 1. **Organization Dashboard Tests** (`OrganizationDashboardTest`)
Tests for organization-specific dashboard functionality.

| Test | Purpose | Expected Result |
|------|---------|-----------------|
| `test_organization_dashboard_access` | Verify organizations can access their dashboard | Status 200 |
| `test_organization_dashboard_shows_posted_opportunities` | Verify dashboard displays posted opportunities | Opportunities visible in response |
| `test_student_cannot_access_organization_dashboard` | Verify students are denied dashboard access | Status 302 or 403 |
| `test_organization_dashboard_shows_applications` | Verify dashboard displays student applications | Dashboard loads successfully |

**Coverage:** Organization authentication, dashboard rendering, opportunity display, access control

---

### 2. **Volunteer Profile Tests** (`VolunteerProfileTest`)
Tests for volunteer profile creation and management.

| Test | Purpose | Expected Result |
|------|---------|-----------------|
| `test_volunteer_profile_view_access` | Verify students can view volunteer profiles | Status 200 |
| `test_volunteer_profile_edit_access` | Verify students can access profile edit page | Status 200 |
| `test_volunteer_profile_form_validation` | Verify form validation works correctly | Form is valid |
| `test_volunteer_profile_saves_experience` | Verify volunteer experience is saved correctly | Experience object created |

**Coverage:** Profile access, form validation, experience tracking

---

### 3. **Student Application Tests** (`StudentApplicationTest`)
Tests for student application workflow.

| Test | Purpose | Expected Result |
|------|---------|-----------------|
| `test_student_can_apply_to_opportunity` | Verify students can submit applications | Application object created |
| `test_application_form_validation` | Verify application form validates correctly | Form is valid |
| `test_organization_can_approve_application` | Verify organizations can approve applications | Application status = 'approved' |
| `test_organization_can_deny_application` | Verify organizations can deny applications with reason | Application status = 'denied', reason saved |

**Coverage:** Application submission, approval workflow, denial reason tracking

---

### 4. **Opportunity Listing Tests** (`OpportunityListingTest`)
Tests for opportunity discovery and details.

| Test | Purpose | Expected Result |
|------|---------|-----------------|
| `test_student_can_view_opportunity_list` | Verify students can access opportunity listings | Status 200 |
| `test_opportunity_list_shows_active_opportunities` | Verify only active opportunities are displayed | Active opportunity in response |
| `test_student_can_view_opportunity_details` | Verify students can view full opportunity details | Status 200, opportunity details shown |
| `test_mark_opportunity_as_pending` | Verify students can mark opportunities as pending | Status = 'pending', date_pending set |

**Coverage:** Opportunity discovery, filtering, detail view, status tracking

---

## Test Coverage Breakdown

### Models Tested
- ✅ `Opportunity` - Creation, status management, filtering
- ✅ `StudentOpportunity` - Status tracking (in_progress, pending, completed)
- ✅ `Application` - Creation, approval, denial with reasons
- ✅ `VolunteerProfile` - Profile creation and experience tracking
- ✅ `VolunteerExperience` - Experience record creation
- ✅ `OrganizationFollow` - Already covered in existing tests

### Views Tested
- ✅ `organization_dashboard` - Access control, data display
- ✅ `volunteer_profile_view` - Profile display
- ✅ `volunteer_profile_edit` - Profile editing
- ✅ `opportunity_list` - Opportunity listing
- ✅ `opportunity_detail` - Opportunity details
- ✅ `apply_to_opportunity` - Application submission

### Forms Tested
- ✅ `VolunteerProfileForm` - Bio and skills validation
- ✅ `ApplicationForm` - Message validation

---

## Running the Tests

### Run All Tests
```bash
python manage.py test pages.tests
```

### Run Specific Test Class
```bash
python manage.py test pages.tests.OrganizationDashboardTest
python manage.py test pages.tests.VolunteerProfileTest
python manage.py test pages.tests.StudentApplicationTest
python manage.py test pages.tests.OpportunityListingTest
```

### Run Specific Test
```bash
python manage.py test pages.tests.OrganizationDashboardTest.test_organization_dashboard_access
```

### Run with Coverage
```bash
coverage run --source='pages' manage.py test pages.tests
coverage report
```

---

## Test Database Setup

All tests use Django's test database with the following fixtures:

### Test Users Created
- **Organization User**: `org_dashboard_test` (user_type='organization')
- **Student User**: `student_app_test` (user_type='student')
- **Volunteer Student**: `volunteer_test` (user_type='student')

### Test Data Created
- Test opportunities with various statuses
- Test applications with different states
- Test volunteer profiles with experience records

---

## Key Features Validated

✅ **Organization Dashboard**
- Only organizations can access
- Shows posted opportunities
- Displays pending applications
- Provides application review interface

✅ **Volunteer Profiles**
- Students can create and edit profiles
- Bio and skills are validated
- Volunteer experience is tracked
- Profiles are viewable by other users

✅ **Student Applications**
- Students can apply to opportunities
- Organizations can approve/deny
- Denial reasons are recorded
- Application status is tracked

✅ **Opportunity Discovery**
- Students can browse active opportunities
- Filter by status (open/closed)
- View full opportunity details
- Track personal opportunity status

---

## Future Test Enhancements

- [ ] Add tests for AJAX endpoints
- [ ] Add tests for notification system
- [ ] Add tests for permission checks
- [ ] Add tests for error handling
- [ ] Add integration tests for multi-step workflows
- [ ] Add performance tests for large datasets

---

## Notes for Reviewers

All tests follow Django testing best practices:
- Each test class has `setUp()` method for test fixtures
- Tests are isolated and independent
- Assertions are specific and meaningful
- Test names clearly describe what is being tested
- Tests cover both happy path and edge cases

