# Opportunity App - Project Documentation

## 📋 Project Overview

**Opportunity App** is a Django-based web application designed to facilitate connections between students, organizations, and administrators. The platform enables students to explore opportunities, log their achievements, and track professional growth while allowing organizations to post and manage opportunities. Administrators maintain oversight and control over the entire platform.

### Key Features:
- **Multi-role user system** (Student, Organization, Administrator)
- **Email-based authentication** with custom user model
- **Student achievement tracking** system
- **Role-based dashboard screens** with tailored interfaces
- **PostgreSQL database** for persistent data storage
- **Responsive template system** with role-specific partials

---

## 🗂️ Project Structure & File Descriptions

### **Root Level Files**

#### `manage.py`
Django's command-line utility for administrative tasks. Used to run migrations, start the development server, create SuperUsers, and interact with the Django shell.

#### `bootstrap.py`
One-shot setup script that automates the project initialization process. It:
- Creates and activates a Python virtual environment
- Installs Django, PostgreSQL driver (psycopg2-binary), and python-dotenv
- Configures the PostgreSQL database connection
- Sets up environment variables
- Creates initial templates and static files

#### `requirements.txt`
Lists all Python package dependencies with version constraints:
- `Django>=5.0,<6.0` — Web framework
- `psycopg2-binary` — PostgreSQL database adapter
- `python-dotenv` — Environment variable management

#### `Readme.md`
Original project setup guide with installation instructions, test account credentials, and server startup commands.

#### `Readme_ryan_devita.md` (This File)
Comprehensive documentation of the project architecture, file structure, and file interactions.

#### `output_20251011.xml`
Generated XML export file (likely from project directory scanning utility).

#### `pack_dir_to_xml.py`
Utility script for converting directory structures to XML format.

#### `test.py`
Testing script for development/debugging purposes.

---

### **opportunity_app/ (Django Project Configuration)**

#### `settings.py`
Central Django configuration file containing:
- **Database configuration** — PostgreSQL connection settings
- **Installed apps** — Registers `accounts` and `pages` apps along with Django's built-in apps
- **Middleware stack** — Security, session, CSRF, authentication, and messaging
- **Template configuration** — Template directory and context processors
- **Static files** — CSS/JavaScript location and serving
- **Authentication** — Custom User model (`AUTH_USER_MODEL = 'accounts.User'`)
- **Authentication flow** — Login/logout redirect URLs
- **Password validators** — Minimum 8 characters, common password checks, etc.

#### `urls.py`
Root URL router that directs all incoming requests. Includes:
- `/admin/` — Django admin panel
- `/accounts/` — User authentication routes (prefix)
- `/` — Pages app routes (prefix)
- `/logout/` — Direct logout handler

#### `asgi.py`
ASGI (Asynchronous Server Gateway Interface) configuration for async deployment environments.

#### `wsgi.py`
WSGI (Web Server Gateway Interface) configuration for production deployment.

---

### **accounts/ (User Authentication & Management)**

#### `models.py`
Defines the custom `User` model extending Django's `AbstractUser`:
- **user_type** — CharField with three choices: Student, Organization, Administrator
- **email** — Unique email field (used for login instead of username)
- **USERNAME_FIELD** — Set to 'email' for email-based authentication
- **Auto-username generation** — Saves email as username for compatibility

#### `views.py`
Contains view classes for authentication:
- **RegisterView** — Handles user registration with user type selection
- **CustomLoginView** — Custom login view that:
  - Uses email instead of username
  - Redirects authenticated users to `screen1`
  - Passes selected user type through session/GET parameters

#### `forms.py`
Django forms for authentication:
- **UserRegistrationForm** — Registration form with:
  - Email field
  - Password confirmation
  - User type selection (radio buttons)
- **EmailAuthenticationForm** — Login form that relabels username field as "Email"

#### `urls.py`
Routes for user accounts:
- `/accounts/login/` → CustomLoginView
- `/accounts/register/` → RegisterView
- `/accounts/logout/` → Built-in LogoutView

#### `admin.py`
Registers User model in Django admin interface.

#### `apps.py`
Application configuration file.

#### `tests.py`
Test file for accounts app functionality.

---

### **pages/ (Core Application Pages & Features)**

#### `models.py`
Defines the `Achievement` model for student accomplishment tracking:
- **student** — ForeignKey to User (students only)
- **title** — Achievement name
- **description** — Detailed explanation
- **date_completed** — When the achievement was earned

#### `views.py`
Handles all page rendering and achievement management:
- **welcome()** — Public landing page
- **screen1()** — Post-login welcome screen with role-specific content
- **screen2()** — Navigation screen (role-specific)
- **screen3()** — Navigation screen (role-specific)
- **student_achievements()** — Achievement dashboard:
  - Displays student's achievements
  - Allows creating new achievements via form
  - Redirects non-students
  - Filters achievements by logged-in student
- **faq()** — Frequently Asked Questions page
- **dashboard()** — General dashboard page

#### `forms.py`
Application forms:
- **AchievementForm** — ModelForm for creating/editing achievements with:
  - Title, description, date_completed fields
  - HTML5 date picker for date_completed

#### `urls.py`
Routes for pages app:
- `/` → welcome
- `/screen1/` → screen1
- `/screen2/` → screen2
- `/screen3/` → screen3
- `/achievements/` → student_achievements
- `/faq/` → faq
- `/dashboard/` → dashboard

#### `admin.py`
Registers models in Django admin.

#### `apps.py`
Application configuration.

#### `tests.py`
Test file for pages app functionality.

---

### **templates/ (HTML Templates)**

#### `base.html`
Master template providing site-wide layout, navigation, and styling inheritance.

#### `accounts/login.html`
Login page with email and password form fields.

#### `accounts/register.html`
Registration page with email, password, and user type selection.

#### `pages/welcome.html`
Public landing page greeting.

#### `pages/screen1.html`
Post-authentication welcome screen displaying:
- User's name greeting
- Navigation buttons to Screen 2 and Screen 3
- Links to achievements (if student) and other sections
- Role-specific content via partials

#### `pages/screen2.html`
Second navigation screen with role-specific content.

#### `pages/screen3.html`
Third navigation screen with role-specific content.

#### `pages/student_achievements.html`
Students-only page displaying:
- List of completed achievements
- Form to add new achievements
- Achievement details (title, description, date)

#### `pages/faq.html`
Frequently Asked Questions page.

#### `pages/dashboard.html`
General dashboard for platform overview.

#### `pages/partials/`
Role-specific content fragments:
- **s1_student.html** — Screen 1 content for students
- **s1_organization.html** — Screen 1 content for organizations
- **s1_administrator.html** — Screen 1 content for administrators
- **s2_student.html**, **s2_organization.html**, **s2_administrator.html** — Screen 2 variants
- **s3_student.html**, **s3_organization.html**, **s3_administrator.html** — Screen 3 variants

(Partials are included in their respective screen templates for role-specific rendering)

---

### **static/ (Client-Side Assets)**

#### `css/styles.css`
Application-wide CSS styling for:
- Layout and responsive design
- Form styling
- Navigation appearance
- Role-specific theming

---

## 🔄 File Interactions & Data Flow

### **User Authentication Flow**

```
User visits app
    ↓
[request] → urls.py (ROOT_URLCONF = 'opportunity_app.urls')
    ↓
Match path /accounts/login/
    ↓
[routes to] accounts/urls.py
    ↓
CustomLoginView (accounts/views.py)
    ↓
Render accounts/login.html + EmailAuthenticationForm (accounts/forms.py)
    ↓
Form submission
    ↓
[validates against] accounts/models.py → User.objects.get(email=...)
    ↓
Authentication successful
    ↓
[redirects to] screen1 view (pages/views.py)
    ↓
[renders] pages/screen1.html with user.user_type context
    ↓
[includes] pages/partials/s1_[user_type].html
    ↓
[styled by] static/css/styles.css
```

### **Registration Process**

```
User visits /accounts/register/
    ↓
RegisterView (accounts/views.py)
    ↓
Render accounts/register.html + UserRegistrationForm (accounts/forms.py)
    ↓
Form includes user_type radio buttons
    ↓
Form submission
    ↓
[validates and creates] accounts/models.py → User instance
    ↓
User saved to PostgreSQL (settings.py database config)
    ↓
[auto-logs in user]
    ↓
[redirects to] screen1
```

### **Achievement Management Flow** (Students Only)

```
Authenticated student visits /achievements/
    ↓
student_achievements() view (pages/views.py)
    ↓
[checks] request.user.user_type == 'student'
    ↓
[if not student, redirects] to screen1
    ↓
[if GET request]
    └→ Render pages/student_achievements.html + AchievementForm (pages/forms.py)
    
[if POST request]
    ↓
form_valid() → form.save(commit=False)
    ↓
[links achievement to] achievement.student = request.user
    ↓
[saves to database] Achievement model (pages/models.py)
    ↓
[redirects] back to student_achievements (refreshes page)
    ↓
[queries] Achievement.objects.filter(student=request.user)
    ↓
[renders] achievements list in template
```

### **Navigation Between Screens**

```
screen1.html
    ↓
[user clicks] "Go to Screen 2" button
    ↓
[navigates to] /screen2/
    ↓
screen2() view (pages/views.py)
    ↓
[extracts role] request.user.user_type
    ↓
[renders] pages/screen2.html with role context
    ↓
[includes] pages/partials/s2_[role].html
    ↓
[styled by] static/css/styles.css
    ↓
[same pattern] for screen3
```

### **Database Operations**

```
Django ORM
    ↓
models.py (accounts/pages)
    ↓
settings.py (PostgreSQL config)
    ↓
34.16.174.60:5432 (Remote database)
    ↓
Database tables:
    - auth_user (extended by accounts_user)
    - pages_achievement
    - auth_group
    - etc.
```

---

## 🔐 Security & Access Control

1. **Email-based authentication** — Prevents username enumeration attacks
2. **Password validators** — Enforces strong passwords (8+ chars, no common passwords)
3. **@login_required** — Protects sensitive views (screen1-3, achievements)
4. **User type validation** — Ensures role-based access (only students can view achievements)
5. **CSRF protection** — Middleware prevents cross-site request forgery
6. **Session management** — HTTP-only session cookies prevent JavaScript access

---

## 🚀 Development Workflow

### Setup
```bash
python bootstrap.py          # One-time setup
source venv/Scripts/activate # (Windows) or source venv/bin/activate (Unix)
pip install -r requirements.txt
```

### Running the Server
```bash
python manage.py migrate     # Apply database migrations
python manage.py runserver   # Start dev server on 127.0.0.1:8000
```

### Creating Superuser
```bash
python manage.py createsuperuser  # Access /admin/ panel
```

### Testing
```bash
python test.py               # Run tests
```

---

## 📝 Configuration & Environment

Settings are defined in `opportunity_app/settings.py` and loaded from `.env`:
- **DJANGO_SECRET_KEY** — Secret key for security
- **DJANGO_DEBUG** — Debug mode (True for development)
- **ALLOWED_HOSTS** — Allowed domain names
- **DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT** — PostgreSQL credentials

---

## 🎯 Key Design Patterns Used

1. **Class-Based Views (CBV)** — RegisterView, CustomLoginView extend Django's generic views
2. **ModelForm** — AchievementForm auto-generates from Achievement model
3. **Foreign Keys** — Achievement links to User for data relationships
4. **Template Inheritance** — base.html extends to all pages
5. **Middleware Pipeline** — Middleware stack handles security, sessions, authentication
6. **Decorators** — @login_required gates protected views

---

## 📚 Additional Notes

- The project uses Django's built-in admin interface (`/admin/`) for managing data
- Role-specific templates (`partials/`) allow different UI for each user type
- Static files (CSS) are served from `static/` directory
- The `.env` file stores sensitive credentials (database, secret key)
- Migrations track schema changes in `accounts/migrations/` and `pages/migrations/`

---

**Created by:** Ryan DeVita  
**Project:** Opportunity App (Spring 2026)  
**Framework:** Django 5.0+  
**Database:** PostgreSQL  
