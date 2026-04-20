@echo off
echo Running backend coverage...
call run_coverage_backend.bat
if %ERRORLEVEL% neq 0 (
  echo Backend coverage failed.
  exit /b %ERRORLEVEL%
)

echo Running frontend coverage...
call run_coverage_frontend.bat
if %ERRORLEVEL% neq 0 (
  echo Frontend coverage failed.
  exit /b %ERRORLEVEL%
)
echo Coverage run complete.