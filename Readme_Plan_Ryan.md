## Plan: Issue #22 Auth Forms + Password Reset

Implement a complete, secure authentication UX by extending the existing login/registration system with password-reset flows, security hardening, and tests. The recommended approach is to reuse Django’s built-in auth reset/token machinery (to avoid custom crypto/token mistakes), wire it through project-specific forms/templates, and then verify both behavior and security controls.

**Steps**
1. Confirm and lock requirements for issue #22 scope in implementation notes: HTML-based login-related forms, credential validation, secure persistence of user input where appropriate (account creation/login sessions), and password reset support.
2. Phase 1 - Reuse Existing Auth Foundation (*start here*): review current custom user and auth flow in accounts app, then document integration points to avoid breaking existing email-based login. This anchors all later steps.
3. Phase 2 - Password Reset Request Flow (*depends on 2*): add reset-request form/view/route so a user can submit email and receive a reset link without user-enumeration leakage in responses.
4. Phase 3 - Password Reset Confirm Flow (*depends on 3*): add reset-confirm form/view/route that validates uid/token and updates password using Django validators; ensure invalid/expired token paths are handled safely.
5. Phase 4 - Templates and Navigation Wiring (*parallel with 6 after route names are set*): create/reset related HTML templates under the accounts templates area and add a visible forgot-password entry point in the existing login page.
6. Phase 5 - Email Delivery Configuration (*depends on 3*): define environment-backed email settings for dev/prod and set sender defaults so reset emails are deliverable and testable.
7. Phase 6 - Security Hardening (*parallel with 8 after core flow works*): apply session/cookie security settings suitable for production (secure + httponly + csrf secure under HTTPS), verify no plaintext credential logging, and document deployment constraints.
8. Phase 7 - Tests (*depends on 3, 4, 5*): add/extend auth tests for reset request, valid token reset, invalid/expired token behavior, and post-reset login outcomes.
9. Phase 8 - Content Consistency and QA (*depends on 4, 7*): align FAQ/help copy with actual functionality, then run end-to-end manual validation from login page to successful password reset.

**Relevant files**
- [accounts/models.py](accounts/models.py) - Reuse custom user model contract (email-based identity, user_type) to keep reset/login compatibility.
- [accounts/forms.py](accounts/forms.py) - Extend with reset-related forms while preserving existing registration/auth form patterns.
- [accounts/views.py](accounts/views.py) - Add reset request/confirm orchestration and messaging behavior.
- [accounts/urls.py](accounts/urls.py) - Register reset-related routes and named URL patterns.
- [templates/accounts/login.html](templates/accounts/login.html) - Add forgot-password link and user guidance.
- [templates/accounts](templates/accounts) - Add password reset HTML and email templates in this area.
- [opportunity_app/settings.py](opportunity_app/settings.py) - Add email backend/env configuration and security-related auth/session settings.
- [accounts/tests.py](accounts/tests.py) - Add automated tests for happy path + failure/security scenarios.
- [templates/pages/faq.html](templates/pages/faq.html) - Update wording so documented behavior matches implemented behavior.

**Verification**
1. Run auth test suite covering reset request/confirm/token edge cases and confirm all pass.
2. Manual flow test: from login page, request reset, open emailed link, set new password, login succeeds with new password and fails with old password.
3. Confirm reset request response is non-enumerating (same user-facing outcome for existing vs non-existing email).
4. Confirm CSRF is present on all relevant forms and reset token failures do not expose sensitive details.
5. Validate environment-driven email config in development and one production-like configuration check.
6. Validate secure-cookie/session settings in HTTPS context before release.

**Decisions**
- Use Django-native password reset token flow instead of custom token logic to reduce security risk and implementation complexity.
- Keep scope focused on issue #22 requirements (login-related forms + password reset + core security controls), excluding broader auth expansions (e.g., MFA) for this issue.
- Include FAQ/content alignment as part of done criteria because user-facing docs currently imply reset support.

**Further Considerations**
1. Rate-limiting/lockout on repeated failed login/reset attempts: recommended as a follow-up hardening task if not already tracked.
2. Optional email verification on registration: useful but outside primary issue #22 scope unless product owner adds it.
3. Decide reset token timeout policy explicitly for team docs if default is changed from framework defaults.
