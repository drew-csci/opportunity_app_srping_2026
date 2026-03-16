# Opportunity App

## Project Description

The Opportunity App is a website made with Django, which is a tool for building websites using Python. It helps students, organizations, and admins manage things like volunteer jobs or school opportunities. The app lets people sign up and log in with their email. Different users see different pages based on their role, like students can add their achievements, and organizations can see special info.

## Description of Each File and Folder

### Root Level Files

- **bootstrap.py**: A script that sets up the whole project. It makes a special folder for Python code, installs needed programs, creates the Django project and parts of it, sets up the database, and makes basic pages for login and main screens.
- **manage.py**: A helper file from Django. You use it to start the website server, update the database, or do other tasks like creating admin users.
- **output_20251011.xml**: A file made by pack_dir_to_xml.py. It packs all the project files into one XML file, like a zip but in text form.
- **pack_dir_to_xml.py**: A tool that takes all files in a folder and puts them into an XML file. It handles text files and pictures differently.
- **Readme.md**: Instructions on how to set up and run the app. It tells you how to install things, start the server, and gives test user accounts.
- **requirements.txt**: A list of programs the app needs, like Django and database tools.
- **test.py**: A small script that makes example HTML files for different user types and screens.

### Folders

- **accounts/**: Handles users. It has code for signing up, logging in, and storing user info like if they are a student or admin.
- **opportunity_app/**: The main project folder. It has settings for the whole app, like database info and where files are stored.
- **pages/**: Manages the website pages. It has code for showing screens, letting students add achievements, and other pages like FAQ.
- **static/**: Holds files like CSS for styling the website.
- **templates/**: Holds HTML files that make up the web pages. There's a base page that others build on, and specific pages for login, main screens, etc.

## How the Files Interact

Django uses manage.py to run the app. The settings in opportunity_app tell Django what to do, like which database to use and where to find pages.

When someone visits the site, Django looks at the URLs and sends them to the right code in accounts or pages. That code talks to the database if needed, gets data, and puts it into HTML templates to show on the screen.

For example, when a student logs in, the accounts code checks them, then pages code shows their screen with their achievements from the database.

## Summary

This is a Django website with parts for users and pages. It uses a database to store info and lets different types of users do different things. It's set up in a clean way so it's easy to add more features.
