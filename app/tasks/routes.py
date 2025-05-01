from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
from .models import Task, TaskCategory, TaskSkillLevel, TaskStatus
from .schemas import TaskCreate, TaskUpdate, TaskResponse
from app.auth.models import User, UserType

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def validate_budget(budget_min: float | None, budget_max: float | None):
    if budget_min is not None and budget_max is not None:
        if budget_min > budget_max:
            raise ValueError("Минимальный бюджет не может быть больше максимального")
    return True


# Создание задачи
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Только заказчики могут создавать задачи")

    try:
        validate_budget(task_data.budget_min, task_data.budget_max)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if task_data.category == "Другое" and not task_data.custom_category:
        raise HTTPException(status_code=400, detail="Необходимо указать 'custom_category' при категории 'Другое'")

    # Преобразуем строковые значения в enum
    try:
        category = TaskCategory(task_data.category)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Некорректное значение категории: {task_data.category}")

    try:
        skill_level = TaskSkillLevel(task_data.skill_level)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Некорректный уровень навыка: {task_data.skill_level}")

    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        budget_min=task_data.budget_min,
        budget_max=task_data.budget_max,
        deadline=task_data.deadline,
        category=category,
        custom_category=task_data.custom_category,
        skill_level=skill_level,
        owner_id=current_user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return TaskResponse.model_validate(new_task.__dict__)


# Получить все свои задачи
@router.get("/", response_model=list[TaskResponse])
async def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Только заказчики могут просматривать задачи")

    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()
    return [TaskResponse.model_validate(task.__dict__) for task in tasks]


# Получить одну задачу по ID
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Только заказчики могут просматривать задачи")

    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return TaskResponse.model_validate(task.__dict__)


# Обновить задачу по ID
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Только заказчики могут изменять задачи")

    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # Оставляем только поле description
    update_data = task_data.dict(exclude_unset=True)

    # Проверяем, что в update_data только 'description'
    allowed_fields = {"description"}
    for key in update_data.keys():
        if key not in allowed_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Изменение поля '{key}' запрещено через этот эндпоинт"
            )

    # Обновляем только description
    if "description" in update_data:
        task.description = update_data["description"]

    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task.__dict__)

# Удалить задачу по ID
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Только заказчики могут удалять задачи")

    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    db.delete(task)
    db.commit()

    return {"message": "Задача удалена"}