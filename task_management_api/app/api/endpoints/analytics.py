# app/api/endpoints/analytics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.task import Task
from sqlalchemy import func
from app.models.task import Task, TaskStatus, TaskPriority


router = APIRouter()

@router.get("/dashboard")
def get_analytics(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_tasks = db.query(Task).filter(Task.user_id == 1).all()  # Placeholder user_id
    total_tasks = len(user_tasks)
    completed_tasks = len([t for t in user_tasks if t.status == TaskStatus.COMPLETED])
    pending_tasks = len([t for t in user_tasks if t.status == TaskStatus.PENDING])
    in_progress_tasks = len([t for t in user_tasks if t.status == TaskStatus.IN_PROGRESS])
    tasks_by_priority = {
        "high": len([t for t in user_tasks if t.priority == TaskPriority.HIGH]),
        "medium": len([t for t in user_tasks if t.priority == TaskPriority.MEDIUM]),
        "low": len([t for t in user_tasks if t.priority == TaskPriority.LOW])
    }
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    overdue_tasks = len([t for t in user_tasks if t.due_date and t.due_date < func.now() and t.status != TaskStatus.COMPLETED])

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks,
        "tasks_by_priority": tasks_by_priority,
        "completion_rate": round(completion_rate, 1),
        "overdue_tasks": overdue_tasks
    }