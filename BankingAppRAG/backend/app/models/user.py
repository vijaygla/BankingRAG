from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="CUSTOMER")  # ADMIN, EMPLOYEE, CUSTOMER
    status = Column(String(50), nullable=False, default="KYC_PENDING")  # KYC_PENDING, ACTIVE, SUSPENDED, REJECTED
    phone_number = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")
    credit_cards = relationship("CreditCard", back_populates="user", cascade="all, delete-orphan")
    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    kyc_documents = relationship("KYCDocument", back_populates="user", cascade="all, delete-orphan")
    tickets = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")
