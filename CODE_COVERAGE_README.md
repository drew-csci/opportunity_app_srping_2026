# Code Coverage Analysis

This document explains how to run code coverage analysis for the Opportunity App project.

## Backend (Django) Coverage

### Prerequisites
- Install dependencies: `pip install -r requirements.txt`
- Ensure coverage.py is installed (included in requirements.txt)

### Running Coverage
1. Run the coverage script:
   ```
   run_coverage_backend.bat
   ```

2. Or run manually:
   ```
   coverage run manage.py test
   coverage report
   coverage html
   ```

### Coverage Reports
- **Console Report**: Displays coverage percentage in terminal
- **HTML Report**: Generated in `htmlcov/` directory - open `htmlcov/index.html` in browser

### Configuration
- Configuration file: `.coveragerc`
- Excludes migrations, test files, and common Django boilerplate
- Source: All Python files in the project

## Frontend (React/Vite) Coverage

### Prerequisites
- Install dependencies: `npm install` or `yarn install`
- Ensure @vitest/coverage-v8 is installed (included in devDependencies)

### Running Coverage
1. Run the coverage command:
   ```
   npm run test:coverage
   ```

2. Or run manually:
   ```
   npx vitest run --coverage
   ```

### Coverage Reports
- **Console Report**: Displays coverage percentage in terminal
- **JSON Report**: Generated as `coverage/coverage.json`
- **HTML Report**: Generated in `coverage/` directory - open `coverage/index.html` in browser

### Configuration
- Configured in `vite.config.js`
- Excludes node_modules, main.jsx, test files, and config files
- Uses V8 coverage provider

## Current Coverage Results

### Backend (Django) - 73% Overall Coverage
- **Total Statements**: 986
- **Missed**: 271
- **Coverage**: 73%

**Key Files Coverage:**
- `pages/views.py`: 79% (210 statements, 45 missed)
- `pages/models.py`: 93% (74 statements, 5 missed)
- `accounts/views.py`: 53% (32 statements, 15 missed)
- `pages/tests.py`: 100% (323 statements, 0 missed)

### Frontend (React/Vite) - 45% Overall Coverage
- **Total Statements**: Coverage enabled with V8
- **Coverage**: 45%

**Key Components Coverage:**
- `ActivityFeed.jsx`: 93% (high coverage from unit tests)
- `ConversationList.jsx`: 91% (high coverage from unit tests)
- `ChatWindow.jsx`: 73% (good coverage from unit tests)
- `Messaging.jsx`: 0% (needs integration tests fixed)

## Best Practices

1. Run coverage regularly during development
2. Don't aim for 100% coverage at expense of test quality
3. Focus on testing business logic over getters/setters
4. Use coverage reports to identify untested code paths
5. Integrate coverage into CI/CD pipeline