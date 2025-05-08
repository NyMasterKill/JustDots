from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg.errors import UniqueViolation
from .models import User, UserType, BlacklistedToken
from .schemas import UserCreate, UserResponse, UserLogin, Token
from .dependencies import hash_password, verify_password, create_access_token, create_refresh_token, \
    verify_refresh_token, get_current_user, oauth2_scheme
from ..database import get_db
from datetime import datetime
from ..tasks.models import Task, TaskStatus

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        if db_user.email == user.email:
            raise HTTPException(status_code=400, detail="Электронная почта уже зарегистрирована")
        if db_user.username == user.username:
            raise HTTPException(status_code=400, detail="Имя пользователя уже занято")

    hashed_password = hash_password(user.password)
    if user.user_type == "customer":
        user_type = UserType.CUSTOMER
    elif user.user_type == "freelancer":
        user_type = UserType.FREELANCER
    else:
        raise HTTPException(status_code=400, detail=f"Недопустимый тип пользователя: {user.user_type}")

    db_user = User(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        patronymic=user.patronymic,
        email=user.email,
        hashed_password=hashed_password,
        user_type=user_type
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError as e:
        db.rollback()
        if isinstance(e.orig, UniqueViolation):
            if "ix_users_username" in str(e.orig):
                raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
            if "ix_users_email" in str(e.orig):
                raise HTTPException(status_code=400, detail="Электронная почта уже зарегистрирована")
        raise HTTPException(status_code=500, detail="Ошибка при регистрации пользователя")

    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        patronymic=db_user.patronymic,
        email=db_user.email,
        user_type=db_user.user_type.value,
        created_at=db_user.created_at.isoformat() if db_user.created_at else None,
        profile=db_user.profile,
        skills=db_user.skills,
        completed_tasks_count=0
    )


@router.post("/login", response_model=Token)
async def login_user(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    query = db.query(User)
    if user.email:
        query = query.filter(User.email == user.email)
    elif user.username:
        query = query.filter(User.username == user.username)
    else:
        raise HTTPException(status_code=400, detail="Необходимо указать email или username")

    db_user = query.first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email, username или пароль")

    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_refresh_token(data={"sub": db_user.email})
    # Устанавливаем refresh token в HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Для localhost в разработке
        samesite="strict",
        max_age=7 * 24 * 60 * 60  # 7 дней
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token, include_in_schema=False)
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    query = db.query(User)
    input_value = form_data.username
    if "@" in input_value:
        query = query.filter(User.email == input_value)
    else:
        query = query.filter(User.username == input_value)

    db_user = query.first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email, username или пароль")

    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_refresh_token(data={"sub": db_user.email})
    
    # Устанавливаем refresh token в HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Для localhost в разработке
        samesite="strict",
        max_age=7 * 24 * 60 * 60  # 7 дней
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_access_token(response: Response, refresh_token: str | None = Cookie(default=None), db: Session = Depends(get_db)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token не предоставлен")
    
    email = verify_refresh_token(refresh_token)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  
        samesite="strict",
        max_age=7 * 24 * 60 * 60  
    )
    
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout_user(response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Добавляем access token в чёрный список
    blacklisted_token = BlacklistedToken(token=token)
    db.add(blacklisted_token)
    db.commit()
    
    # Очищаем refresh token cookie
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Выход выполнен успешно, токен отозван"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
        completed_tasks_count=completed_tasks_count,
        rating = current_user.rating
    )
