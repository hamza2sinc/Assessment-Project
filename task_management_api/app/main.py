# app/main.py
import logging
import os
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, Form, Security, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import List

from dotenv import load_dotenv
from app.core.database import get_db, engine
from app.models.user import User
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

# ──────────────────────────────────────────────────────────────

load_dotenv()

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT config
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# OAuth2 Scopes
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    scopes={
        "me": "Read your user info",
        "tasks": "Access your tasks"
    },
)

# ──────────────────────────────────────────────────────────────

# Get current user based on token and required scopes
async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_scopes = payload.get("scopes", [])
        if username is None:
            raise credentials_exception
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user

# ──────────────────────────────────────────────────────────────
# Auth Routes

@app.post("/register")
def register(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter((User.email == email) | (User.username == username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    hashed_password = pwd_context.hash(password)
    new_user = User(email=email, username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "id": new_user.id, "email": new_user.email}

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    scopes = form_data.scopes or ["me", "tasks"]

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user.username,
        "scopes": scopes,
        "exp": expire
    }
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected")
def protected_route(current_user: User = Security(get_current_user, scopes=["me"])):
    return {"message": f"Welcome {current_user.username}, you're authenticated!"}

# ──────────────────────────────────────────────────────────────
# Task CRUD (authenticated)

@app.get("/tasks/", response_model=List[dict])
def read_tasks(
    current_user: User = Security(get_current_user, scopes=["tasks"]),
    db: Session = Depends(get_db)
):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description or "",
            "status": task.status,
            "priority": task.priority,
            "category": task.category or "",
            "due_date": task.due_date.isoformat() if task.due_date else "",
            "user_id": task.user_id,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat() if task.updated_at else ""
        }
        for task in tasks
    ]

@app.post("/tasks/", response_model=dict)
def create_task(
    task: TaskCreate,
    current_user: User = Security(get_current_user, scopes=["tasks"]),
    db: Session = Depends(get_db)
):
    db_task = Task(**task.dict(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return {"message": "Task created", "task_id": db_task.id}

@app.put("/tasks/{task_id}", response_model=dict)
def update_task(
    task_id: int,
    task: TaskUpdate,
    current_user: User = Security(get_current_user, scopes=["tasks"]),
    db: Session = Depends(get_db)
):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found or unauthorized")
    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return {"message": "Task updated", "task_id": db_task.id}

@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(
    task_id: int,
    current_user: User = Security(get_current_user, scopes=["tasks"]),
    db: Session = Depends(get_db)
):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found or unauthorized")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted"}

# ──────────────────────────────────────────────────────────────
# Optional UI endpoints (can remove in API-only)

@app.get("/register", response_class=HTMLResponse)
def register_form():
    with open("app/static/register.html", "r") as file:
        return HTMLResponse(content=file.read())

@app.get("/login", response_class=HTMLResponse)
def login_form():
    with open("app/static/login.html", "r") as file:
        return HTMLResponse(content=file.read())

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard():
    with open("app/static/dashboard.html", "r") as f:
        return f.read()
