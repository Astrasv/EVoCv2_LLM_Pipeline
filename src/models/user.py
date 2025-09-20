from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    subscription_tier: str = "free"


class UserCreate(UserBase):
    password: str  # Plain password for input


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    subscription_tier: Optional[str] = None
    password: Optional[str] = None  # Optional password update


class UserResponse(UserBase):
    """User response model (excludes password_hash)"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserBase):
    """Internal user model with password hash"""
    id: UUID
    password_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True