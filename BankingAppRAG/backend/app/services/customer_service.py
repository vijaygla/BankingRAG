import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.banking import BankAccount, CreditCard, Loan, Transaction, KYCDocument, SupportTicket
from app.core.masking import mask_account_number, mask_credit_card
from app.schemas.banking import AccountOut, CreditCardOut, LoanOut, TransactionOut, KYCOut, SupportTicketOut
from app.services.audit_service import audit_service

class CustomerService:
    @staticmethod
    def get_balances(db: Session, user_id: int) -> List[AccountOut]:
        accounts = db.query(BankAccount).filter(BankAccount.user_id == user_id).all()
        return [
            AccountOut(
                id=a.id,
                account_number=mask_account_number(a.account_number),
                account_type=a.account_type,
                balance=a.balance,
                currency=a.currency,
                status=a.status,
                created_at=a.created_at
            )
            for a in accounts
        ]

    @staticmethod
    def get_cards(db: Session, user_id: int) -> List[CreditCardOut]:
        cards = db.query(CreditCard).filter(CreditCard.user_id == user_id).all()
        return [
            CreditCardOut(
                id=c.id,
                card_number=mask_credit_card(c.card_number),
                card_variant=c.card_variant,
                total_limit=c.total_limit,
                available_limit=c.available_limit,
                outstanding_balance=c.outstanding_balance,
                due_date=c.due_date,
                status=c.status
            )
            for c in cards
        ]

    @staticmethod
    def get_loans(db: Session, user_id: int) -> List[LoanOut]:
        loans = db.query(Loan).filter(Loan.user_id == user_id).all()
        return [
            LoanOut(
                id=l.id,
                loan_account_no=l.loan_account_no,
                loan_type=l.loan_type,
                principal_amount=l.principal_amount,
                remaining_balance=l.remaining_balance,
                interest_rate=l.interest_rate,
                tenure_months=l.tenure_months,
                monthly_emi=l.monthly_emi,
                status=l.status
            )
            for l in loans
        ]

    @staticmethod
    def get_transactions(db: Session, user_id: int, limit: int = 20) -> List[TransactionOut]:
        txs = db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.timestamp.desc()).limit(limit).all()
        return [
            TransactionOut(
                id=t.id,
                account_id=t.account_id,
                amount=t.amount,
                transaction_type=t.transaction_type,
                description=t.description,
                reference_id=t.reference_id,
                balance_after=t.balance_after,
                timestamp=t.timestamp
            )
            for t in txs
        ]

    @staticmethod
    def submit_kyc(
        db: Session,
        user_id: int,
        document_type: str,
        document_number: str,
        file_path: Optional[str] = None
    ) -> KYCDocument:
        doc = KYCDocument(
            user_id=user_id,
            document_type=document_type.upper(),
            document_number=document_number,
            file_path=file_path,
            status="PENDING",
            verification_notes="Awaiting review by bank operations staff"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        audit_service.log_action(
            db, action="KYC_SUBMITTED", user_id=user_id,
            details=f"Customer submitted KYC document: {document_type} ({document_number})"
        )
        return doc

    @staticmethod
    def create_support_ticket(
        db: Session,
        user_id: int,
        subject: str,
        description: str,
        priority: str = "MEDIUM"
    ) -> SupportTicket:
        t_code = f"TCK-{uuid.uuid4().hex[:6].upper()}"
        ticket = SupportTicket(
            user_id=user_id,
            ticket_code=t_code,
            subject=subject,
            description=description,
            priority=priority.upper(),
            status="OPEN"
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

customer_service = CustomerService()
