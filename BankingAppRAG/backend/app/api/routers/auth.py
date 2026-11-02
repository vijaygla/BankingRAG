from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserProfile
from app.services.auth_service import auth_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(tags=["Authentication & Onboarding"])

@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
def register_customer(
    payload: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Customer Self-Registration:
    New public users (customers) register here. Password hashed with BCrypt,
    and status defaults to KYC_PENDING. Role is strictly CUSTOMER (no selection exposed).
    """
    try:
        ip = request.client.host if request.client else None
        user = auth_service.register_customer(db, payload, ip_address=ip)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Secure Login Module:
    Any user (CUSTOMER, EMPLOYEE, ADMIN) logs in with email and password.
    Returns a unique 24-hour expiry JWT token and role context.
    """
    try:
        ip = request.client.host if request.client else None
        token_data = auth_service.authenticate_user(db, payload, ip_address=ip)
        return token_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/me", response_model=UserProfile)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves logged-in user profile, role, and verification status.
    """
    return current_user
