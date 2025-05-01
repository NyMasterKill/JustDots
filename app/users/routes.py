from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth.models import User, UserType
from ..auth.dependencies import get_current_user
from ..auth.schemas import UserResponse
from .models import Profile, Skill, Portfolio
from .schemas import ProfileUpdate
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/profile", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
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

@router.put("/profile/update", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
    
    if profile_data.bio is not None:
        profile.bio = profile_data.bio
    if profile_data.rating is not None:
        profile.rating = profile_data.rating
    
    if profile_data.skills and current_user.user_type == UserType.FREELANCER:
        db.query(Skill).filter(Skill.user_id == current_user.id).delete()
        for skill_data in profile_data.skills:
            skill = Skill(user_id=current_user.id, name=skill_data.name)
            db.add(skill)
    
    if profile_data.portfolio and current_user.user_type == UserType.FREELANCER:
        db.query(Portfolio).filter(Portfolio.user_id == current_user.id).delete()
        for portfolio_data in profile_data.portfolio:
            portfolio = Portfolio(
                user_id=current_user.id,
                title=portfolio_data.title,
                description=portfolio_data.description,
                url=portfolio_data.url
            )
            db.add(portfolio)
    
    db.commit()
    db.refresh(current_user)
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

@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        patronymic=user.patronymic,
        email=user.email,
        user_type=user.user_type.value,
        profile=user.profile,
        skills=user.skills
    )