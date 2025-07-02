# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Form, status
from fastapi.responses import HTMLResponse
from app.core.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # Fallback for safety
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Fallback to default
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))  # Fallback to 30 minutes

# Dependency to get the current user (for protected routes)
def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Token required", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/register")
def register(email: str = Form(...), username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    try:
        # Check if email or username already exists
        existing_user = db.query(User).filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email or username already registered")

        # Hash the password
        hashed_password = pwd_context.hash(password)
        # Create a new user
        new_user = User(email=email, username=username, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully", "id": new_user.id, "email": new_user.email}  # Fixed syntax
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), remember_me: bool = Form(False), db: Session = Depends(get_db)):
    try:
        # Find user by username
        user = db.query(User).filter(User.username == username).first()
        if not user or not pwd_context.verify(password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        # Generate JWT token
        access_token_expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES if not remember_me else 1440)
        access_token = jwt.encode({"sub": user.username, "exp": access_token_expires}, SECRET_KEY, algorithm=ALGORITHM)
        
        return {"access_token": access_token, "token_type": "bearer", "message": "Login successful"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/register", response_class=HTMLResponse)
def register_form():
    with open("app/static/register.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.get("/login", response_class=HTMLResponse)
def login_form():
    with open("app/static/login.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Optional protected route for testing
@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user.username}! This is a protected route."}