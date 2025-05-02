from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.auth.dependencies import get_current_user
from app.database import get_db
from .models import Task, TaskCategory, TaskSkillLevel, TaskStatus, Application, ApplicationStatus
from .schemas import TaskCreate, TaskUpdate, TaskResponse, ApplicationCreate, ApplicationResponse
from app.auth.models import User, UserType
from typing import List, Optional

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def validate_budget(budget_min: float | None, budget_max: float | None):
    if budget_min is not None and budget_max is not None:
        if budget_min > budget_max:
            raise ValueError("Минимальный бюджет не может быть больше максимального")
    return True

# Создание задачи
@router.post("/create", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
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

    if task_data.category == TaskCategory.OTHER.value and not task_data.custom_category:
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

# Получить все свои задачи (для заказчиков)
@router.get("/", response_model=List[TaskResponse])
async def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Только заказчики могут просматривать свои задачи")

    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()
    return [TaskResponse.model_validate(task.__dict__) for task in tasks]

# Получить все публичные задачи (для фрилансеров)
@router.get("/public", response_model=List[TaskResponse])
async def get_public_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category: Optional[TaskCategory] = Query(None, description="Фильтр по категории"),
    skill_level: Optional[TaskSkillLevel] = Query(None, description="Фильтр по уровню навыка"),
    skip: int = Query(0, ge=0, description="Пропустить первые N записей"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей")
):
    if current_user.user_type != UserType.FREELANCER:
        raise HTTPException(status_code=403, detail="Только фрилансеры могут просматривать публичные задачи")

    query = db.query(Task).filter(Task.status == TaskStatus.OPEN)
    if category:
        query = query.filter(Task.category == category)
    if skill_level:
        query = query.filter(Task.skill_level == skill_level)

    tasks = query.offset(skip).limit(limit).all()
    return [TaskResponse.model_validate(task.__dict__) for task in tasks]

# Получить одну задачу по ID (для заказчиков)
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Только заказчики могут просматривать свои задачи")

    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return TaskResponse.model_validate(task.__dict__)

# Получить публичную задачу по ID (для фрилансеров)
@router.get("/{task_id}/public", response_model=TaskResponse)
async def get_public_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.FREELANCER:
        raise HTTPException(status_code=403, detail="Только фрилансеры могут просматривать публичные задачи")

    task = db.query(Task).filter(Task.id == task_id, Task.status == TaskStatus.OPEN).first()
    if not task:
        raise HTTPException(status_code=404, detail="Открытая задача не найдена")

    return TaskResponse.model_validate(task.__dict__)

# Подать заявку на задачу (для фрилансеров)
@router.post("/{task_id}/apply", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_task(
    task_id: int,
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.FREELANCER:
        raise HTTPException(status_code=403, detail="Только фрилансеры могут подавать заявки на задачи")

    task = db.query(Task).filter(Task.id == task_id, Task.status == TaskStatus.OPEN).first()
    if not task:
        raise HTTPException(status_code=404, detail="Открытая задача не найдена")

    # Проверяем, не подал ли фрилансер уже заявку
    existing_application = db.query(Application).filter(
        and_(Application.task_id == task_id, Application.freelancer_id == current_user.id)
    ).first()
    if existing_application:
        raise HTTPException(status_code=400, detail="Вы уже подали заявку на эту задачу")

    new_application = Application(
        task_id=task_id,
        freelancer_id=current_user.id,
        comment=application_data.comment,
        proposed_price=application_data.proposed_price,
        proposed_deadline=application_data.proposed_deadline,
        status=ApplicationStatus.PENDING
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return ApplicationResponse.model_validate(new_application.__dict__)

# Получить список заявок на задачу (для заказчиков)
@router.get("/{task_id}/applications", response_model=List[ApplicationResponse])
async def get_task_applications(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Только заказчики могут просматривать заявки на свои задачи")

    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    applications = db.query(Application).filter(Application.task_id == task_id).all()
    return [ApplicationResponse.model_validate(app.__dict__) for app in applications]

# Принять заявку на задачу (для заказчиков)
@router.post("/{task_id}/applications/{application_id}/accept", response_model=TaskResponse)
async def accept_application(
    task_id: int,
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Только заказчики могут принимать заявки")

    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if task.status != TaskStatus.OPEN:
        raise HTTPException(status_code=400, detail="Задача уже в процессе или закрыта")

    application = db.query(Application).filter(
        and_(Application.id == application_id, Application.task_id == task_id)
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    if application.status != ApplicationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Заявка уже обработана")

    # Обновляем задачу
    task.status = TaskStatus.IN_PROGRESS
    task.freelancer_id = application.freelancer_id

    # Обновляем статус заявки
    application.status = ApplicationStatus.ACCEPTED

    # Отклоняем остальные заявки
    other_applications = db.query(Application).filter(
        and_(Application.task_id == task_id, Application.id != application_id)
    ).all()
    for app in other_applications:
        app.status = ApplicationStatus.REJECTED

    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task.__dict__)

# Отклонить заявку на задачу (для заказчиков)
@router.post("/{task_id}/applications/{application_id}/reject", response_model=ApplicationResponse)
async def reject_application(
    task_id: int,
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Только заказчики могут отклонять заявки")

    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    application = db.query(Application).filter(
        and_(Application.id == application_id, Application.task_id == task_id)
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    if application.status != ApplicationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Заявка уже обработана")

    application.status = ApplicationStatus.REJECTED
    db.commit()
    db.refresh(application)

    return ApplicationResponse.model_validate(application.__dict__)

# Обновить задачу по ID
@router.put("/{task_id}/update", response_model=TaskResponse)
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

    update_data = task_data.dict(exclude_unset=True)

    # Проверяем бюджет
    budget_min = update_data.get("budget_min", task.budget_min)
    budget_max = update_data.get("budget_max", task.budget_max)
    try:
        validate_budget(budget_min, budget_max)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Проверяем custom_category, если категория "Другое"
    if update_data.get("category") == TaskCategory.OTHER.value:
        if not update_data.get("custom_category") and not task.custom_category:
            raise HTTPException(status_code=400, detail="Необходимо указать 'custom_category' при категории 'Другое'")

    # Преобразуем строковые значения в enum, если они переданы
    if "category" in update_data:
        try:
            update_data["category"] = TaskCategory(update_data["category"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Некорректное значение категории: {update_data['category']}")

    if "skill_level" in update_data:
        try:
            update_data["skill_level"] = TaskSkillLevel(update_data["skill_level"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Некорректный уровень навыка: {update_data['skill_level']}")

    if "status" in update_data:
        try:
            update_data["status"] = TaskStatus(update_data["status"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Некорректный статус: {update_data['status']}")

    # Обновляем поля задачи
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task.__dict__)

# Закрыть задачу по ID
@router.post("/{task_id}/close", response_model=TaskResponse)
async def close_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Только заказчики могут закрывать задачи")

    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task.status = TaskStatus.CLOSED
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