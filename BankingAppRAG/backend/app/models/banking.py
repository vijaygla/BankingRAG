from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_number = Column(String(20), unique=True, index=True, nullable=False) # 10-digit number
    account_type = Column(String(50), nullable=False, default="SAVINGS") # SAVINGS, CURRENT
    balance = Column(Float, nullable=False, default=0.0)
    currency = Column(String(10), nullable=False, default="INR")
    status = Column(String(50), nullable=False, default="ACTIVE") # ACTIVE, FROZEN, DORMANT
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")


class CreditCard(Base):
    __tablename__ = "credit_cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    card_number = Column(String(30), unique=True, index=True, nullable=False) # 16-digit card number
    card_variant = Column(String(50), nullable=False, default="Platinum Rewards")
    total_limit = Column(Float, nullable=False, default=100000.0)
    available_limit = Column(Float, nullable=False, default=100000.0)
    outstanding_balance = Column(Float, nullable=False, default=0.0)
    due_date = Column(String(50), nullable=True) # e.g. "2026-10-15"
    status = Column(String(50), nullable=False, default="ACTIVE") # ACTIVE, BLOCKED
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="credit_cards")


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    loan_account_no = Column(String(30), unique=True, index=True, nullable=False)
    loan_type = Column(String(50), nullable=False) # Home Loan, Personal Loan, Auto Loan
    principal_amount = Column(Float, nullable=False)
    remaining_balance = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False) # e.g. 8.40 (%)
    tenure_months = Column(Integer, nullable=False)
    monthly_emi = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="ACTIVE") # ACTIVE, CLOSED, DEFAULTED
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="loans")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False) # CREDIT, DEBIT
    description = Column(String(255), nullable=False)
    reference_id = Column(String(50), unique=True, index=True, nullable=False)
    balance_after = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    account = relationship("BankAccount", back_populates="transactions")


class KYCDocument(Base):
    __tablename__ = "kyc_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type = Column(String(50), nullable=False) # PAN, AADHAAR, PASSPORT
    document_number = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="PENDING") # PENDING, VERIFIED, REJECTED
    verification_notes = Column(String(500), nullable=True)
    verified_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="kyc_documents")


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_code = Column(String(50), unique=True, index=True, nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="MEDIUM") # LOW, MEDIUM, HIGH
    status = Column(String(50), nullable=False, default="OPEN") # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    action_notes = Column(Text, nullable=True)
    assigned_to = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="tickets")
