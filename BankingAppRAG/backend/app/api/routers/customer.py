from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_customer
from app.models.user import User
from app.schemas.banking import (
    AccountOut, CreditCardOut, LoanOut, TransactionOut,
    KYCSubmit, KYCOut, SupportTicketCreate, SupportTicketOut
)
from app.services.customer_service import customer_service

router = APIRouter(tags=["Personal Customer Banking Dashboard"])

@router.get("/me/balance", response_model=List[AccountOut])
def get_customer_balances(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Tabular Account Balances View:
    Fetches real customer account records from database with masked account identifiers.
    """
    return customer_service.get_balances(db, current_user.id)

@router.get("/me/cards", response_model=List[CreditCardOut])
def get_customer_cards(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Credit Card Parameter Display:
    Available lines, statement status, outstanding numbers, and masked card numbers.
    """
    return customer_service.get_cards(db, current_user.id)

@router.get("/me/loans", response_model=List[LoanOut])
def get_customer_loans(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Loan Repayment Monitoring Screen:
    Active lending items, calculated interest rates, EMI amounts, and status.
    """
    return customer_service.get_loans(db, current_user.id)

@router.get("/me/transactions", response_model=List[TransactionOut])
def get_customer_transactions(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Live account transaction traces and balance after transactions.
    """
    return customer_service.get_transactions(db, current_user.id)

@router.post("/me/kyc/submit", response_model=KYCOut, status_code=status.HTTP_201_CREATED)
def submit_customer_kyc(
    payload: KYCSubmit,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Submits identity document (PAN, Aadhaar, Passport) for staff review.
    """
    doc = customer_service.submit_kyc(
        db, user_id=current_user.id,
        document_type=payload.document_type,
        document_number=payload.document_number
    )
    return KYCOut(
        id=doc.id,
        user_id=doc.user_id,
        user_name=current_user.full_name,
        user_email=current_user.email,
        document_type=doc.document_type,
        document_number=doc.document_number,
        status=doc.status,
        verification_notes=doc.verification_notes,
        verified_by=doc.verified_by,
        created_at=doc.created_at,
        updated_at=doc.updated_at
    )

@router.post("/me/tickets", response_model=SupportTicketOut, status_code=status.HTTP_201_CREATED)
def submit_customer_ticket(
    payload: SupportTicketCreate,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Creates an operational support ticket for bank staff handling.
    """
    ticket = customer_service.create_support_ticket(
        db, user_id=current_user.id,
        subject=payload.subject,
        description=payload.description,
        priority=payload.priority
    )
    return SupportTicketOut(
        id=ticket.id,
        ticket_code=ticket.ticket_code,
        user_id=ticket.user_id,
        user_name=current_user.full_name,
        subject=ticket.subject,
        description=ticket.description,
        priority=ticket.priority,
        status=ticket.status,
        action_notes=ticket.action_notes,
        assigned_to=ticket.assigned_to,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at
    )
