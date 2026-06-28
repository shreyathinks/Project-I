from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from models.user import User
from schemas.user import Token, UserLogin, UserOut, UserRegister, UserUpdate
from services.auth_service import AuthService
from utils.security import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    return AuthService.register(db, data)


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and return a JWT access token."""
    return AuthService.login(db, data.email, data.password)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user


@router.put("/me", response_model=UserOut)
def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile settings."""
    return AuthService.update_profile(db, current_user, data)
