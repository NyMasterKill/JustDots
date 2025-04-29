# tasks/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import Task
from .schemas import TaskCreate, TaskResponse
from auth.dependencies import get_current_user
from database import get_db
from auth.models import User

router = APIRouter()

@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if task.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Недопустимая категория")
    if task.requirements not in REQUIREMENTS:
        raise HTTPException(status_code=400, detail="Недопустимые требования")
    if task.status not in STATUSES:
        raise HTTPException(status_code=400, detail="Недопустимый статус")

    db_task = Task(**task.dict(), owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=list[TaskResponse])
def read_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Задача не найдена или доступ запрещён")
    db.delete(task)
    db.commit()
    return {"message": "Задача удалена"}

@router.put("/{task_id}/update-description")
def update_task_description(
    task_id: int,
    new_description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Задача не найдена или доступ запрещён")
    task.description = new_description
    db.commit()
    db.refresh(task)
    return {"message": "Описание обновлено", "description": task.description}