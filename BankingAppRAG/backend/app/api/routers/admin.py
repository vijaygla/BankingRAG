from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_admin
from app.models.user import User
from app.models.rag import AuditLog
from app.schemas.auth import EmployeeCreate, UserProfile
from app.services.auth_service import auth_service

router = APIRouter(prefix="/admin", tags=["Admin Operations & System Governance"])

@router.post("/employees", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
def provision_employee(
    payload: EmployeeCreate,
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Employee Account Provisioning:
    Admin dashboard creates new bank staff profiles and grants employee privileges.
    No public access allowed.
    """
    try:
        ip = request.client.host if request.client else None
        employee = auth_service.provision_employee(
            db, emp_data=payload, admin_user_id=current_admin.id, ip_address=ip
        )
        return employee
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/users", response_model=List[UserProfile])
def list_system_users(
    role: Optional[str] = Query(None, description="Filter by role: ADMIN, EMPLOYEE, CUSTOMER"),
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE, KYC_PENDING, SUSPENDED"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin directory view of all provisioned accounts across all roles.
    """
    query = db.query(User)
    if role:
        query = query.filter(User.role == role.upper())
    if status:
        query = query.filter(User.status == status.upper())
    return query.order_by(User.id.desc()).all()

@router.get("/audit-logs")
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Immutable Compliance Audit Logs Archive:
    Provides full security operational timelines, login checks, and token traces.
    """
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "action": l.action,
            "ip_address": l.ip_address,
            "status": l.status,
            "details": l.details,
            "created_at": l.created_at
        }
        for l in logs
    ]
