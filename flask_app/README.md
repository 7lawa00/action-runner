# AutoFlow Pro (Flask) - Local Web Automation Tool

This is a Windows-friendly, zip-ready Flask application that replicates a simplified Postman with extras: HTTP Requests, Scenarios, Environments, Snippets, Trello integration (with fallback), and Selenium actions.

Quick start on Windows 11 (no Docker):

1) Install Python 3.10+ and PostgreSQL 14+
   - Ensure PostgreSQL service is running
   - Create database and user (example):
     - DB name: automation_db
     - User: postgres
     - Password: postgres

2) Create and activate a virtual environment:
   - python -m venv .venv
   - .venv\\Scripts\\activate

3) Install dependencies:
   - pip install -r requirements.txt

4) Configure database (optional):
   - By default it uses: postgresql://postgres:postgres@localhost:5432/automation_db
   - To change it, set env var:
     - set DATABASE_URL=postgresql://USER:PASS@HOST:PORT/DB

5) Run the app:
   - python run.py
   - Open http://127.0.0.1:5050

6) Optional: Trello keys
   - set TRELLO_API_KEY=your_key
   - set TRELLO_TOKEN=your_token

Selenium Demo Notes:
- Requires Google Chrome. The driver is auto-installed via webdriver-manager on first run.

Pack to zip (PowerShell):
- powershell -ExecutionPolicy Bypass -File .\\pack.ps1

Structure:
- run.py (entrypoint)
- app/ (Flask app, models, routes, services, templates, static)
- app/seed.py (loads demo data into Postgres on first run)
- requirements.txt
- USER_MANUAL.md (feature guide for non-technical users)
