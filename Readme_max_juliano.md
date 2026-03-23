# OPPORTUNITY_APP_SPRING_2026 - Project Structure & Architecture

## Project Overview

**OPPORTUNITY_APP_SPRING_2026** is a Django-based web application designed for managing student opportunities with role-based access. It supports three user types: Students, Organizations, and Administrators, each with different capabilities.

---

## Directory Structure & File Purposes

### **Root Configuration Files**
- **manage.py** — Django management utility for running server, migrations, and commands
- **bootstrap.py** — Initialization or setup script (likely for data seeding)
- **requirements.txt** — Python dependencies (Django 5.0+, PostgreSQL driver, python-dotenv)
- **Readme.md** — Setup instructions and test account credentials

### **opportunity_app/** (Main Django Project)
The core project configuration module:

- **opportunity_app/settings.py** — Django configuration including:
  - Database connection (PostgreSQL)
  - Installed apps registration (accounts, pages)
  - Authentication settings (custom User model)
  - Static files configuration
  - Login/logout redirect URLs
  - Password validators

- **opportunity_app/urls.py** — Root URL router that directs traffic to `accounts/` and `pages/` apps

- **opportunity_app/asgi.py** — ASGI server entry point (for async servers)

- **opportunity_app/wsgi.py** — WSGI production server entry point

### **accounts/** (Authentication & User Management)
Handles user registration, login, and role-based user profiles.

**Models:**
- **accounts/models.py** — Custom `User` model extending Django's AbstractUser with three roles:
  - `student`
  - `organization`
  - `administrator`
  - Uses email for authentication instead of username
  - Auto-generates username from email on save
  - Includes `display_name` property for user-friendly names

**Views:**
- **accounts/views.py**
  - `RegisterView` — Handles new user registration with role selection
  - `CustomLoginView` — Email-based login with role-aware redirection

**Routes:**
- **accounts/urls.py** — Maps the following paths:
  - `/accounts/login/` — User login
  - `/accounts/register/` — User registration
  - `/accounts/logout/` — User logout

**Forms:**
- **accounts/forms.py** — Contains:
  - `UserRegistrationForm` — For user sign-up with role selection
  - `EmailAuthenticationForm` — Validates email-based login

---

### **pages/** (Main Application Features)
Serves content and manages opportunity-related features.

**Models:**
- **pages/models.py** — `Achievement` model storing student accomplishments with:
  - Foreign key link to User (student-only)
  - Title and description fields
  - Date completion tracking

**Views:**
- **pages/views.py**
  - `welcome()` — Public landing page (no login required)
  - `screen1()` — First workflow screen (login-required, role-specific content)
  - `screen2()` — Second workflow screen (login-required, role-specific content)
  - `screen3()` — Third workflow screen (login-required, role-specific content)
  - `student_achievements()` — Allows students to view/add achievements (student-only)
  - `faq()` — Frequently asked questions page
  - `dashboard()` — Dashboard/info page

**Routes:**
- **pages/urls.py** — Maps the following paths:
  - `/` — Welcome page
  - `/screen1/` — First workflow screen
  - `/screen2/` — Second workflow screen
  - `/screen3/` — Third workflow screen
  - `/achievements/` — Student achievements
  - `/faq/` — FAQ page
  - `/dashboard/` — Dashboard

**Forms:**
- **pages/forms.py** — Contains `AchievementForm` for creating/editing student achievements

---

### **templates/** (HTML Templates)
Role-based and page-specific templates organized as follows:

- **base.html** — Base layout template (likely contains navigation, styling, shared elements)

- **accounts/** — Authentication templates:
  - `login.html` — Login page
  - `register.html` — Registration page

- **pages/** — Application page templates:
  - `welcome.html` — Public welcome/landing page
  - `screen1.html` — First workflow screen
  - `screen2.html` — Second workflow screen
  - `screen3.html` — Third workflow screen
  - `student_achievements.html` — Student achievements page
  - `faq.html` — FAQ page
  - `dashboard.html` — Dashboard page

- **pages/partials/** — Role-specific content snippets:
  - `s1_administrator.html` — Screen 1 admin view
  - `s1_organization.html` — Screen 1 organization view
  - `s1_student.html` — Screen 1 student view
  - `s2_administrator.html` — Screen 2 admin view
  - `s2_organization.html` — Screen 2 organization view
  - `s2_student.html` — Screen 2 student view
  - `s3_administrator.html` — Screen 3 admin view
  - `s3_organization.html` — Screen 3 organization view
  - `s3_student.html` — Screen 3 student view

### **static/** (Frontend Assets)
- **static/css/styles.css** — Application-wide styling and CSS rules

### **migrations/** (Database Schema)
Located in both `accounts/` and `pages/` directories:
- Track database schema changes
- Allow reproducible database state across environments

---

## Data Flow & Interactions

### **Authentication Flow**
```
User Input → Login View (email)
    ↓
CustomLoginView authenticates against User model
    ↓
Session created
    ↓
Redirect to screen1 (based on role)
```

### **Page Access Flow**
```
Request to screen1/screen2/screen3
    ↓
Login required check
    ↓
View extracts user.user_type
    ↓
Render template with role context
    ↓
Template selects appropriate partial (s1_student.html, etc.)
```

### **Achievement Management Flow**
```
Student accesses /achievements/
    ↓
View checks user_type == 'student'
    ↓
GET: Display form + list of user's achievements
    ↓
POST: Form submission
    ↓
Save achievement linked to student user
    ↓
Redirect back to achievements page
```

---

## Key Interactions Between Components

### **1. Authentication System**
- **User Model** (accounts/models.py) is the central authentication point
- **CustomLoginView** uses email to authenticate against **User model**
- **RegisterView** creates new users and assigns roles at registration time
- All protected views check `request.user.user_type`

### **2. Role-Based Content Delivery**
- **Views** render base templates with role context
- **Templates** use partial templates to display role-specific content
- Examples:
  - `screen1.html` includes `s1_student.html`, `s1_organization.html`, or `s1_administrator.html`
  - Role context is passed from view to template

### **3. Student Achievement Tracking**
- **Achievement Model** stores records linked to student users via ForeignKey
- **student_achievements() view** queries `Achievement` objects filtered by current user
- Only accessible to users with `user_type == 'student'`
- Form submission creates new Achievement records in PostgreSQL database

### **4. URL Routing Hierarchy**
```
opportunity_app/urls.py (root routes)
    ↓
pages/urls.py (main application routes)
accounts/urls.py (authentication routes)
    ↓
Views process requests and render templates
    ↓
Templates render HTML with data from context
```

---

## User Roles & Access Levels

| Role | Can Access | Primary Functions |
|------|------------|------------------|
| **Student** | Welcome, Screens 1-3, Achievements, FAQ, Dashboard | Track personal accomplishments, view opportunities |
| **Organization** | Welcome, Screens 1-3 (different content), FAQ, Dashboard | Post opportunities, manage listings |
| **Administrator** | All above + Django Admin panel (/admin) | Manage system, users, and data |

---

## Database Structure

The application uses **PostgreSQL** (configured in settings.py):

### **User Table** (accounts_user)
- Extends Django's AbstractUser
- Fields: email (unique, login credential), user_type (student/organization/administrator), username, password, first_name, last_name, etc.

### **Achievement Table** (pages_achievement)
- Foreign key to User (student only)
- Fields: title, description, date_completed
- Used only for students

---

## Key Configuration Settings

From `opportunity_app/settings.py`:

- **INSTALLED_APPS**: Includes Django core apps + custom apps (accounts, pages)
- **AUTH_USER_MODEL**: 'accounts.User' (uses custom user model)
- **DATABASES**: PostgreSQL connection details
- **LOGIN_URL**: 'login' (redirect for login_required)
- **LOGIN_REDIRECT_URL**: 'screen1' (post-login redirect)
- **LOGOUT_REDIRECT_URL**: 'login' (post-logout redirect)
- **STATIC_URL**: '/static/' (for CSS, JS, images)

---

## Environment Variables (from .env)

Configured via `python-dotenv`:

```
DJANGO_SECRET_KEY=<secret_key>
DJANGO_DEBUG=True/False
ALLOWED_HOSTS=<comma-separated hosts>
DB_NAME=opportunity
DB_USER=oppo_app
DB_PASSWORD=<password>
DB_HOST=<postgres_host>
DB_PORT=5432
```

---

## Authentication Test Accounts

Available for development/testing:

| Role | Email | Password |
|------|--------|-----------|
| Student | student_oppo@drew.edu | 1Opportunity! |
| Organization | org_oppo@drew.edu | 1Opportunity! |
| Administrator | admin_oppo@drew.edu | 1Opportunity! |

**Superuser for Admin Panel:**
- Email: `super_oppo@drew.edu`
- Username: `super_oppo`
- Password: `1OpportunityApp!`

---

## Architecture Summary

This is a **classic Django MTV (Models-Templates-Views) architecture**:

1. **Models** define data structure (User, Achievement)
2. **Views** handle business logic and authentication checks
3. **Templates** render HTML with context data, including role-specific partials
4. **URLs** route requests to appropriate views
5. **Forms** handle user input validation
6. **Static files** provide styling and frontend assets

The application separates concerns into two main Django apps:
- **accounts**: Manages authentication and user profiles
- **pages**: Manages application features and content

This separation makes the codebase maintainable and scalable for future feature additions.
