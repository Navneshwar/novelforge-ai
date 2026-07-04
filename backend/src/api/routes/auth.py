from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from src.models import User

router = APIRouter()


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=2000)
    avatar_url: str | None = Field(default=None, max_length=1024)


class UserResponse(BaseModel):
    id: int
    email: str
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    is_active: bool
    created_at: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


def serialize_user(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        bio=user.bio,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    email = request.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=400, detail="A valid email address is required")
    
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email is already registered")
    
    user = User(
        email=email,
        password_hash=hash_password(request.password),
        display_name=request.display_name or email.split("@")[0],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return AuthResponse(
        access_token=create_access_token(str(user.id)),
        user=serialize_user(user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    email = request.email.strip().lower()
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return AuthResponse(
        access_token=create_access_token(str(user.id)),
        user=serialize_user(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return serialize_user(user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for key, value in request.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return serialize_user(user)
