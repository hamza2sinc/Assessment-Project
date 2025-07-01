# app/models/task.py
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum("pending", "in_progress", "completed", name="task_status"), nullable=False)
    priority = Column(Enum("low", "medium", "high", name="task_priority"), nullable=False)
    category = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to User (optional, for querying)
    user = relationship("User", back_populates="tasks")