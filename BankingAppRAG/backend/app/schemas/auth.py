from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    full_name: str = Field(..., min_length=2)
    phone_number: Optional[str] = None
    # Strictly NO role selection field allowed here! Public registration is always CUSTOMER.

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: str
    role: str
    status: str
    expires_in: int = 86400  # 24 hours in seconds

class EmployeeCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    phone_number: Optional[str] = None

class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    status: str
    phone_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
