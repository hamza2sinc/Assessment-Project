# app/schemas/task.py
from pydantic import BaseModel, validator
from datetime import datetime
from enum import Enum
from typing import Optional

# Define the TaskStatus enum with explicit members
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# Define the TaskPriority enum with explicit members
class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING  # Use the enum member directly
    priority: TaskPriority = TaskPriority.MEDIUM  # Use the enum member directly
    category: Optional[str] = None
    due_date: Optional[datetime] = None

    @validator('due_date')
    def due_date_must_be_future(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Due date cannot be in the past')
        return v

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    category: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskResponse(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True