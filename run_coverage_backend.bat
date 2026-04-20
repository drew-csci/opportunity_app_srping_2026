@echo off
echo Running Django tests with coverage...
coverage run manage.py test
coverage report
coverage html