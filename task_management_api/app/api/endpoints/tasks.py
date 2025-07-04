# app/api/endpoints/tasks.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from sqlalchemy import func
from typing import Optional, List 

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Task).filter(Task.user_id == 1)  # Placeholder user_id
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if category:
        query = query.filter(Task.category == category)
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = Task(**task.dict(), user_id=1)  # Placeholder user_id
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == 1).first()  # Placeholder user_id
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == 1).first()  # Placeholder user_id
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
def delete_task(task_id: int, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == 1).first()  # Placeholder user_id
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted"}

@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(task_id: int, status: TaskStatus, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == 1).first()  # Placeholder user_id
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.status = status
    db.commit()
    db.refresh(db_task)
    return db_task