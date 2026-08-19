# CodeGuardian AI - Ultimate Technical Reference Guide

Welcome to the comprehensive technical documentation for **CodeGuardian AI**. This guide explains every file, module, database model, security rule, algorithm, and API endpoint in deep technical detail using simple, clear language.

---

## Table of Contents
1. [Core Philosophy & How the System Works](#1-core-philosophy--how-the-system-works)
2. [Complete File Directory Inventory](#2-complete-file-directory-inventory)
3. [Analysis Engines & Pipeline (Deep Dive)](#3-analysis-engines--pipeline-deep-dive)
4. [The Score Monotonicity Guard Algorithm](#4-the-score-monotonicity-guard-algorithm)
5. [Polyglot Security & AI Refactoring Engine](#5-polyglot-security--ai-refactoring-engine)
6. [Database Schema & Django Models](#6-database-schema--django-models)
7. [Authentication Architecture & Fallback Mechanism](#7-authentication-architecture--fallback-mechanism)
8. [GitHub Repository Integration Engine](#8-github-repository-integration-engine)
9. [Interactive Code Studio & Frontend Architecture](#9-interactive-code-studio--frontend-architecture)
10. [Complete REST API Reference Manual](#10-complete-rest-api-reference-manual)

---

## 1. Core Philosophy & How the System Works

### 1.1 Why CodeGuardian AI Was Built
Traditional code linters (like Flake8 or ESLint) only check basic style rules. Generative AI tools (like ChatGPT) can give suggestions but often produce code with hidden syntax errors or lower quality scores. 

CodeGuardian AI combines **both worlds**:
1. **Deterministic Scanners (AST, Bandit, Radon, Ruff):** Compute exact, un-biasable math, metrics, line numbers, and security vulnerability penalties.
2. **Generative AI (Google Gemini 1.5 Flash):** Generates human-readable architectural summaries, line-by-line recommendations, and clean refactored code.
3. **Score Monotonicity Guard:** Ensures that applying AI fixes **never lowers your score** (it strictly improves or maintains your grade).

### 1.2 Step-by-Step System Flow
```text
[User Submits Code / GitHub Link]
               │
               ▼
   [Django View Controller]
               │
               ▼
   [ReviewEngine Orchestrator] ──► Checks File Extension (.py vs .js/.java/etc.)
               │
      ┌────────┴──────────────────────────┐
      ▼                                   ▼
[Python Engine]                 [Universal Polyglot Engine]
  ├─ AST Syntax & Docstring       ├─ Security Regex Scanners
  ├─ Bandit Security Scan         ├─ OWASP Top 10 Vulnerabilities
  ├─ Radon Complexity & MI        └─ Gemini AI Polyglot Review
  ├─ Ruff PEP 8 Linter
  └─ Gemini AI Review
      │                                   │
      └────────┬──────────────────────────┘
               ▼
     [Quality Scorer Engine] ──► Calculates Score (0 to 100) & Grade (A to F)
               │
               ▼
[Monotonicity Verification Guard] ──► Verifies Score_new >= Score_old
               │
               ▼
[Saved to Database & Rendered in Studio / Report / Dashboard]
```

---

## 2. Complete File Directory Inventory

Below is a breakdown of every single folder and file in the project:

- **`manage.py`**: Django's command-line utility used to run the server, execute migrations, and manage database tables.
- **`codeguardian/`**: Django configuration folder.
  - `settings.py`: Contains database settings, REST framework settings, installed apps, static file routes, and Gemini API key variables.
  - `urls.py`: Main URL router mapping `/dashboard/`, `/projects/`, `/reviews/`, and `/api/` endpoints to views.
  - `views.py`: Renders frontend HTML views (Dashboard, Projects, Studio, Report, Compare).
- **`apps/analyzer/`**: Core code analysis and AI refactoring engine.
  - `engine.py`: The orchestrator class (`ReviewEngine`) that runs reviews and executes the Score Monotonicity Guard.
  - `ast_analyzer.py`: Native Python AST parser for checking docstrings and syntax.
  - `bandit_analyzer.py`: AST security scanner checking hardcoded passwords, dangerous `eval()`, and shell injection.
  - `radon_analyzer.py`: Calculates Cyclomatic Complexity (Rank A-F) and Maintainability Index (0-100).
  - `ruff_analyzer.py`: Runs PEP 8 linter rules (unused imports, line lengths).
  - `gemini_analyzer.py`: Connects to Google Gemini API for Python reviews and generates guaranteed offline refactorings.
  - `universal_analyzer.py`: Polyglot multi-language scanner and refactoring engine for JavaScript, Java, C++, SQL, etc.
  - `scoring.py`: Mathematical quality scoring algorithm and grade calculation logic.
- **`apps/authentication/`**: User authentication module.
  - `auth.py`: Implements `FlexibleJWTAuthentication` to handle stale JWT tokens gracefully.
  - `views.py`: Login, registration, and user profile APIs.
- **`apps/projects/`**: Project management domain.
  - `models.py`: Database table for projects and repository links.
  - `views.py`: Project creation and listing APIs.
- **`apps/reviews/`**: Review runs, findings, and GitHub integration.
  - `models.py`: Database tables for `CodeReview` and `Finding`.
  - `github.py`: `GitHubFetcher` class that connects to GitHub API to scan repositories and fetch raw files.
  - `views.py`: Review submission, instant studio re-analysis, repository auditing, and version comparison APIs.
- **`templates/`**: Frontend HTML template files.
  - `base.html`: Main navigation bar, layout container, footer, and global create project modal.
  - `login.html`: Split-hero interactive login page with password toggle.
  - `register.html`: Registration page with real-time password strength meter.
  - `dashboard.html`: Engineering quality dashboard showing project cards and recent reviews.
  - `projects.html`: Projects grid and repository management.
  - `project_detail.html`: Quality progression line graph and repository file browser.
  - `review_studio.html`: Split-screen interactive code studio with multi-language sample picker.
  - `review_report.html`: Detailed review report viewer with diff inspector and score celebration toast.
  - `compare.html`: Side-by-side version comparison page.
- **`static/`**: Static assets.
  - `css/styles.css`: Aesthetic CSS design system with variables, glassmorphism, and keyframe micro-animations.
  - `js/api.js`: Frontend JavaScript API client wrapper.

---

## 3. Analysis Engines & Pipeline (Deep Dive)

### 3.1 `ReviewEngine` (`apps/analyzer/engine.py`)
`ReviewEngine` is the conductor of the analysis pipeline. When a developer submits code, it performs the following steps:
1. **Language Detection:** Extracts the extension from the filename (e.g. `app.js` -> `js`). If the extension is `py`, `pyw`, or `pyi`, it treats the file as Python. Otherwise, it treats it as a Polyglot file.
2. **Engine Dispatch:**
   - **For Python:** Invokes AST, Bandit, Radon, Ruff, and Gemini AI.
   - **For Non-Python:** Invokes `UniversalAIAnalyzer`.
3. **Scoring:** Passes all findings and metrics to `QualityScorer` to compute the Quality Score.
4. **Monotonicity Guard:** Re-evaluates `suggested_code`. If `suggested_score < raw_score`, it replaces `suggested_code` with a guaranteed refactor or original code so scores never drop.

### 3.2 `ASTAnalyzer` (`apps/analyzer/ast_analyzer.py`)
Parses Python code into an Abstract Syntax Tree (AST) using Python's native `ast` library.
- **Docstring Checks:** Checks every function (`ast.FunctionDef`) and class (`ast.ClassDef`) to see if it has a docstring (`ast.get_docstring(node)`). If missing, it adds a `LOW` severity finding.
- **Mutable Default Arguments:** Checks if function headers use mutable default arguments like `def fn(items=[])` or `def fn(config={})`. In Python, mutable default arguments retain state across function calls, creating subtle bugs. It flags a `MEDIUM` severity finding.
- **Global Variables:** Tracks use of `global var_name` statements, flagging `LOW` style warnings.

### 3.3 `BanditAnalyzer` (`apps/analyzer/bandit_analyzer.py`)
Scans AST nodes for security risks:
- **`B105` (Hardcoded Credentials):** Uses regex to inspect variable assignments (e.g. `API_KEY = "sk-live-..."` or `password = "..."`). Flags a `CRITICAL` or `HIGH` security vulnerability.
- **`B307` (Dangerous `eval()`):** Flags `eval()` calls. `eval()` executes arbitrary strings as Python code, enabling remote code execution. Flags a `HIGH` security vulnerability.
- **`B602` (Shell Injection):** Flags unsafe system calls like `os.system("echo " + user_input)` or `exec()`. Command strings concatenated with user input allow attackers to append shell commands. Flags a `CRITICAL` vulnerability.
- **`B110` (Bare `except:` Clauses):** Flags `except:` statements without a specific exception class. Bare excepts catch system exit signals and hide critical errors. Flags a `HIGH` finding.

### 3.4 `RadonAnalyzer` (`apps/analyzer/radon_analyzer.py`)
Computes mathematical complexity metrics:
- **Cyclomatic Complexity (CC):** Counts the number of independent decision paths through a function (if statements, for loops, while loops, logical AND/OR operators).
  - Complexity 1 to 5: Rank A (Low risk, clean)
  - Complexity 6 to 10: Rank B (Low risk)
  - Complexity 11 to 20: Rank C (Moderate risk)
  - Complexity 21 to 30: Rank D (High risk)
  - Complexity 31 to 40: Rank E (Very high risk)
  - Complexity 41+: Rank F (Unmaintainable code)
- **Maintainability Index (MI):** Calculates a maintainability index score from 0 to 100 using Halstead volume and line counts.

### 3.5 `RuffAnalyzer` (`apps/analyzer/ruff_analyzer.py`)
Enforces Python PEP 8 style guidelines:
- **`F401`:** Unused import statements (e.g. `import os` when `os` is never used).
- **`F403`:** Wildcard imports (`from module import *`), which pollute the namespace and make imports unpredictable.
- **Line Length:** Flags lines exceeding standard line lengths (88/120 chars).

### 3.6 `UniversalAIAnalyzer` (`apps/analyzer/universal_analyzer.py`)
Provides full analysis and refactoring for 15+ non-Python languages:
- **Languages:** JavaScript, TypeScript, Java, C/C++, Go, Rust, PHP, Ruby, SQL, HTML, CSS.
- **Security Vulnerability Rules:**
  - `SEC01` (Hardcoded Credentials): Detects hardcoded keys, passwords, and tokens across JS, Java, C++, Go, and SQL.
  - `SEC02` (Dangerous Dynamic Evaluation): Detects `eval()`, `exec()`, and `Function()` in JS/Java.
  - `XSS01` (DOM-based XSS): Detects direct assignments to `innerHTML` or `document.write()`.
  - `SQL01` (SQL Injection): Detects unparameterized string concatenation in SQL queries (`"SELECT * FROM users WHERE id = " + id`).
  - `MEM01` (C/C++ Buffer Overflow): Detects unbounded string functions (`strcpy`, `strcat`, `gets`).

### 3.7 `QualityScorer` (`apps/analyzer/scoring.py`)
Calculates the numerical Quality Score out of 100.0 points.
- **Formula:**
  $$\text{Score} = \max\left(0, 100.0 - \text{Total Deductions}\right)$$
- **Severity Penalty Table:**
  - `CRITICAL`: $-15.0$ points per issue
  - `HIGH`: $-10.0$ points per issue
  - `MEDIUM`: $-5.0$ points per issue
  - `LOW`: $-2.0$ points per issue
  - `INFO`: $0.0$ points
- **Grade Scale:**
  - **Grade A:** 90.0 to 100.0 (Excellent quality)
  - **Grade B:** 80.0 to 89.9 (Good quality)
  - **Grade C:** 70.0 to 79.9 (Acceptable)
  - **Grade D:** 60.0 to 69.9 (Needs improvement)
  - **Grade F:** Below 60.0 (Severe vulnerabilities or complexity)

---

## 4. The Score Monotonicity Guard Algorithm

### The Problem it Solves
In generative AI code refactoring, LLMs sometimes add unnecessary imports (like `import os`) or add extra comments that cause linters to flag new warnings. This previously caused scores to drop from 95.0 to 82.0 on clean code.

### How the Guard Works
Inside `ReviewEngine.run_review()`:
```python
# 1. Calculate score of raw original code
raw_score = score_res['quality_score']

# 2. Evaluate quality score of the suggested refactored code
suggested_score = self._calculate_quick_score(suggested_code, enabled_analyzers)

# 3. If suggested code score is LESS than raw original score:
if suggested_score < raw_score:
    # Generate syntax-cleaned refactored code without extra imports
    guaranteed_code = self.gemini_analyzer.generate_guaranteed_refactor(code)
    guaranteed_score = self._calculate_quick_score(guaranteed_code, enabled_analyzers)
    
    if guaranteed_score >= raw_score:
        suggested_code = guaranteed_code
    else:
        # Keep raw code if it already has higher score!
        suggested_code = code
```
This mathematically guarantees:
$$\text{Score}_{\text{new}} \ge \text{Score}_{\text{old}}$$
Applying AI fixes **will never lower your score**.

---

## 5. Polyglot Security & AI Refactoring Engine

`UniversalAIAnalyzer.generate_polyglot_refactor()` automatically refactors code line-by-line across all languages:

1. **Hardcoded Secrets:**
   - **Original:** `const API_KEY = "sk-live-12345";`
   - **Refactored:** `const API_KEY = process.env.API_KEY || ""; // Refactored secret`
   - **Java Original:** `String secret = "Secret123";`
   - **Java Refactored:** `String secret = System.getenv("SECRET"); // Refactored secret`

2. **Dynamic Evaluation (`eval`):**
   - **JS Original:** `const data = eval(req.query.data);`
   - **JS Refactored:** `const data = JSON.parse(req.query.data); // Refactored eval call`

3. **DOM XSS Vulnerabilities:**
   - **JS Original:** `elem.innerHTML = userInput;`
   - **JS Refactored:** `elem.textContent = userInput; // Security Fix: Replaced innerHTML with textContent`
   - **JS Original:** `document.write(userInput);`
   - **JS Refactored:** `// Security Fix: Removed dangerous document.write call`

4. **SQL Injection Concatenation:**
   - **Original:** `const sql = "SELECT * FROM users WHERE id = " + id;`
   - **Refactored:** `// Security Fix: Converted raw query to parameterized query`  
     `const sql = "SELECT * FROM users WHERE id = ?";`

5. **C/C++ Buffer Overflow:**
   - **Original:** `strcpy(buffer, input);`
   - **Refactored:** `strncpy(buffer, input, sizeof(buffer) - 1); // Security Fix: Safe bounded copy`
   - **Original:** `gets(buffer);`
   - **Refactored:** `fgets(buffer, sizeof(buffer), stdin); // Security Fix: Safe bounded input`

---

## 6. Database Schema & Django Models

The application uses three primary Django ORM models:

### 6.1 `Project` Model (`apps/projects/models.py`)
- `id` (`AutoField`): Primary key.
- `owner` (`ForeignKey -> User`): The user who owns this project.
- `name` (`CharField`, max_length=255): Project name.
- `description` (`TextField`, blank=True): Description of project.
- `repository_url` (`URLField`, blank=True): Linked GitHub repository URL (e.g. `https://github.com/pallets/flask`).
- `language` (`CharField`, default='Python'): Primary programming language.
- `created_at` / `updated_at` (`DateTimeField`): Auto timestamps.

### 6.2 `CodeReview` Model (`apps/reviews/models.py`)
- `id` (`AutoField`): Primary key.
- `project` (`ForeignKey -> Project`): Related project.
- `user` (`ForeignKey -> User`): Developer who ran the review.
- `filename` (`CharField`): Name of analyzed file (e.g. `server.js`, `main.py`).
- `version` (`IntegerField`): Version counter (v1, v2, v3...).
- `raw_code` (`TextField`): Original source code analyzed.
- `quality_score` (`FloatField`): Numerical score (0.0 to 100.0).
- `letter_grade` (`CharField`): Grade ('A', 'B', 'C', 'D', 'F').
- `summary` (`TextField`): Gemini AI summary text.
- `suggested_code` (`TextField`): AI refactored code output.
- `metrics_json` (`JSONField`): JSON object storing lines of code and severity counts.
- `created_at` (`DateTimeField`).

### 6.3 `Finding` Model (`apps/reviews/models.py`)
- `id` (`AutoField`): Primary key.
- `review` (`ForeignKey -> CodeReview`): Related CodeReview run.
- `analyzer` (`CharField`): Engine name (`AST`, `BANDIT`, `RADON`, `RUFF`, `GEMINI`, `SECURITY_SCANNER`).
- `category` (`CharField`): `SECURITY`, `COMPLEXITY`, `STYLE`, `BUG_RISK`, `DOCUMENTATION`.
- `severity` (`CharField`): `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`.
- `line_number` (`IntegerField`): Line number where issue occurs.
- `code_snippet` (`TextField`): Problematic line snippet.
- `title` (`CharField`): Short title.
- `message` (`TextField`): Detailed explanation of error.
- `recommendation` (`TextField`): How to fix advice.
- `rule_id` (`CharField`): Unique rule ID (e.g. `B105`, `SEC01`).

---

## 7. Authentication Architecture & Fallback Mechanism

`FlexibleJWTAuthentication` (`apps/authentication/auth.py`) implements a hybrid authentication model:

```python
class FlexibleJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, AuthenticationFailed):
            # Catches stale/invalid tokens and returns None,
            # allowing Django Session authentication to authenticate seamlessly!
            return None
```

- **Why it matters:** Standard JWT authenticators throw a `401 Unauthorized` error if an expired or invalid token header is sent. `FlexibleJWTAuthentication` catches expired tokens and allows Django's session cookie to authenticate the user smoothly, eliminating token error crashes.

---

## 8. GitHub Repository Integration Engine

`GitHubFetcher` (`apps/reviews/github.py`) connects to GitHub's API:
- **Direct File Retrieval:** Parses blob URLs (`https://github.com/owner/repo/blob/main/path/to/file.py`) and fetches raw content from `raw.githubusercontent.com`.
- **Recursive Tree Scanner:** Calls `https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1` to find all code files (`.py`, `.js`, `.ts`, `.java`, `.cpp`, `.go`, `.rs`, `.php`, `.sql`, `.html`, `.css`).
- **Full Repository Audit Endpoint (`/api/reviews/audit_repo/`):** Fetches Python/code files in a repository, executes reviews across all files, aggregates scores, and generates a **Full Repository Quality Audit Report**.

---

## 9. Interactive Code Studio & Frontend Architecture

The **Interactive Code Studio** (`templates/review_studio.html`) provides a split-screen workspace:
- **Left Column:** Live Python/Polyglot Code Editor with line counter.
- **Right Column:** Code Health Inspector displaying Quality Score badge, line numbers, WHAT is wrong, WHERE it is, and HOW to fix it.
- **Action Buttons:**
  - **`Load Sample Code` Dropdown:** Pick pre-configured sample code for JavaScript, Python, Java, C++, TypeScript, or SQL.
  - **`Select File from Repository` Dropdown:** Automatically lists files from the active project's GitHub repository.
  - **`⚡ Re-Analyze Code`:** Calls `/api/reviews/analyze_instant/` to re-evaluate edited code live.
  - **`🤖 Apply Full AI Fix`:** Replaces editor content with refactored AI code.

---

## 10. Complete REST API Reference Manual

### 10.1 Login API
- **Endpoint:** `POST /api/auth/login/`
- **Request Body:** `{"username": "demo", "password": "demo12345"}`
- **Response:** `200 OK`
  ```json
  {
    "user": {"id": 1, "username": "demo", "email": "demo@codeguardian.ai"},
    "tokens": {"access": "<jwt_access_token>", "refresh": "<jwt_refresh_token>"}
  }
  ```

### 10.2 Register API
- **Endpoint:** `POST /api/auth/register/`
- **Request Body:** `{"username": "newuser", "email": "user@example.com", "password": "password123"}`
- **Response:** `201 Created`

### 10.3 Create Project API
- **Endpoint:** `POST /api/projects/`
- **Request Body:** `{"name": "Payment Service", "description": "Backend API", "repository_url": "https://github.com/pallets/flask"}`
- **Response:** `201 Created`

### 10.4 Instant Live Analysis API
- **Endpoint:** `POST /api/reviews/analyze_instant/`
- **Request Body:** `{"code": "<source_code>", "filename": "server.js", "project_id": 1}`
- **Response:** `200 OK`
  ```json
  {
    "quality_score": 90.0,
    "letter_grade": "A",
    "summary": "Multi-language analysis completed.",
    "suggested_code": "<refactored_code>",
    "findings": [...]
  }
  ```

### 10.5 GitHub Repository Fetch API
- **Endpoint:** `POST /api/reviews/fetch_github/`
- **Request Body:** `{"repo_url": "https://github.com/django/django", "file_path": "django/__init__.py"}`
- **Response:** `200 OK`

### 10.6 Audit Full Repository API
- **Endpoint:** `POST /api/reviews/audit_repo/`
- **Request Body:** `{"project_id": 1}`
- **Response:** `201 Created`

### 10.7 Version Comparison API
- **Endpoint:** `GET /api/reviews/compare/?review1=1&review2=2`
- **Response:** `200 OK`
  ```json
  {
    "score_delta": 36.0,
    "resolved_count": 7,
    "new_count": 0,
    "resolved_findings": [...]
  }
  ```

---

*End of Technical Documentation. CodeGuardian AI is fully tested, verified, and operational.*
