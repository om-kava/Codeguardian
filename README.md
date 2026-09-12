<div align="center">
  <img src="https://img.icons8.com/color/96/000000/shield.png" alt="CodeGuardian Shield"/>
  <h1>CodeGuardian AI</h1>
  <p><strong>Intelligent, Automated Code Review & Security Analysis Platform</strong></p>
  
  [![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
  [![Django](https://img.shields.io/badge/Django-5.0-092E20.svg)](https://djangoproject.com)
  [![MySQL](https://img.shields.io/badge/Database-MySQL_&_SQLite-00758F.svg)](https://mysql.com)
  [![AI](https://img.shields.io/badge/AI-OpenRouter_&_Gemini-success.svg)](https://openrouter.ai/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

---

## 🌟 Overview
**CodeGuardian AI** is an advanced software engineering platform that acts as your automated first-level code reviewer. By combining lightning-fast deterministic static analysis with deep AI reasoning, CodeGuardian identifies security vulnerabilities, code smells, and performance bottlenecks *before* they reach human review.

## 🚀 Key Features

* **🛡️ Polyglot Support**: Analyze Python, JavaScript, TypeScript, Java, C++, Go, Rust, PHP, SQL, and HTML.
* **🧠 Dual-Engine Analysis**: Uses both strict static analysis tools (Bandit, Radon, Ruff) and AI models for contextual insights.
* **📊 Visual Dashboards**: Real-time metrics on your code health, quality scores, and maintainability via Chart.js.
* **🌐 GitHub Integration**: Directly fetch and analyze files from public GitHub repositories.
* **🤖 One-Click AI Fixes**: Automatically refactor vulnerable or messy code with AI-generated solutions.
* **📱 Mobile Responsive**: Carefully crafted, aesthetic UI that works flawlessly on desktop and mobile.

## 🏗️ Architecture & Tech Stack

CodeGuardian relies on a robust and modular architecture:

* **Backend**: Python 3.13, Django 5.0, Django REST Framework, JWT Authentication
* **Database**: MySQL (Production & Local relational database) with pure-Python PyMySQL driver and SQLite fallback
* **Frontend**: HTML5, Vanilla CSS (Custom Glassmorphic Design System), JavaScript, Bootstrap 5
* **Static Analysis**: Python AST, Bandit (Security AST), Radon (Cyclomatic Complexity & Maintainability Index), Ruff rules
* **AI Engine**: OpenRouter API (Gemini & DeepSeek LLM reasoning with automated suggested fixes)

## 💻 Local Setup & Installation

Follow these steps to run CodeGuardian locally on your machine.

1. **Clone the Repository**
   ```bash
   git clone https://github.com/om-kava/Codeguardian.git
   cd Codeguardian
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory based on `.env.example`:
   ```env
   SECRET_KEY=your_secure_random_key
   DEBUG=True
   OPENROUTER_API_KEY=your_openrouter_key
   
   # Database Settings (Defaults to MySQL locally)
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=codeguardian
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```

5. **Database Migration**
   ```bash
   python manage.py migrate
   ```

6. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```
   *Visit `http://127.0.0.1:8000` in your browser.*

## ☁️ Cloud Deployment (Render)

CodeGuardian is pre-configured to deploy seamlessly to [Render](https://render.com/). 

1. Go to your Render Dashboard and create a **New Blueprint**.
2. Connect your fork of this repository.
3. Render will automatically read the `render.yaml` file, provision the server and persistent database disk, and prompt you for your `OPENROUTER_API_KEY`.
4. Click **Apply**! Your app will be live in minutes.

## 🔒 Security

* **No Code Execution**: User-submitted code is strictly parsed (AST) and analyzed; it is never executed (`eval()` or `exec()`).
* **Secure Cookies**: In production, the app enforces HTTPS, strict HSTS, and secure flags for CSRF/Session cookies.
* **Password Hashing**: Django's robust `PBKDF2` hashing algorithm protects user accounts.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
<div align="center">
  <b>Built with ❤️ by Om Kava</b>
</div>
