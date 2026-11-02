import re
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.masking import mask_account_number, mask_credit_card
from app.core.guardrails import validate_safe_sql_query
from app.models.banking import BankAccount, CreditCard, Loan, Transaction, KYCDocument

class UserScopedSQLAssistant:
    @staticmethod
    def execute_personal_query(
        db: Session,
        user_id: int,
        user_query: str
    ) -> Tuple[str, str]:
        """
        Executes safe, user-scoped query for current user only.
        Returns: (formatted_response, sql_executed)
        """
        clean_query = user_query.lower()

        # 1. Accounts and Balance
        if any(w in clean_query for w in ["balance", "account", "savings", "funds", "how much"]):
            accounts = db.query(BankAccount).filter(BankAccount.user_id == user_id).all()
            if not accounts:
                return (
                    "You currently do not have an active bank account. If your KYC is in pending verification, our bank staff will activate your account shortly.",
                    f"SELECT * FROM bank_accounts WHERE user_id = {user_id}"
                )
            
            lines = ["Here are your live bank account balances:"]
            for acc in accounts:
                masked_num = mask_account_number(acc.account_number)
                lines.append(f"• **{acc.account_type} Account** ({masked_num}): **₹{acc.balance:,.2f} {acc.currency}** [Status: {acc.status}]")
            return ("\n".join(lines), f"SELECT * FROM bank_accounts WHERE user_id = {user_id}")

        # 2. Credit Cards
        if any(w in clean_query for w in ["card", "credit", "limit", "outstanding"]):
            cards = db.query(CreditCard).filter(CreditCard.user_id == user_id).all()
            if not cards:
                return (
                    "No credit card is currently linked to your profile.",
                    f"SELECT * FROM credit_cards WHERE user_id = {user_id}"
                )
            
            lines = ["Here are your credit card details:"]
            for card in cards:
                masked_card = mask_credit_card(card.card_number)
                lines.append(
                    f"• **{card.card_variant}** ({masked_card}):\n"
                    f"  - Available Limit: ₹{card.available_limit:,.2f}\n"
                    f"  - Total Limit: ₹{card.total_limit:,.2f}\n"
                    f"  - Outstanding Balance: ₹{card.outstanding_balance:,.2f}\n"
                    f"  - Payment Due Date: {card.due_date or 'N/A'}\n"
                    f"  - Status: {card.status}"
                )
            return ("\n".join(lines), f"SELECT * FROM credit_cards WHERE user_id = {user_id}")

        # 3. Loans
        if any(w in clean_query for w in ["loan", "emi", "borrowing"]):
            loans = db.query(Loan).filter(Loan.user_id == user_id).all()
            if not loans:
                return (
                    "You do not have any active loans with Capgemini Apex Commercial Bank.",
                    f"SELECT * FROM loans WHERE user_id = {user_id}"
                )
            
            lines = ["Here is your active loan portfolio:"]
            for loan in loans:
                lines.append(
                    f"• **{loan.loan_type}** (Ref: {loan.loan_account_no}):\n"
                    f"  - Remaining Principal: ₹{loan.remaining_balance:,.2f} / ₹{loan.principal_amount:,.2f}\n"
                    f"  - Interest Rate: {loan.interest_rate}%\n"
                    f"  - Monthly EMI: ₹{loan.monthly_emi:,.2f}\n"
                    f"  - Tenure: {loan.tenure_months} months\n"
                    f"  - Status: {loan.status}"
                )
            return ("\n".join(lines), f"SELECT * FROM loans WHERE user_id = {user_id}")

        # 4. Transactions
        if any(w in clean_query for w in ["transaction", "statement", "passbook", "spends"]):
            txs = db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.timestamp.desc()).limit(5).all()
            if not txs:
                return (
                    "No recent transactions found on your account.",
                    f"SELECT * FROM transactions WHERE user_id = {user_id} ORDER BY timestamp DESC"
                )
            
            lines = ["Here are your last 5 transactions:"]
            for tx in txs:
                sign = "+" if tx.transaction_type == "CREDIT" else "-"
                lines.append(f"• {tx.timestamp.strftime('%Y-%m-%d %H:%M')}: {sign}₹{tx.amount:,.2f} ({tx.transaction_type}) - {tx.description} [Ref: {tx.reference_id}]")
            return ("\n".join(lines), f"SELECT * FROM transactions WHERE user_id = {user_id} ORDER BY timestamp DESC")

        # 5. KYC Status
        if "kyc" in clean_query:
            docs = db.query(KYCDocument).filter(KYCDocument.user_id == user_id).all()
            if not docs:
                return (
                    "You have not submitted any KYC documents yet. Please submit your PAN or Aadhaar card.",
                    f"SELECT * FROM kyc_documents WHERE user_id = {user_id}"
                )
            lines = ["Your KYC Document Status:"]
            for d in docs:
                lines.append(f"• {d.document_type} ({d.document_number}): Status: {d.status}. Notes: {d.verification_notes or 'Pending review'}")
            return ("\n".join(lines), f"SELECT * FROM kyc_documents WHERE user_id = {user_id}")

        # Default fallback to account summary
        accounts = db.query(BankAccount).filter(BankAccount.user_id == user_id).all()
        if accounts:
            summary = ", ".join([f"{a.account_type}: ₹{a.balance:,.2f}" for a in accounts])
            return (f"Your active account balances: {summary}", f"SELECT * FROM bank_accounts WHERE user_id = {user_id}")

        return (
            "I could not match your request to your banking records. You can ask for your account balance, cards, loans, or recent transactions.",
            f"SELECT * FROM users WHERE id = {user_id}"
        )

text_to_sql = UserScopedSQLAssistant()
