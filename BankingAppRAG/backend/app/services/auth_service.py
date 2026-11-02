import logging
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, EmployeeCreate
from app.services.audit_service import audit_service

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def register_customer(db: Session, reg_data: UserRegister, ip_address: Optional[str] = None) -> User:
        """
        Public user registration.
        Strictly sets role = 'CUSTOMER' and status = 'KYC_PENDING'.
        """
        existing_user = db.query(User).filter(User.email == reg_data.email.lower()).first()
        if existing_user:
            raise ValueError("Email already registered with Capgemini Apex Commercial Bank.")
            
        new_user = User(
            email=reg_data.email.lower(),
            hashed_password=get_password_hash(reg_data.password),
            full_name=reg_data.full_name,
            phone_number=reg_data.phone_number,
            role="CUSTOMER",
            status="KYC_PENDING"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        audit_service.log_action(
            db, action="CUSTOMER_REGISTER", user_id=new_user.id, ip_address=ip_address,
            details=f"Customer registered: {new_user.email} with status KYC_PENDING"
        )
        return new_user

    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin, ip_address: Optional[str] = None) -> TokenResponse:
        """
        Authenticates any role (CUSTOMER, EMPLOYEE, ADMIN) and generates 24-hour JWT token.
        """
        user = db.query(User).filter(User.email == login_data.email.lower()).first()
        if not user or not verify_password(login_data.password, user.hashed_password):
            audit_service.log_action(
                db, action="LOGIN_FAILED", ip_address=ip_address, status="FAILED",
                details=f"Failed login attempt for: {login_data.email}"
            )
            raise ValueError("Invalid email or password.")
            
        if user.status == "SUSPENDED":
            audit_service.log_action(
                db, action="LOGIN_BLOCKED", user_id=user.id, ip_address=ip_address, status="BLOCKED",
                details=f"Suspended user attempted login: {user.email}"
            )
            raise ValueError("Account is suspended. Please contact bank administration.")

        token = create_access_token(
            subject=user.id,
            role=user.role,
            email=user.email,
            status=user.status
        )

        audit_service.log_action(
            db, action="LOGIN_SUCCESS", user_id=user.id, ip_address=ip_address,
            details=f"Successful login as {user.role} ({user.email})"
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            status=user.status
        )

    @staticmethod
    def provision_employee(db: Session, emp_data: EmployeeCreate, admin_user_id: int, ip_address: Optional[str] = None) -> User:
        """
        Provisions a new bank employee profile. Admin-only.
        """
        existing = db.query(User).filter(User.email == emp_data.email.lower()).first()
        if existing:
            raise ValueError("An account with this email already exists.")
            
        employee = User(
            email=emp_data.email.lower(),
            hashed_password=get_password_hash(emp_data.password),
            full_name=emp_data.full_name,
            phone_number=emp_data.phone_number,
            role="EMPLOYEE",
            status="ACTIVE"
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)

        audit_service.log_action(
            db, action="EMPLOYEE_PROVISIONED", user_id=admin_user_id, ip_address=ip_address,
            details=f"Admin {admin_user_id} created bank employee: {employee.email}"
        )
        return employee

    @staticmethod
    def seed_super_admin(db: Session) -> User:
        """
        Super-User Auto-Seeding: Populates default master administrator on app startup.
        """
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL.lower()).first()
        if not admin:
            logger.info(f"Seeding master Super Admin: {settings.ADMIN_EMAIL}")
            admin = User(
                email=settings.ADMIN_EMAIL.lower(),
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                full_name=settings.ADMIN_NAME,
                role="ADMIN",
                status="ACTIVE"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            logger.info("Master Super Admin created successfully.")
        return admin

auth_service = AuthService()
