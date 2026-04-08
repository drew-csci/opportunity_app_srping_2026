# Opportunity App — Project Overview (by Nakiwe McDonald)

## Project description

Opportunity App is a Django-based web application for managing volunteer opportunities and student achievements. It supports three user roles (student, organization, administrator), custom email-based authentication, and a simple achievement posting feature for students.

This document explains the purpose of key files and how they interact at runtime.

## How the app runs (high level)

- `manage.py` is the CLI entrypoint used for running the development server, migrations, and other management commands. It sets `DJANGO_SETTINGS_MODULE` to `opportunity_app.settings`.
- `opportunity_app/settings.py` configures installed apps, database connections, templates, static files, and the custom user model via `AUTH_USER_MODEL = 'accounts.User'`.
- `opportunity_app/urls.py` is the root URL dispatcher. It mounts the `pages` and `accounts` apps and exposes the admin site.

When a request is received, Django uses the root URLconf to route it to the appropriate app's view. Views render templates that extend the global `base.html`, and models persist data to the database configured in `settings.py`.

## File-by-file description

Root files
- `manage.py`: Django management script; runs server and commands.
- `requirements.txt`: python dependencies (Django, psycopg2-binary, python-dotenv).
- `Readme.md`: project setup instructions and test account info (original README).
- `Readme_Nakiwe_McDonald.md` (this file): developer-focused overview and file interactions.
- `bootstrap.py`, `pack_dir_to_xml.py`, `test.py`, `output_20251011.xml`: utility / experimental scripts and outputs used by the repository authors (not required for core app runtime).

Project package: `opportunity_app/`
- `opportunity_app/settings.py`: central configuration — INSTALLED_APPS (`accounts`, `pages`), DB settings (Postgres via env), static/template dirs, `AUTH_USER_MODEL` and login redirect settings. This file drives app behavior and is imported by `manage.py` and the WSGI/ASGI entrypoints.
- `opportunity_app/urls.py`: root URL patterns. Routes:
  - `admin/` → Django admin
  - `''` → `pages.urls`
  - `accounts/` → `accounts.urls`
  - `logout/` → global logout view
- `opportunity_app/wsgi.py`, `opportunity_app/asgi.py`: server interfaces for deployment.

Accounts app: `accounts/`
- `accounts/models.py`: defines `User` which extends `AbstractUser`. Adds `user_type` (student, organization, administrator) and makes `email` the `USERNAME_FIELD`. Since `settings.AUTH_USER_MODEL` points here, all references to the user model (in forms, admin, and foreign keys) use this class.
- `accounts/forms.py`: `UserRegistrationForm` (wraps `UserCreationForm`) and `EmailAuthenticationForm` (adapts the standard `AuthenticationForm` to use an email label/placeholder). These forms are used by the accounts views and templates.
- `accounts/views.py`: `RegisterView` (creates user, logs them in, respects an optional `type` GET parameter to preselect `user_type`) and `CustomLoginView` (uses `EmailAuthenticationForm`, saves `selected_user_type` to session if provided). Views return templates under `templates/accounts/`.
- `accounts/urls.py`: maps `login/`, `register/`, `logout/` to the account views.
- `accounts/admin.py`: registers the custom `User` in Django admin, exposing `user_type` and making it manageable.

Pages app: `pages/`
- `pages/models.py`: defines `Achievement` with a ForeignKey to `settings.AUTH_USER_MODEL` limited to users where `user_type='student'`.
- `pages/forms.py`: `AchievementForm` (ModelForm for posting achievements).
- `pages/views.py`: contains the site views:
  - `welcome` (public landing page)
  - `screen1`, `screen2`, `screen3` (login-protected pages shown after login)
  - `student_achievements` (students can post and view their achievements; enforces `user.user_type == 'student'`)
  - `faq`, `dashboard` (other site pages)
- `pages/urls.py`: maps URL paths to the views above and is included by the root URLconf.

Templates and static
- `templates/base.html`: application shell used by all pages. It loads the static CSS (`static/css/styles.css`), renders navigation depending on `user.is_authenticated`, and includes a messages area.
- `templates/accounts/login.html` and `templates/accounts/register.html`: forms for authentication and registration, rendered by `accounts` views.
- `templates/pages/*.html`: page-specific templates (e.g., `student_achievements.html`, `screen1.html`, `dashboard.html`) that extend `base.html` and render context provided by the views.
- `static/css/styles.css`: styling served in development by Django's staticfiles and used by the base template.

Migrations
- `accounts/migrations/` and `pages/migrations/` contain schema migrations. These files define the database tables for `User` and `Achievement` and are applied with `python manage.py migrate`.

Key runtime interactions and dataflow
- Authentication flow: `accounts/views.CustomLoginView` uses `EmailAuthenticationForm` to authenticate users by email. After login, `LOGIN_REDIRECT_URL` in settings points users to `screen1`.
- User model propagation: `AUTH_USER_MODEL = 'accounts.User'` in `settings.py` means all references to the user model (forms, admin, foreign keys like `Achievement.student`) link to the custom `User` class.
- Page rendering: views gather data (e.g., `Achievement` queryset for the logged-in student) and pass it to templates which extend `base.html`. Template URL tags reference names defined in `pages/urls.py` and `accounts/urls.py`.
- Admin: `accounts.admin.UserAdmin` allows site administrators to manage users and their types; Django admin is mounted at `/admin/` in the root URLconf.

Development notes
- Environment variables: `settings.py` uses `python-dotenv` to load a `.env` file located at the project base. DB credentials and secret key can be configured there.
- To run locally (development):

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # optional for admin
python manage.py runserver
```

## Where I wrote this
This file: `Readme_Nakiwe_McDonald.md` (project root) — a developer-focused overview and file interaction map.

If you want, I can also generate:
- a visual diagram of the URL → view → template → model flow, or
- a shorter quick-reference listing of just templates and their contexts.

---
*Created by Nakiwe McDonald*.
