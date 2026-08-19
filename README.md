# CodeGuardian AI

Intelligent first-level code review for modern development teams.

## Project Overview
CodeGuardian AI is an automated, AI-powered software engineering quality platform. It provides deterministic static analysis coupled with Google Gemini's AI reasoning to identify security vulnerabilities, code quality issues, maintainability problems, and poor coding practices in Python applications.

## Problem
AI coding assistants have dramatically increased the amount of code developers can produce. However, faster code generation can also create insecure, complex, and unmaintainable code. Human reviewers spend significant time identifying these issues manually.

## Solution
CodeGuardian AI provides an automated first-pass review, combining strict deterministic static code analysis with intelligent AI-powered explanations. It acts as an intelligent first-level code reviewer, catching common problems before the code reaches a human reviewer.

## Features
- Secure Authentication via JWT.
- Project & Repository management.
- Dual-engine Code Analysis (Deterministic Static Analysis + Google Gemini AI).
- Transparent Quality Scoring (Security, Quality, Maintainability, Complexity, Performance).
- Issue Severity Grouping (Critical, High, Medium, Low, Info).
- Professional Dashboard with Chart.js analytics.
- Code Review History and Version Comparison.

## Architecture
CodeGuardian AI uses a modular Django architecture, strictly separating concerns:
- **`accounts/`**: Authentication and user-related functionality.
- **`projects/`**: Project management and code submissions.
- **`reviews/`**: Review records, issues, reports, scores, and history.
- **`analyzer/`**: Deterministic static analysis logic (AST, Ruff, Bandit, Radon).
- **`ai_engine/`**: Gemini API integration and AI reasoning.
- **`dashboard/`**: UI views and analytics.

## Tech Stack
- **Backend:** Python 3, Django, Django REST Framework
- **Database:** MySQL
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5, Chart.js
- **AI Integration:** Google Gemini API
- **Static Analysis Tools:** Python AST, Ruff, Bandit, Radon

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/codeguardian-ai.git
   cd codeguardian-ai
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory based on `.env.example`:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   GEMINI_API_KEY=your-gemini-key
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=codeguardian
   DB_USER=root
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=3306
   ```

5. **Database Setup (MySQL)**
   Ensure MySQL is running locally and create the database:
   ```sql
   CREATE DATABASE codeguardian;
   ```
   Then run migrations:
   ```bash
   python manage.py migrate
   ```

6. **Running Locally**
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000`

## API Documentation
The REST API uses JWT for authentication.

- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Obtain JWT tokens
- `GET /api/projects/` - List user projects
- `POST /api/projects/` - Create a project
- `POST /api/projects/<id>/submissions/` - Submit code for analysis
- `GET /api/dashboard/` - Retrieve dashboard analytics

## Testing
Run the automated test suite using Django's test runner:
```bash
python manage.py test
```

## Security
- User-submitted code is **never** executed (no `eval()` or `exec()`).
- Strict validation and isolation of user data.
- Passwords hashed using Django's built-in `PBKDF2`.
- Secure JWT authentication for API endpoints.

## Future Roadmap
- GitHub repository integration.
- Automated Pull Request analysis.
- Multi-language support (JavaScript, Java, C++).
- Team accounts and analytics.

## Author
CodeGuardian AI Implementation
