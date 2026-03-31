# FastAPI REST API — Django Comparison Project

The same User CRUD + JWT auth API built in FastAPI for direct comparison
with the Django implementation. Built to understand framework trade-offs.

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL 15 via SQLAlchemy ORM
- **Auth:** JWT via python-jose + bcrypt password hashing
- **Server:** Uvicorn (ASGI)
- **Containerization:** Docker + Docker Compose
- **Language:** Python 3.13

## Features

- User registration with bcrypt password hashing
- JWT login via OAuth2 standard (form data, not JSON)
- Protected profile endpoint
- Auto-generated Swagger UI at /docs
- SQLAlchemy ORM with PostgreSQL

## Project Structure

\`\`\`
FastAPI_quickstart/
├── app/
│   ├── main.py         # App entry point, router registration
│   ├── database.py     # SQLAlchemy engine + session setup
│   ├── models.py       # SQLAlchemy ORM models
│   ├── schemas.py      # Pydantic schemas (request/response validation)
│   ├── auth.py         # JWT creation, verification, dependencies
│   └── routers/
│       └── users.py    # User + auth endpoints
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
└── requirements.txt
\`\`\`

## Getting Started

\`\`\`bash
git clone https://github.com/yourusername/FastAPI_quickstart.git
cd FastAPI_quickstart

cp .env.example .env

docker-compose up --build
\`\`\`

Visit **http://localhost:8001/docs** for interactive API documentation.

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/v1/users/register | None | Register new user |
| POST | /api/v1/auth/token | None | Login (form data) |
| GET | /api/v1/users/me | JWT | Get own profile |

## Django vs FastAPI — What I Learned

| | Django + DRF | FastAPI |
|---|---|---|
| ORM | Built-in | SQLAlchemy (separate) |
| Migrations | Built-in | Alembic (separate) |
| Serialization | DRF Serializers | Pydantic schemas |
| API Docs | Manual | Auto Swagger UI |
| Admin Panel | Built-in | None |
| Login format | JSON body | OAuth2 form data |
| Best for | Full apps | Microservices |