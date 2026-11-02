import random
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.banking import BankAccount, CreditCard, Loan, Transaction, KYCDocument, SupportTicket
from app.schemas.banking import KYCOut, AccountActivationOut, SupportTicketOut
from app.services.audit_service import audit_service

def generate_10_digit_account_number() -> str:
    """Calculates a unique 10-digit bank account string code (e.g. 1029384756)"""
    return str(random.randint(1000000000, 9999999999))

def generate_16_digit_card_number() -> str:
    """Generates standard 16-digit card number with bank BIN 4111"""
    rest = "".join([str(random.randint(0, 9)) for _ in range(12)])
    return f"4111{rest}"

class StaffService:
    @staticmethod
    def get_pending_kyc_queue(db: Session) -> List[KYCOut]:
        """
        Workspace: Retrieves all user verification items where status is KYC_PENDING or document status PENDING.
        """
        records = db.query(KYCDocument).join(User, KYCDocument.user_id == User.id).filter(
            (KYCDocument.status == "PENDING") | (User.status == "KYC_PENDING")
        ).all()
        
        results = []
        for r in records:
            results.append(KYCOut(
                id=r.id,
                user_id=r.user_id,
                user_name=r.user.full_name if r.user else "Unknown",
                user_email=r.user.email if r.user else "Unknown",
                document_type=r.document_type,
                document_number=r.document_number,
                status=r.status,
                verification_notes=r.verification_notes,
                verified_by=r.verified_by,
                created_at=r.created_at,
                updated_at=r.updated_at
            ))
        return results

    @staticmethod
    def verify_kyc_document(
        db: Session,
        doc_id: int,
        status: str,
        notes: Optional[str],
        staff_user_id: int,
        ip_address: Optional[str] = None
    ) -> KYCDocument:
        """
        Document Authenticity Audit: Staff inspects identity credentials and toggles verification status.
        """
        doc = db.query(KYCDocument).filter(KYCDocument.id == doc_id).first()
        if not doc:
            raise ValueError(f"KYC Document ID {doc_id} not found.")
            
        doc.status = status.upper()
        doc.verification_notes = notes or f"Audited and marked {status} by Bank Staff #{staff_user_id}"
        doc.verified_by = staff_user_id
        doc.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(doc)

        audit_service.log_action(
            db, action="KYC_VERIFICATION", user_id=staff_user_id, ip_address=ip_address,
            details=f"Staff {staff_user_id} set KYC doc {doc_id} (User {doc.user_id}) to {doc.status}"
        )
        return doc

    @staticmethod
    def activate_customer_account(
        db: Session,
        customer_user_id: int,
        staff_user_id: int,
        initial_deposit: float = 15000.0,
        ip_address: Optional[str] = None
    ) -> AccountActivationOut:
        """
        Account Core Activation:
        1. Checks customer exists.
        2. Calculates unique 10-digit account string code.
        3. Provisions default BankAccount with initial balance.
        4. Provisions Platinum Rewards CreditCard.
        5. Logs welcome transaction with unique reference ID.
        6. Updates user status to ACTIVE.
        """
        customer = db.query(User).filter(User.id == customer_user_id, User.role == "CUSTOMER").first()
        if not customer:
            raise ValueError(f"Customer #{customer_user_id} not found.")

        # Check if already active with account
        existing_acc = db.query(BankAccount).filter(BankAccount.user_id == customer_user_id).first()
        if existing_acc:
            customer.status = "ACTIVE"
            db.commit()
            return AccountActivationOut(
                message="Customer already possessed an active core account. Status refreshed to ACTIVE.",
                user_id=customer.id,
                account_number=existing_acc.account_number,
                initial_balance=existing_acc.balance,
                user_status=customer.status
            )

        # Generate unique 10-digit account string code
        while True:
            new_acc_num = generate_10_digit_account_number()
            if not db.query(BankAccount).filter(BankAccount.account_number == new_acc_num).first():
                break

        # Create Primary Savings Bank Account
        new_account = BankAccount(
            user_id=customer.id,
            account_number=new_acc_num,
            account_type="SAVINGS",
            balance=initial_deposit,
            currency="INR",
            status="ACTIVE"
        )
        db.add(new_account)
        db.flush()

        # Create Platinum Rewards Credit Card
        card_num = generate_16_digit_card_number()
        new_card = CreditCard(
            user_id=customer.id,
            card_number=card_num,
            card_variant="Platinum Rewards",
            total_limit=150000.0,
            available_limit=150000.0,
            outstanding_balance=0.0,
            due_date=(datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
            status="ACTIVE"
        )
        db.add(new_card)

        # Initial Welcome Deposit Transaction
        ref_code = f"REF-{uuid.uuid4().hex[:8].upper()}"
        welcome_tx = Transaction(
            account_id=new_account.id,
            user_id=customer.id,
            amount=initial_deposit,
            transaction_type="CREDIT",
            description="Account Opening Initial Deposit & Welcome Credit",
            reference_id=ref_code,
            balance_after=initial_deposit
        )
        db.add(welcome_tx)

        # Update User Status to ACTIVE
        customer.status = "ACTIVE"
        db.commit()
        db.refresh(new_account)

        audit_service.log_action(
            db, action="ACCOUNT_ACTIVATED", user_id=staff_user_id, ip_address=ip_address,
            details=f"Staff {staff_user_id} activated Customer {customer.id} with 10-digit Account {new_acc_num}"
        )

        return AccountActivationOut(
            message="Core account activation executed successfully with 10-digit code and linked credit card.",
            user_id=customer.id,
            account_number=new_acc_num,
            initial_balance=initial_deposit,
            user_status="ACTIVE"
        )

    @staticmethod
    def list_support_tickets(db: Session) -> List[SupportTicketOut]:
        tickets = db.query(SupportTicket).join(User, SupportTicket.user_id == User.id).all()
        return [
            SupportTicketOut(
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
            for t in tickets
        ]

    @staticmethod
    def action_support_ticket(
        db: Session,
        ticket_id: int,
        status: str,
        notes: Optional[str],
        staff_user_id: int,
        ip_address: Optional[str] = None
    ) -> SupportTicket:
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            raise ValueError(f"Ticket #{ticket_id} not found.")
            
        ticket.status = status.upper()
        ticket.action_notes = notes
        ticket.assigned_to = staff_user_id
        ticket.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(ticket)

        audit_service.log_action(
            db, action="TICKET_ACTION", user_id=staff_user_id, ip_address=ip_address,
            details=f"Staff {staff_user_id} updated Ticket {ticket.ticket_code} to {ticket.status}"
        )
        return ticket

staff_service = StaffService()
