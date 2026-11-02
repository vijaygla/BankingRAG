from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class AccountOut(BaseModel):
    id: int
    account_number: str # will be masked e.g. AC*******1023
    account_type: str
    balance: float
    currency: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class CreditCardOut(BaseModel):
    id: int
    card_number: str # masked e.g. 4111********1234
    card_variant: str
    total_limit: float
    available_limit: float
    outstanding_balance: float
    due_date: Optional[str] = None
    status: str

    class Config:
        from_attributes = True

class LoanOut(BaseModel):
    id: int
    loan_account_no: str
    loan_type: str
    principal_amount: float
    remaining_balance: float
    interest_rate: float
    tenure_months: int
    monthly_emi: float
    status: str

    class Config:
        from_attributes = True

class TransactionOut(BaseModel):
    id: int
    account_id: int
    amount: float
    transaction_type: str
    description: str
    reference_id: str
    balance_after: float
    timestamp: datetime

    class Config:
        from_attributes = True

class KYCSubmit(BaseModel):
    document_type: str = Field(..., description="PAN, AADHAAR, or PASSPORT")
    document_number: str = Field(..., min_length=4)

class KYCReview(BaseModel):
    status: str = Field(..., description="VERIFIED or REJECTED")
    verification_notes: Optional[str] = None

class KYCOut(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    document_type: str
    document_number: str
    status: str
    verification_notes: Optional[str] = None
    verified_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AccountActivationOut(BaseModel):
    message: str
    user_id: int
    account_number: str # 10-digit generated account number
    initial_balance: float
    user_status: str

class SupportTicketCreate(BaseModel):
    subject: str = Field(..., min_length=3)
    description: str = Field(..., min_length=5)
    priority: str = Field("MEDIUM", description="LOW, MEDIUM, or HIGH")

class SupportTicketAction(BaseModel):
    status: str = Field(..., description="OPEN, IN_PROGRESS, RESOLVED, or CLOSED")
    action_notes: Optional[str] = None

class SupportTicketOut(BaseModel):
    id: int
    ticket_code: str
    user_id: int
    user_name: Optional[str] = None
    subject: str
    description: str
    priority: str
    status: str
    action_notes: Optional[str] = None
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
