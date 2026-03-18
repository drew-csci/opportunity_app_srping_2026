# Opportunity App - Developer README

## 📋 Project Description

The **Opportunity App** is a Django-based web application that connects three key user types: **students**, **organizations**, and **administrators**. The platform enables students to discover volunteering, internship, and employment opportunities while tracking their achievements. Organizations can post and manage opportunities, and administrators oversee platform activity. The app features email-based authentication, role-based access control, personalized dashboards for each user type, and PostgreSQL for data persistence.

---

## 📁 Important Files and Folders

### Root-Level FilesCreate a new file in the current project named Readme_Dev_Hirpara.md and write the full README content into it.

The README should include:
- Project description
- Description of each important file and folder
- Explanation of how all files interact in the Django application

Write it in proper markdown format with headings and bullet points.

#### **manage.py**
- **Purpose**: Django's command-line utility for administrative operations
- **Common Commands**:
  - `python manage.py runserver` - Start development server
  - `python manage.py migrate` - Apply database migrations
  - `python manage.py makemigrations` - Generate migration files
  - `python manage.py createsuperuser` - Create admin user

#### **requirements.txt**
- **Purpose**: Lists all Python package dependencies
- **Contents**: Django, psycopg2-binary, python-dotenv
- **Usage**: `pip install -r requirements.txt`

#### **.env**
- **Purpose**: Stores sensitive environment variables (NOT committed to version control)
- **Contains**:
  - Database host, name, user, password, port
  - Django secret key
  - Debug mode setting
  - Allowed hosts

#### **bootstrap.py**
- **Purpose**: One-time automated setup script
- **Functionality**:
  - Creates Python virtual environment
  - Installs dependencies
  - Creates Django project and apps
  - Generates initial configuration files
  - Runs database migrations

---

### Django Project Configuration (`opportunity_app/`)

#### **settings.py**
- **Purpose**: Central configuration file for the entire Django project
- **Key Settings**:
  - `AUTH_USER_MODEL = 'accounts.User'` - Points to custom User model
  - `INSTALLED_APPS` - Registers Django apps
  - `DATABASES` - PostgreSQL connection settings (reads from `.env`)
  - `TEMPLATES` - Template engine configuration and directories
  - `STATIC_URL` - URL prefix for static files
  - `LOGIN_URL` / `LOGIN_REDIRECT_URL` - Authentication flow settings

#### **urls.py**
- **Purpose**: Root URL router that dispatches HTTP requests to apps
- **Routing Logic**:
  - `path('admin/', admin.site.urls)` → Django admin panel
  - `path('', include('pages.urls'))` → Pages app routes
  - `path('accounts/', include('accounts.urls'))` → Authentication routes

#### **wsgi.py / asgi.py**
- **Purpose**: Server gateway interfaces for production deployment

---

### Accounts App (`accounts/`)

#### **models.py**
- **Purpose**: Defines database models for user management
- **Custom User Model**:
  - Extends Django's `AbstractUser`
  - Uses `email` as primary login field (prevents username enumeration)
  - Includes `user_type` field with three choices:
    - `student` - Students seeking opportunities
    - `organization` - Organizations posting opportunities
    - `administrator` - Platform administrators
  - Auto-generates `username` from `email` for Django admin compatibility
  - Provides `display_name` property to show full name or email

#### **views.py**
- **Purpose**: Handles authentication logic and user session management
- **Key Views**:
  - `CustomLoginView` - Processes email-based login
  - `RegisterView` - Handles user registration and auto-login
  - `LogoutView` - Manages user logout

#### **urls.py**
- **Purpose**: Maps authentication URLs to views
- **Routes**:
  - `/accounts/login/` → CustomLoginView
  - `/accounts/register/` → RegisterView
  - `/accounts/logout/` → LogoutView

#### **forms.py**
- **Purpose**: Provides form classes for authentication workflows
- **Forms**:
  - `EmailAuthenticationForm` - Login with email field
  - `UserRegistrationForm` - Registration with email, password, and role selection

#### **admin.py**
- **Purpose**: Customizes Django admin interface for User model management

#### **migrations/**
- **Purpose**: Stores database schema change history
- **Auto-generated** by `python manage.py makemigrations`

---

### Pages App (`pages/`)

#### **models.py**
- **Purpose**: Defines business logic models
- **Achievement Model**:
  - Stores student accomplishments
  - ForeignKey to User (only students)
  - Fields: `title`, `description`, `date_completed`

#### **views.py**
- **Purpose**: Contains view functions for page rendering
- **Key Views**:
  - `welcome()` - Landing page for unauthenticated users
  - `screen1()` - Role-based welcome screen post-login
  - `screen2()` - Role-based navigation screen
  - `screen3()` - Role-based navigation screen
  - `student_achievements()` - Achievement management (students only)
  - `faq()` - FAQ page
  - `dashboard()` - General dashboard

#### **urls.py**
- **Purpose**: Maps page URLs to views
- **Routes**:
  - `/` → welcome
  - `/screen1/` → screen1
  - `/screen2/` → screen2
  - `/screen3/` → screen3
  - `/achievements/` → student_achievements
  - `/faq/` → faq
  - `/dashboard/` → dashboard

#### **forms.py**
- **Purpose**: Provides ModelForm for achievements
- **AchievementForm** - Allows students to post new achievements

#### **migrations/**
- **Purpose**: Tracks Achievement model schema changes

---

### Templates (`templates/`)

#### **base.html**
- **Purpose**: Master template providing consistent layout across all pages
- **Includes**:
  - Navigation bar with authenticated/unauthenticated states
  - Header with branding
  - Main content block for child templates
  - Footer
  - Message display for alerts/notifications
  - CSRF token protection

#### **pages/**
- **welcome.html** - Landing page with role selection
- **screen1.html** - Post-login welcome screen
- **screen2.html** - Navigation screen
- **screen3.html** - Contact/information screen
- **student_achievements.html** - Achievement dashboard
- **faq.html** - FAQ page
- **dashboard.html** - General dashboard

#### **pages/partials/**
- **s1_student.html**, **s1_organization.html**, **s1_administrator.html** - Screen 1 role-specific content
- **s2_student.html**, **s2_organization.html**, **s2_administrator.html** - Screen 2 role-specific content
- **s3_student.html**, **s3_organization.html**, **s3_administrator.html** - Screen 3 role-specific content

#### **accounts/**
- **login.html** - Email-based login form
- **register.html** - User registration form

---

### Static Files (`static/`)

#### **css/styles.css**
- **Purpose**: Application-wide CSS styling
- **Includes**: Layout, navigation, buttons, forms, cards, responsive design
- **Loaded by**: All templates via `{% static 'css/styles.css' %}`

---

## 🔄 How Files Interact in the Django App

### User Authentication Flow

```
1. User visits http://127.0.0.1:8000/
   ↓
   manage.py routes to settings.py configuration
   ↓
   urls.py (project root) matches "" → pages.urls
   ↓
   pages/urls.py matches "" → pages/views.py welcome()
   ↓
   welcome() renders pages/welcome.html (extends base.html)
   ↓
   pages/welcome.html displays role selection buttons

2. User clicks "I am a Student" → /accounts/login/?type=student
   ↓
   urls.py (project root) matches /accounts/ → accounts/urls.py
   ↓
   accounts/urls.py matches login/ → accounts/views.py CustomLoginView
   ↓
   CustomLoginView.get() extracts ?type=student, renders accounts/login.html

3. User enters email and password, form POSTs
   ↓
   accounts/views.py CustomLoginView processes POST request
   ↓
   accounts/forms.py EmailAuthenticationForm validates:
     - Queries accounts/models.py User.objects.get(email='...')
     - Verifies password hash against database
   ↓
   If valid: auth_login(request, user) creates session
   ↓
   Redirects to LOGIN_REDIRECT_URL = 'screen1' (defined in settings.py)

4. User redirected to /screen1/
   ↓
   pages/urls.py matches screen1/ → pages/views.py screen1()
   ↓
   @login_required decorator checks session validity
   ↓
   screen1() extracts request.user.user_type = 'student'
   ↓
   Renders pages/screen1.html with role context

5. pages/screen1.html extends base.html
   ↓
   base.html provides navigation and layout
   ↓
   screen1.html contains conditional:
     {% if request.user.user_type == 'student' %}
       {% include "pages/partials/s1_student.html" %}
   ↓
   s1_student.html displays student-specific options

6. Styling applied from static/css/styles.css
   ↓
   Browser renders complete HTML with CSS
```

### Database and Configuration Flow

```
Django Startup:
  ↓
  settings.py loads via manage.py
  ↓
  .env file is read: load_dotenv(BASE_DIR / '.env')
  ↓
  Database credentials extracted from .env:
    - DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
  ↓
  DATABASES configuration created with PostgreSQL engine
  ↓
  psycopg2-binary establishes connection to 34.16.174.60:5432

During Request Processing:
  ↓
  View requests data (e.g., User.objects.get(email='...'))
  ↓
  Django ORM translates to SQL query
  ↓
  psycopg2-binary executes query over database connection
  ↓
  PostgreSQL returns results
  ↓
  View processes data and renders template
  ↓
  Template displayed to user via base.html layout
```

### Achievement Management Flow (Students Only)

```
1. Student clicks "My Achievements" link in s1_student.html partial
   ↓
   Link URL from {% url 'student_achievements' %} → /achievements/

2. pages/urls.py matches achievements/ → pages/views.py student_achievements()
   ↓
   @login_required checks authentication
   ↓
   View checks: request.user.user_type == 'student'
   ↓
   If not student: redirect to screen1

3. GET request (page load):
   ↓
   pages/views.py queries:
     Achievement.objects.filter(student=request.user)
   ↓
   accounts/models.py User model linked via ForeignKey
   ↓
   pages/models.py Achievement model returns queryset
   ↓
   pages/forms.py AchievementForm() instantiated for display
   ↓
   Renders pages/student_achievements.html with:
     - Form for posting new achievement
     - List of past achievements

4. Template displays achievements:
   ↓
   pages/student_achievements.html extends base.html
   ↓
   {% for achievement in achievements %} loops through queryset
   ↓
   Displays: title, date_completed, description
   ↓
   static/css/styles.css applies styling

5. Student submits new achievement form:
   ↓
   Form POSTs to student_achievements() view
   ↓
   pages/forms.py AchievementForm validates data
   ↓
   If valid:
     - achievement = form.save(commit=False)
     - achievement.student = request.user  ← Links to current user
     - achievement.save()  ← INSERT into database
   ↓
   pages/models.py Achievement inserted into PostgreSQL
   ↓
   View redirects to student_achievements
   ↓
   New query retrieves achievements (now includes new one)
   ↓
   Template re-renders with updated list
```

### Role-Based Screen Rendering

```
1. User logs in as organization → redirected to /screen1/

2. pages/views.py screen1() view:
   ↓
   Extracts request.user.user_type = 'organization'
   ↓
   Passes to template context

3. pages/screen1.html conditional rendering:
   ↓
   {% if request.user.user_type == 'organization' %}
     {% include "pages/partials/s1_organization.html" %}
   ↓
   s1_organization.html displays organization-specific content:
     - Post opportunity button
     - Manage applications
     - View analytics

4. Template inheritance:
   ↓
   s1_organization.html inherits styling from base.html
   ↓
   base.html extends from static/css/styles.css
   ↓
   Navigation bar shows organization-specific links
   ↓
   Footer and header consistent across all roles

5. Same applies for screens 2 and 3:
   ↓
   pages/screen2.html includes partials/s2_*.html
   ↓
   pages/screen3.html includes partials/s3_*.html
   ↓
   Each role sees different options
```

### Static Files and CSS Integration

```
1. Template requests static CSS:
   ↓
   {% load static %}
   <link rel="stylesheet" href="{% static 'css/styles.css' %}">

2. Django static file handler processes request:
   ↓
   settings.py defines: STATIC_URL = '/static/'
   ↓
   STATICFILES_DIRS = [BASE_DIR / 'static']

3. Browser fetches /static/css/styles.css
   ↓
   static/css/styles.css loads in browser

4. Styling applied to HTML elements:
   ↓
   Navigation, buttons, forms, cards rendered with CSS
   ↓
   Responsive design rules applied
   ↓
   User sees styled interface
```

---

## 🔒 Security Features

| Component | Security Mechanism |
|-----------|-------------------|
| **.env file** | Credentials NOT in version control |
| **settings.py** | Loads secrets from environment variables only |
| **accounts/models.py** | Email-based auth prevents username enumeration |
| **accounts/forms.py** | Password validators enforce 8+ chars, complexity |
| **templates/** | `{% csrf_token %}` prevents CSRF attacks |
| **views.py** | `@login_required` protects sensitive views |
| **models.py** | ForeignKey constraints ensure data integrity |

---

## 🚀 Getting Started

### Initial Setup
```bash
# Run bootstrap.py for one-time setup
python bootstrap.py

# Activate virtual environment
source .venv/bin/activate  # On Mac/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the Application
```bash
# Start development server
python manage.py runserver

# Access at http://127.0.0.1:8000/
```

### Create Admin User
```bash
python manage.py createsuperuser

# Access admin panel at http://127.0.0.1:8000/admin/
```

### Create Database Migrations
```bash
# After modifying models
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

---

## 📊 Key Interactions Summary

| From | To | Purpose |
|------|-----|---------|
| **manage.py** | settings.py | Load configuration |
| **settings.py** | .env | Read credentials |
| **urls.py** | accounts/urls.py, pages/urls.py | Route requests |
| **views.py** | models.py | Query database |
| **models.py** | PostgreSQL (via psycopg2) | Persist data |
| **views.py** | templates/ | Render HTML |
| **templates/** | base.html | Inherit layout |
| **templates/** | static/css/styles.css | Apply styling |
| **forms.py** | models.py | Validate and save data |

---

This README provides a comprehensive overview of the Opportunity App's structure and interactions, enabling developers to understand and extend the application effectively.
