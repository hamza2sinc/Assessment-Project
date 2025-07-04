# Assessment-Project: Task Management API Documentation


## Overview
The Task Management API is a FastAPI-based application designed to manage user tasks with features like registration, authentication, CRUD operations, task categorization, filtering, and basic analytics. Built with Python 3.10+, it uses SQLAlchemy with SQLite for database management, Pydantic for validation, and JWT for authentication.

## Features
- **User Registration and Authentication**: Secure user signup and login with JWT tokens.
- **Task CRUD Operations**: Create, read, update, and delete tasks with filtering and pagination.
- **Task Categorization and Filtering**: Organize and filter tasks by status, priority, and category.
- **Basic Analytics**: Endpoint to retrieve task statistics (e.g., completion rate, overdue tasks).
- **Error Handling and Validation**: Robust validation and meaningful error messages.
- **API Documentation**: Interactive docs via FastAPI's Swagger UI.

## Technical Requirements
- **Python**: 3.10+
- **Dependencies**:
  - `fastapi==0.104.1`
  - `uvicorn==0.24.0`
  - `sqlalchemy==2.0.23`
  - `alembic==1.12.1` (optional for migrations)
  - `pydantic==2.5.0`
  - `python-jose[cryptography]==3.3.0`
  - `passlib[bcrypt]==1.7.4`
  - `python-multipart==0.0.6`
  - `pytest==7.4.3`
  - `pytest-asyncio==0.21.1`
  - `python-dotenv==1.0.0`
- **Database**: SQLite (`task_management.db`)
- **Testing**: Pytest with 80%+ coverage target

## Project Structure
```
task_management_api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── tasks.py
│   │       └── analytics.py
│   └── services/
│       ├── __init__.py
│       ├── user_service.py
│       └── task_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_tasks.py
│   └── test_analytics.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── run.py
```

## Installation

### Prerequisites
- Python 3.10+ installed
- Git installed

### Steps
1. **Clone the Repository**:
   ```
   git clone https://github.com/hamza2sinc/Assessment-Project.git
   cd task_management_api
   ```

2. **Set Up Virtual Environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   - Copy `.env.example` to `.env`:
     ```
     cp .env.example .env
     ```
   - Edit `.env` with your values:
     ```
     SECRET_KEY=your-secret-key-here
     ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     DATABASE_URL=sqlite:///./task_management.db
     ```

5. **Initialize Database**:
   - Run: python init_db.py
     once to create the database
     ```
     uvicorn app.main:app --reload --port 8000
     ```
   - Stop the server (`Ctrl+C`) after the database is initialized.

6. **Run the Application**:
   ```
   uvicorn app.main:app --reload --port 8000
   ```

7. **Run Tests**:
   ```
   pytest -v
   pytest --cov=app --cov-report=html
   ```

## API Endpoints

### Authentication Endpoints
- **POST /auth/register**
  - **Description**: Register a new user.
  - **Request**:
    ```json
    {
      "email": "user@example.com",
      "username": "username",
      "password": "password123"
    }
    ```
  - **Response (200)**:
    ```json
    {
      "message": "User registered successfully",
      "id": 1,
      "email": "user@example.com"
    }
    ```
  - **Response (400)**: `{"detail": "Email or username already registered"}`

- **POST /auth/login**
  - **Description**: Log in and get a JWT token.
  - **Request**:
    ```json
    {
      "username": "username",
      "password": "password123"
    }
    ```
  - **Response (200)**:
    ```json
    {
      "access_token": "your-jwt-token-here",
      "token_type": "bearer",
      "message": "Login successful"
    }
    ```
  - **Response (400)**: `{"detail": "Incorrect username or password"}`

- **POST /auth/refresh**
  - **Description**: Refresh the JWT token (not implemented yet, returns 501).
  - **Response (501)**: `{"detail": "Not implemented"}`

### User Endpoints
- **GET /users/me**
  - **Description**: Get current user profile (requires authentication).
  - **Request Headers**: `Authorization: Bearer <token>`
  - **Response (200)**:
    ```json
    {
      "id": 1,
      "email": "user@example.com",
      "username": "username",
      "full_name": null,
      "is_active": true,
      "created_at": "2025-07-04T06:33:00",
      "updated_at": null
    }
    ```
  - **Response (401)**: `{"detail": "Token required"}`

- **PUT /users/me**
  - **Description**: Update current user profile (requires authentication).
  - **Request Headers**: `Authorization: Bearer <token>`
  - **Request**:
    ```json
    {
      "email": "newemail@example.com",
      "full_name": "New Name"
    }
    ```
  - **Response (200)**:
    ```json
    {
      "message": "User updated",
      "id": 1,
      "email": "newemail@example.com",
      "username": "username"
    }
    ```
  - **Response (401)**: `{"detail": "Token required"}`

### Task Endpoints
- **GET /tasks/**
  - **Description**: Get user's tasks with filtering and pagination.
  - **Query Parameters**:
    - `status`: Filter by status (e.g., `pending`)
    - `priority`: Filter by priority (e.g., `high`)
    - `category`: Filter by category (e.g., `work`)
    - `page`: Page number (default: 1)
    - `per_page`: Items per page (default: 10)
  - **Request Headers**: `Authorization: Bearer <token>`
  - **Response (200)**:
    ```json
    [
      {
        "id": 1,
        "title": "Test Task",
        "description": "Test Description",
        "status": "pending",
        "priority": "medium",
        "category": "work",
        "due_date": "2025-07-05T12:00:00",
        "user_id": 1,
        "created_at": "2025-07-04T06:33:00",
        "updated_at": null
      }
    ]
    ```
  - **Response (401)**: `{"detail": "Token required"}`

- **POST /tasks/**
  - **Description**: Create a new task.
  - **Request Headers**: `Authorization: Bearer <token>`
  - **Request**:
    ```json
    {
      "title": "New Task",
      "description": "Task Description",
      "status": "pending",
      "priority": "medium",
      "category": "work",
      "due_date": "2025-07-05T12:00:00"
    }
    ```
  - **Response (200)**:
    ```json
    {
      "message": "Task created",
      "task_id": 1
    }
    ```
  - **Response (400)**: `{"detail": "Due date cannot be in the past"}`

- **GET /tasks/{task_id}**
  - **Description**: Get a specific task.
  - **Request Headers**: `Authorization: Bearer <token>`
  - **Response (200)**:
    ```json
    {
      "id": 1,
      "title": "Test Task",
      "description": "Test Description",
      "status": "pending",
      "priority": "medium",
      "category": "work",
      "due_date": "2025-07-05T12:00:00",
      "user_id": 1,
      "created_at": "2025-07-04T06:33:00",
      "updated_at": null
    }
    ```
  - **Response (404)**: `{"detail": "Task not found"}`

- **PUT /tasks/{task_id}**
  - **Description**: Update a task.
  - **Request Headers**: `Authorization: Bearer <token>`
  - **Request**:
    ```json
    {
      "title": "Updated Task",
      "status": "completed"
    }
    ```
  - **Response (200)**:
    ```json
    {
      "message": "Task updated",
      "task_id": 1
    }
    ```
  - **Response (404)**: `{"detail": "Task not found"}`

- **DELETE /tasks/{task_id}**
  - **Description**: Delete a task.
  - **Request Headers**: `Authorization: Bearer <token>`
  - **Response (200)**:
    ```json
    {
      "message": "Task deleted"
    }
    ```
  - **Response (404)**: `{"detail": "Task not found"}`

- **PATCH /tasks/{task_id}/status**
  - **Description**: Update task status.
  - **Request Headers**: `Authorization: Bearer <token>`
  - **Request**:
    ```json
    {
      "status": "completed"
    }
    ```
  - **Response (200)**:
    ```json
    {
      "message": "Task status updated",
      "task_id": 1
    }
    ```
  - **Response (404)**: `{"detail": "Task not found"}`

### Analytics Endpoint
- **GET /analytics/dashboard**
  - **Description**: Get user's task analytics.
  - **Request Headers**: `Authorization: Bearer <token>`
  - **Response (200)**:
    ```json
    {
      "total_tasks": 25,
      "completed_tasks": 15,
      "pending_tasks": 5,
      "in_progress_tasks": 5,
      "tasks_by_priority": {
        "high": 8,
        "medium": 12,
        "low": 5
      },
      "completion_rate": 60.0,
      "overdue_tasks": 2
    }
    ```
  - **Response (401)**: `{"detail": "Token required"}`

## Usage
1. **Access API Documentation**:
   - Open `http://127.0.0.1:8000/docs` in a browser after starting the server to explore the interactive Swagger UI.

2. **Register a User**:
   - Use the `/auth/register` endpoint to create a new user account.

3. **Log In**:
   - Use the `/auth/login` endpoint to obtain a JWT token.

4. **Manage Tasks**:
   - Use the task endpoints with the token in the `Authorization` header to create, read, update, and delete tasks.

5. **View Analytics**:
   - Access `/analytics/dashboard` with a valid token to see task statistics.

## Testing
- Run `pytest -v` to execute tests.
- Run `pytest --cov=app --cov-report=html` to generate a coverage report in `htmlcov/`.

## Contributing
- Follow the Git workflow:
  - Use `develop` for integration.
  - Create `feature/*` branches.
  - Commit with `type(scope): description` format.
- Submit pull requests to `develop`.

## License
 - MIT