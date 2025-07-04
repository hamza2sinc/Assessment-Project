# run.py
from app.core.database import Base, engine
from app import models  # This will load __init__.py and bring in both User and Task
from app.models.user import User
from app.models.task import Task

print("Engine:", engine)  # Debug: Check if engine is created
print("Base metadata:", Base.metadata.tables)  # Debug: Check registered tables

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Creating tables...")
    print("Tables after creation:", Base.metadata.tables.keys())  # Debug: List tables
    print("Database tables created!")

if __name__ == "__main__":
    init_db()