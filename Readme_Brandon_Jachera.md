# Opportunity App

## Project Description
The Opportunity App is a Django-based web application designed to connect students, organizations, and administrators. It provides a platform for students to discover volunteering, internship, and work opportunities while enabling organizations to post opportunities and manage interactions. The app includes user authentication, role-based dashboards, and features for managing achievements and user profiles.

---

## File Descriptions and Interactions

### Root Files
- **`manage.py`**: The entry point for Django administrative tasks, such as running the server and managing migrations.
- **`requirements.txt`**: Lists the dependencies required for the project, including Django, psycopg2-binary, and python-dotenv.
- **`.env`**: Stores environment variables, such as database credentials and Django settings, for secure configuration.

### Apps
#### `accounts/`
- **`models.py`**: Defines the custom `User` model with roles (`student`, `organization`, `administrator`) and additional fields like `email` and `user_type`.
- **`views.py`**: Contains views for user authentication, including login, registration, and logout.
- **`urls.py`**: Maps URLs to views for authentication-related actions.
- **`forms.py`**: Includes forms for user registration and login, extending Django's built-in forms.
- **`admin.py`**: Customizes the Django admin interface for managing users.

#### `pages/`
- **`models.py`**: Defines the `Achievement` model for students to track their accomplishments.
- **`views.py`**: Contains views for role-based screens (`screen1`, `screen2`, `screen3`), the FAQ page, and the dashboard.
- **`urls.py`**: Maps URLs to views for the pages app.
- **`templates/pages/`**: Contains HTML templates for the app's pages, including role-specific partials for dynamic content.

### Templates
- **`base.html`**: The main layout template, including navigation and placeholders for dynamic content.
- **`templates/pages/`**: Contains templates for specific pages like `welcome.html`, `faq.html`, and role-based screens.

### Static Files
- **`static/css/styles.css`**: Contains the CSS styles for the app, including layout and design for navigation, buttons, and forms.

### Utility Scripts
- **`bootstrap.py`**: A one-shot script to set up the project, including creating a virtual environment, installing dependencies, and initializing the Django project.
- **`pack_dir_to_xml.py`**: A utility script to recursively read files and generate an XML representation of their contents.

---

## File Interactions
1. **User Authentication**: 
   - `accounts/models.py` defines the `User` model.
   - `accounts/views.py` handles login, registration, and logout.
   - `accounts/urls.py` maps these views to URLs.
   - Templates in `templates/accounts/` render the authentication pages.

2. **Role-Based Screens**:
   - `pages/views.py` defines views for `screen1`, `screen2`, and `screen3`.
   - Templates in `templates/pages/partials/` provide role-specific content.
   - `base.html` dynamically includes these templates based on the user's role.

3. **Achievements**:
   - `pages/models.py` defines the `Achievement` model.
   - `pages/views.py` handles the logic for creating and displaying achievements.
   - `templates/pages/student_achievements.html` renders the achievements page.

4. **Navigation and Layout**:
   - `base.html` provides the main layout and navigation.
   - `static/css/styles.css` styles the app's UI.

5. **Database Configuration**:
   - `.env` stores database credentials.
   - `settings.py` reads these credentials and configures the database connection.

6. **Project Setup**:
   - `bootstrap.py` automates the setup process, including creating apps and configuring settings.

---

## How to Use
1. **Setup**:
   - Follow the instructions in `Readme.md` to set up the virtual environment and install dependencies.
2. **Run the Server**:
   - Use `python manage.py runserver` to start the development server.
3. **Access the App**:
   - Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---