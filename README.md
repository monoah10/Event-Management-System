🎯 Event Management API – Django (GUI) + FastAPI (Backend)

A full-stack Event Management System built with Django for the frontend admin panel and FastAPI for the backend API services. This hybrid architecture provides a robust and interactive user experience while ensuring high-performance API handling.

🗂️ Project Structure

EventManagementApi/
│
├── admin_panel/           # Django GUI/Admin
│   ├── admin_panel/       # Django config (settings, urls, wsgi)
│   └── events/            # Django app (forms, models, views, templates)
│
├── backend/               # FastAPI backend logic
│   ├── migrations/        # Alembic migrations
│   ├── routes/            # API endpoints (auth, events, etc.)
│   ├── database.py        # DB connection logic
│   ├── main.py            # FastAPI entry point
│   ├── models.py          # SQLAlchemy models
│   └── schemas.py         # Pydantic schemas
│
├── api_documentation.md   # Full API reference (Markdown)
├── openapi.json           # FastAPI OpenAPI schema (generated)
├── requirements.txt       # Dependencies
├── env.example            # Example .env file
└── Unified_Event_&_User_Management_API.json # Postman collection

⚙️ Features

✅ Django (Admin Panel)

Clean GUI for managing events, users, and permissions

Secure authentication and user management

Supports templates for UI rendering

⚡ FastAPI (Backend API)

JWT-based authentication system

User registration, login, event creation, update, deletion

Swagger/OpenAPI documentation out-of-the-box

Clean RESTful design and modular routing

🚀 Quick Start

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Backend – FastAPI
cd backend
uvicorn main:app --reload
Access API Docs at:
Swagger: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

OPEN NEW TERMINAL Frontend – Django Admin Panel
cd admin_panel
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

Visit the admin GUI at:http://localhost:8080/admin
Visit the Event GUI at:http://localhost:8080/ ,
Visit the Event Login GUI at:http://127.0.0.1:8080/login/ ,


🧪 API Documentation

Markdown Docs: api_documentation.md
OpenAPI Spec: openapi.json
Postman Collection: Unified_Event_&_User_Management_API.json

🛠️ Tech Stack
Backend: FastAPI, SQLAlchemy, Pydantic
Frontend: Django 4+, HTML/CSS (Bootstrap for templates)
Database: MySQL
Auth: JWT (OAuth2 password flow)
Docs: Swagger, ReDoc

👨‍💻 Author
Khan Mohammad Kashif ~~ Software Developer | Python Enthusiast | API Integrator

🤝 Contributions
Open to issues, feedback, and PRs to improve and extend the system 🙌

📄 License
This project is licensed under the MIT License.