from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    role: str = "customer"

class UserCreate(UserBase):
    password: str

class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    name: Optional[str] = None
    phone: Optional[str] = None
    dietary_preferences: Optional[List[str]] = None
    notification_enabled: Optional[bool] = None
    preferred_language: Optional[str] = None

class PasswordChange(BaseModel):
    """Schema for changing user password"""
    current_password: str
    new_password: str

class SetPassword(BaseModel):
    new_password: str

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    avatar_url: Optional[str] = None
    dietary_preferences: Optional[List[str]] = []
    notification_enabled: bool = True
    preferred_language: str = "en"
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class User(UserInDBBase):
    restaurant_id: Optional[int] = None
    force_password_change: bool = False
    
    class Config:
        orm_mode = True

class UserStats(BaseModel):
    """User statistics"""
    total_orders: int
    total_spent: float
    favorite_items: List[dict]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
