from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    household_size: int = Field(default=1, ge=1, le=20)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must contain only letters, numbers, underscores, or hyphens")
        return v.lower()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    household_size: int
    dietary_preferences: Optional[str]


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    household_size: Optional[int] = Field(default=None, ge=1, le=20)
    dietary_preferences: Optional[str] = None  # JSON string of preferences


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenData(BaseModel):
    user_id: Optional[int] = None
