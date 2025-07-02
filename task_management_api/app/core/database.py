# app/core/database.pyAdd commentMore actions
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./task_management.db")

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # For SQLite
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for the ORM models
Base = declarative_base()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()