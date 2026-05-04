# Test Submission Document

## Branch Name

`dev_testing`

## Explanation of Tests

### Code Coverage Analysis Tests

These tests verify that the project is configured to measure backend code coverage correctly.

- `test_coverage_dependency_is_pinned`: Checks that the `coverage` package is included in `requirements.txt`, so other developers can install and run coverage analysis.
- `test_coverage_config_measures_project_apps`: Checks that `.coveragerc` measures the main Django apps: `pages`, `accounts`, and `opportunity_app`. It also verifies that the project keeps the required 70% minimum coverage threshold.

### Negative Testing & Input Validation Tests

These tests check that the application rejects invalid input and blocks unauthorized actions.

- `test_rejects_zero_hours_per_week`: Confirms that an organization cannot create an opportunity with `0` hours per week.
- `test_rejects_missing_required_skills`: Confirms that an opportunity cannot be created without required skills.
- `test_rejects_unauthorized_application_acceptance`: Confirms that one organization cannot accept an application for an opportunity posted by another organization.

### Regression Testing Tests

These tests protect behavior that should continue working after future changes.

- `test_organization_dashboard_access`: Confirms that an organization user can access the organization dashboard.
- `test_organization_dashboard_counts_applications_and_opportunities`: Confirms that the dashboard correctly counts pending applications, accepted applications, and active opportunities.
- `test_student_cannot_access_organization_dashboard`: Confirms that student users are redirected away from the organization dashboard.
- `test_achievement_is_saved_for_logged_in_student`: Confirms that a logged-in student can create an achievement.
- `test_student_achievement_list_renders_existing_achievement`: Confirms that saved achievements appear on the student achievements page.
- `test_organization_is_redirected_from_student_achievements`: Confirms that organization users cannot access the student-only achievements page.

### Integration Testing Tests

These tests verify that multiple parts of the system work together correctly.

- `test_organization_posts_opportunity_and_sees_it_in_management_page`: Tests the full workflow where an organization posts a new opportunity and then sees it on the organization opportunities page.
- `test_ajax_accept_and_decline_update_application_statuses`: Tests the AJAX workflow for accepting and declining student applications.
- `test_applicant_profile_shows_student_history_for_posting_organization`: Confirms that an organization can view a student applicant profile with related applications and achievements.
- `test_non_ajax_decline_redirects_to_applicant_profile`: Confirms that declining an application through a normal request updates the application status and redirects back to the applicant profile.

### Performance & Load Testing Tests

These tests check that the application still behaves efficiently when more data is present.

- `test_organization_dashboard_query_count_stays_bounded_with_many_applications`: Creates many applications and confirms that the organization dashboard still loads using a limited number of database queries.

### Smoke Testing Tests

These tests confirm that important pages load successfully and do not crash.

- `test_public_pages_render`: Confirms that public pages such as the welcome page, FAQ page, login page, and register page return successful responses.
- `test_login_required_pages_redirect_anonymous_users`: Confirms that protected pages redirect anonymous users instead of allowing access.
- `test_role_screen_pages_render_for_organization_user`: Confirms that the role-based screen pages render correctly for an organization user.
- `test_organization_pages_render_for_organization_user`: Confirms that key organization pages, including dashboard, profile, messages, opportunities, and post opportunity pages, render successfully.

### Existing Opportunity Posting Tests

These tests cover the opportunity posting workflow for organizations.

- `test_organization_can_view_post_form`: Confirms that an organization can open the opportunity posting form.
- `test_non_organization_user_is_redirected_from_post_form`: Confirms that a student cannot access the organization-only posting form.
- `test_valid_submission_creates_opportunity_for_organization`: Confirms that a valid opportunity submission creates a new opportunity assigned to the logged-in organization.
- `test_past_deadline_is_rejected`: Confirms that opportunities cannot be posted with an application deadline in the past.
- `test_organization_dashboard_contains_post_new_opportunity_link`: Confirms that the organization dashboard includes a link to post a new opportunity.
- `test_successful_submission_shows_success_message_after_redirect`: Confirms that a successful opportunity post shows a success message.
- `test_invalid_submission_shows_error_message_and_does_not_redirect`: Confirms that invalid opportunity form submissions stay on the form page and show an error message.

### Authentication Tests

These tests cover login, registration, password reset, and authentication UI behavior.

- `test_failed_login_shows_authentication_error_on_login_page`: Confirms that invalid login credentials show an error message.
- `test_login_with_email_succeeds`: Confirms that a user can log in using an email address.
- `test_password_reset_request_sends_email_for_existing_user`: Confirms that a password reset email is sent for a registered user.
- `test_password_reset_request_is_non_enumerating_for_unknown_email`: Confirms that unknown emails do not reveal whether an account exists.
- `test_password_reset_confirm_with_valid_token_updates_password`: Confirms that a valid password reset token lets the user set a new password.
- `test_password_reset_confirm_with_invalid_token_shows_error`: Confirms that invalid reset tokens show an error.
- `test_custom_set_password_form_requires_matching_passwords`: Confirms that mismatched password reset fields are rejected.
- `test_complete_password_reset_flow_returns_to_login`: Tests the full password reset flow from request through successful login.
- `test_login_template_contains_new_ui_sections`: Confirms that the login template includes the expected UI sections.
- `test_login_with_type_renders_role_heading_and_register_link_query`: Confirms that the login page reflects the selected user type.
- `test_register_template_contains_new_ui_sections`: Confirms that the register template includes the expected UI sections.
- `test_register_prefills_user_type_from_query_param`: Confirms that the register form can prefill the user type from the URL query parameter.
- `test_register_prefills_user_type_from_session_set_by_login`: Confirms that the register form can prefill the user type from the session.
- `test_register_creates_user_logs_in_and_redirects`: Confirms that registration creates a user, logs them in, and redirects them.
- `test_login_success_redirects_to_screen1`: Confirms that successful login redirects to the first role screen.
- `test_auth_css_selectors_exist`: Confirms that the CSS selectors needed by the authentication UI exist.
