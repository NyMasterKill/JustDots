from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .models import User, UserType, BlacklistedToken
from .schemas import UserCreate, UserResponse, UserLogin, Token
from .dependencies import hash_password, verify_password, create_access_token, get_current_user, oauth2_scheme
from ..database import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Электронная почта уже зарегистрирована")
    
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
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        patronymic=db_user.patronymic,
        email=db_user.email,
        user_type=db_user.user_type.value,
        profile=db_user.profile,
        skills=db_user.skills
    )

@router.post("/login", response_model=Token)
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
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
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token, include_in_schema=False)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    blacklisted_token = BlacklistedToken(token=token)
    db.add(blacklisted_token)
    db.commit()
    return {"message": "Выход выполнен успешно, токен отозван"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        patronymic=current_user.patronymic,
        email=current_user.email,
        user_type=current_user.user_type.value,
        profile=current_user.profile,
        skills=current_user.skills
    )