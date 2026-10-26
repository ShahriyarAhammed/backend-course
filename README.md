# Backend Course API

A REST API built with **FastAPI** and **PostgreSQL**, featuring JWT authentication with refresh tokens, role-based access, database migrations, and file upload.

## Features

- User registration and login with bcrypt password hashing
- JWT access tokens (30 minutes) and refresh tokens (7 days)
- Refresh tokens stored as SHA-256 fingerprints, revocable per device
- Role-based access control (user / admin)
- Ownership checks: users can only edit or delete their own data
- Request validation with Pydantic (field and cross-field validators)
- Centralized error handling and transaction management
- Database migrations with Alembic
- Profile picture upload with type and size checks

## Tech Stack

Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Pydantic, python-jose, passlib

## Setup

1. Clone the repository and create a virtual environment:

        git clone https://github.com/ShahriyarAhammed/backend-course.git
        cd backend-course
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt

2. Create a PostgreSQL database, then create a `.env` file:

        SECRET_KEY=your-long-random-secret
        DATABASE_URL=postgresql://user:password@localhost/dbname

3. Create the uploads folder and apply migrations:

        mkdir uploads
        alembic upgrade head

4. Run the server:

        uvicorn main:app --reload

5. Open the interactive docs at http://127.0.0.1:8000/docs

## Main Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /users | Register a new user |
| POST | /login | Get access and refresh tokens |
| POST | /refresh | Get a new access token |
| POST | /logout | Revoke a refresh token |
| GET | /users/me | Current user profile |
| POST | /users/me/avatar | Upload profile picture |
| PUT/DELETE | /users/{id} | Update or delete own account |
| DELETE | /admin/users/{id} | Admin: delete any user |

## Author

Shahriyar Ahammed

## Live Demo

API docs: https://backend-course-3txb.onrender.com/docs

Note: this runs on a free plan, so the first request after a period of inactivity can take about a minute while the server wakes up.
