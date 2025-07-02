# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from app.core.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import os

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        return {"message": "User registered successfully", "id": new_user.id, "email": new_user.email}
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