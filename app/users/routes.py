from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from ..auth.models import User, UserType
from ..auth.dependencies import get_current_user
from ..auth.schemas import UserResponse
from .models import Profile, Skill, Portfolio
from .schemas import SkillCreate, PortfolioCreate
from ..database import get_db
from ..tasks.models import Task, TaskStatus
import os
import shutil
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("uploads/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.put("/profile/update", response_model=UserResponse)
async def update_profile(
    bio: str = Form(None),  # Делаем опциональным для совместимости с текущим запросом
    avatar: UploadFile = File(None),  # Опциональный файл
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()  # Сохраняем профиль перед обновлением

    # Обновляем bio, если оно передано
    if bio is not None:
        profile.bio = bio

    # Обработка загрузки аватарки
    if avatar:
        # Проверяем тип файла
        allowed_extensions = {".png", ".jpg", ".jpeg"}
        file_extension = os.path.splitext(avatar.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Only PNG, JPG, and JPEG files are allowed")
        
        # Проверяем размер файла (максимум 5 МБ)
        max_size = 5 * 1024 * 1024  # 5 МБ
        content = await avatar.read()
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail="File size must not exceed 5 MB")
        
        # Формируем путь для сохранения файла
        file_path = UPLOAD_DIR / f"{current_user.id}{file_extension}"
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Сохраняем путь в базе данных
        profile.avatar_url = f"/uploads/avatars/{current_user.id}{file_extension}"

    db.commit()
    db.refresh(current_user)

    # Подсчёт завершённых задач
    if current_user.user_type == UserType.CUSTOMER:
        completed_tasks_count = db.query(Task).filter(
            Task.owner_id == current_user.id,
            Task.status == TaskStatus.CLOSED.value
        ).count()
    else:  # FREELANCER
        completed_tasks_count = db.query(Task).filter(
            Task.freelancer_id == current_user.id,
            Task.status == TaskStatus.CLOSED.value
        ).count()

    profile_data = current_user.profile
    if profile_data:
        profile_data.portfolio = current_user.portfolio if current_user.portfolio else []

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        patronymic=current_user.patronymic,
        email=current_user.email,
        user_type=current_user.user_type.value,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None,
        profile=profile_data,
        skills=current_user.skills,
        completed_tasks_count=completed_tasks_count
    )

@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if user.user_type == UserType.CUSTOMER:
        completed_tasks_count = db.query(Task).filter(
            Task.owner_id == user.id,
            Task.status == TaskStatus.CLOSED.value
        ).count()
    else:  # FREELANCER
        completed_tasks_count = db.query(Task).filter(
            Task.freelancer_id == user.id,
            Task.status == TaskStatus.CLOSED.value
        ).count()

    profile_data = user.profile
    if profile_data:
        profile_data.portfolio = user.portfolio if user.portfolio else []

    return UserResponse(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        patronymic=user.patronymic,
        email=user.email,
        user_type=user.user_type.value,
        created_at=user.created_at.isoformat() if user.created_at else None,
        profile=profile_data,
        skills=user.skills,
        completed_tasks_count=completed_tasks_count
    )