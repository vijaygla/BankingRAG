from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_staff
from app.models.user import User
from app.schemas.banking import (
    KYCOut, KYCReview, AccountActivationOut,
    SupportTicketOut, SupportTicketAction
)
from app.services.staff_service import staff_service

router = APIRouter(prefix="/staff", tags=["Bank Staff Operations & Verification Module"])

@router.get("/kyc-queue", response_model=List[KYCOut])
def get_pending_kyc_queue(
    current_staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db)
):
    """
    Pending KYC Queue Workspace:
    Bank staff workspace to inspect all customer applications in KYC_PENDING status.
    """
    return staff_service.get_pending_kyc_queue(db)

@router.post("/kyc-verify/{doc_id}", response_model=KYCOut)
def verify_kyc_document(
    doc_id: int,
    payload: KYCReview,
    request: Request,
    current_staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db)
):
    """
    Document Authenticity Audit & Verification:
    Staff checks uploaded identity credentials and updates verification status (VERIFIED/REJECTED).
    """
    try:
        ip = request.client.host if request.client else None
        doc = staff_service.verify_kyc_document(
            db, doc_id=doc_id, status=payload.status,
            notes=payload.verification_notes, staff_user_id=current_staff.id, ip_address=ip
        )
        return KYCOut(
            id=doc.id,
            user_id=doc.user_id,
            user_name=doc.user.full_name if doc.user else "Customer",
            user_email=doc.user.email if doc.user else "customer@email.com",
            document_type=doc.document_type,
            document_number=doc.document_number,
            status=doc.status,
            verification_notes=doc.verification_notes,
            verified_by=doc.verified_by,
            created_at=doc.created_at,
            updated_at=doc.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/activate-account/{customer_user_id}", response_model=AccountActivationOut)
def activate_customer_account(
    customer_user_id: int,
    request: Request,
    current_staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db)
):
    """
    Account Core Activation Execution:
    Once KYC is confirmed, bank staff triggers activation:
    Calculates unique 10-digit account string code, assigns Savings Account,
    issues Credit Card, creates initial deposit, and toggles status to ACTIVE.
    """
    try:
        ip = request.client.host if request.client else None
        result = staff_service.activate_customer_account(
            db, customer_user_id=customer_user_id, staff_user_id=current_staff.id, ip_address=ip
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/tickets", response_model=List[SupportTicketOut])
def list_support_tickets(
    current_staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db)
):
    """
    Staff workspace to review operational support tickets and customer service issues.
    """
    return staff_service.list_support_tickets(db)

@router.post("/tickets/{ticket_id}/action", response_model=SupportTicketOut)
def action_support_ticket(
    ticket_id: int,
    payload: SupportTicketAction,
    request: Request,
    current_staff: User = Depends(get_current_staff),
    db: Session = Depends(get_db)
):
    """
    Operational Ticket Actions:
    Updates ticket progress, notes internal resolution, and sets status.
    """
    try:
        ip = request.client.host if request.client else None
        t = staff_service.action_support_ticket(
            db, ticket_id=ticket_id, status=payload.status,
            notes=payload.action_notes, staff_user_id=current_staff.id, ip_address=ip
        )
        return SupportTicketOut(
            id=t.id,
            ticket_code=t.ticket_code,
            user_id=t.user_id,
            user_name=t.user.full_name if t.user else "Customer",
            subject=t.subject,
            description=t.description,
            priority=t.priority,
            status=t.status,
            action_notes=t.action_notes,
            assigned_to=t.assigned_to,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
