# Opportunity App (Spring 2026)

## Project Description

This repository is a **Django web application** built for managing and displaying opportunity-related content (such as dashboards, student achievements, and role-based screens). It includes user authentication, role-aware page rendering, and a modular app structure.

---

## Key Files and Folders

### 📁 Root-level files
- **`manage.py`**
  - Django’s command-line utility used to start the development server, apply migrations, run tests, and execute other project management tasks.

- **`requirements.txt`**
  - Lists the Python dependencies required to run the project (Django and any additional packages).

- **`Readme.md`**
  - Main project documentation (setup, usage, features). This file is separate from this custom `Readme_puzi_wei.md`.

- **`bootstrap.py`**, **`test.py`**, **`pack_dir_to_xml.py`**, **`output_20251011.xml`**
  - Utility or experimental scripts that are outside the standard Django app framework. They are likely used for development tasks, tests, or exporting project data.

---

### 📁 `opportunity_app/` (Django project config)
This is the Django **project module** that configures settings, URLs, and deployment entry points.

- **`settings.py`**
  - Global configuration: installed apps, middleware, database connections, templates, static file setup, authentication, etc.

- **`urls.py`**
  - Root URL dispatcher. Maps incoming HTTP requests to app-level URL configurations or view handlers.

- **`wsgi.py`** / **`asgi.py`**
  - Deployment entry points for WSGI/ASGI-compatible web servers.

- **`__init__.py`**
  - Marks the folder as a Python package so it can be imported.

---

### 📦 `accounts/` (User authentication & profiles)
Handles login, registration, user profiles, and related functionality.

- **`models.py`**
  - Defines user-related data models (custom user profiles, extended fields, etc.).

- **`forms.py`**
  - Contains Django forms for login, registration, and other account-related actions.

- **`views.py`**
  - Implements view logic for authentication pages and account actions.

- **`urls.py`**
  - Routes user-facing URLs (e.g., `/login/`, `/register/`) to views.

- **`admin.py`**
  - Registers models with Django admin for site management.

- **`tests.py`**
  - Unit tests for account-related behavior.

- **`migrations/`**
  - Tracks database schema changes for account models.

---

### 📦 `pages/` (Main site pages)
Responsible for rendering the key public and authenticated pages of the application (dashboard, FAQ, screens, etc.).

- **`models.py`**
  - Defines data structures used by the UI (e.g., achievements, screen configurations).

- **`views.py`**
  - Handles requests and renders templates for pages like the dashboard and role-specific screens.

- **`urls.py`**
  - Maps page endpoints to view functions.

- **`admin.py`**
  - Registers page-related models for Django admin.

- **`tests.py`**
  - Contains unit tests for page rendering and logic.

- **`migrations/`**
  - Tracks database schema changes for page models.

---

### 🧩 Templates (HTML rendering)
Templates are stored in `templates/` and used by views to generate HTML pages.

- **`base.html`**
  - The base layout template, defining shared page structure (header, footer, blocks for content).

- **`templates/accounts/`**
  - `login.html`, `register.html`: used by the accounts views.

- **`templates/pages/`**
  - `dashboard.html`, `faq.html`, `screen1.html`, `screen2.html`, `screen3.html`, `student_achievements.html`, `welcome.html`.
  - **`partials/`** contains reusable pieces (e.g. `s1_student.html`) likely included in the main page templates to customize content for different roles (student, organization, administrator).

---

### 📦 Static Assets
- **`static/css/styles.css`**
  - Includes site-wide CSS styling used by templates.

---

## 🔗 How the Pieces Interact

1. **Request routing**
   - Incoming requests hit Django’s URL resolver via `opportunity_app/urls.py`.
   - URLs are delegated to app-specific routers: `accounts/urls.py` or `pages/urls.py`.

2. **View execution**
   - Views in `accounts/views.py` or `pages/views.py` execute logic (authentication, database queries, business rules).
   - Views pass context data to templates for rendering.

3. **Template rendering**
   - Templates in `templates/` generate the final HTML response.
   - Partials (inside `templates/pages/partials/`) are included to adapt content for user roles.

4. **Data storage**
   - Models in `accounts/models.py` and `pages/models.py` define database tables.
   - Migrations in each app’s `migrations/` folder track schema changes.

5. **Static files**
   - CSS and other static assets are served via Django’s static file handling (configured in `settings.py`).

---

## 🧪 Running the App
From the project root:

```bash
python manage.py migrate
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/` in a browser.

---

> 📌 Note: This file is intended as a project-specific overview and does not replace the main `Readme.md` in the repository.