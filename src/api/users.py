from datetime import timedelta
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import UserCreate, UserUpdate
from src.models.auth import LoginRequest  # New import
from src.config import settings
from src.config.database import get_database
from src.utils.security import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_user_id
)
from src.utils.responses import success_response, error_response
from src.persistence.repositories.user_repo import UserRepository

router = APIRouter()


def convert_user_orm_to_response(user_orm) -> dict:
    """Convert UserORM to response dict"""
    return {
        "id": str(user_orm.id),
        "username": user_orm.username,
        "email": user_orm.email,
        "subscription_tier": user_orm.subscription_tier,
        "created_at": user_orm.created_at.isoformat(),
        "updated_at": user_orm.updated_at.isoformat()
    }


# Authentication endpoints - ALL USE JSON
@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_database)
):
    """Register a new user (JSON input)"""
    user_repo = UserRepository(db)
    
    # Check if user already exists
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        return error_response(
            message="User with this email already exists",
            status_code=status.HTTP_409_CONFLICT
        )
    
    existing_username = await user_repo.get_by_username(user_data.username)
    if existing_username:
        return error_response(
            message="Username already taken",
            status_code=status.HTTP_409_CONFLICT
        )
    
    # Create new user
    try:
        user_orm = await user_repo.create(user_data)
        user_dict = convert_user_orm_to_response(user_orm)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user_orm.id)}, 
            expires_delta=access_token_expires
        )
        
        return success_response(
            data={
                "user": user_dict,
                "access_token": access_token,
                "token_type": "bearer"
            },
            message="User registered successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return error_response(
            message=f"Failed to create user: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/auth/login")
async def login_user(
    login_data: LoginRequest,  # Changed to JSON input
    db: AsyncSession = Depends(get_database)
):
    """Login user with email and password (JSON input)"""
    user_repo = UserRepository(db)
    
    # Get user by email
    user_orm = await user_repo.get_by_email(login_data.email)
    if not user_orm or not verify_password(login_data.password, user_orm.password_hash):
        return error_response(
            message="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Convert to dict for JSON serialization
    user_dict = convert_user_orm_to_response(user_orm)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user_orm.id)}, 
        expires_delta=access_token_expires
    )
    
    return success_response(
        data={
            "user": user_dict,
            "access_token": access_token,
            "token_type": "bearer"
        },
        message="Login successful"
    )


# User management endpoints
@router.get("/users/me")
async def get_current_user(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Get current authenticated user"""
    user_repo = UserRepository(db)
    user_orm = await user_repo.get_by_id(UUID(current_user_id))
    
    if not user_orm:
        return error_response(
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    user_dict = convert_user_orm_to_response(user_orm)
    return success_response(data=user_dict, message="User retrieved successfully")


@router.put("/users/me")
async def update_current_user(
    user_update: UserUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database)
):
    """Update current authenticated user (JSON input)"""
    user_repo = UserRepository(db)
    
    try:
        user_orm = await user_repo.update(UUID(current_user_id), user_update)
        if not user_orm:
            return error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        user_dict = convert_user_orm_to_response(user_orm)
        return success_response(data=user_dict, message="User updated successfully")
    except Exception as e:
        return error_response(
            message=f"Failed to update user: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )