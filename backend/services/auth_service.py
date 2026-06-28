from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user import User
from schemas.user import UserRegister, UserUpdate
from utils.security import hash_password, verify_password, create_access_token


class AuthService:
    @staticmethod
    def register(db: Session, data: UserRegister) -> User:
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        if db.query(User).filter(User.username == data.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            household_size=data.household_size,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, email: str, password: str) -> dict:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is disabled")

        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer", "user": user}

    @staticmethod
    def update_profile(db: Session, user: User, data: UserUpdate) -> User:
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.household_size is not None:
            user.household_size = data.household_size
        if data.dietary_preferences is not None:
            user.dietary_preferences = data.dietary_preferences
        db.commit()
        db.refresh(user)
        return user
