import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models.rag import AuditLog

logger = logging.getLogger(__name__)

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        status: str = "SUCCESS",
        details: Optional[str] = None
    ) -> None:
        try:
            log_entry = AuditLog(
                user_id=user_id,
                action=action,
                ip_address=ip_address,
                status=status,
                details=details
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error(f"Audit Log Error: {str(e)}")
            db.rollback()

audit_service = AuditService()
