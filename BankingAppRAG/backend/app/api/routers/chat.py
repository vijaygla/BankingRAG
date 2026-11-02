from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_any_authenticated_user
from app.models.user import User
from app.models.rag import ChatHistory, ChatFeedback
from app.schemas.chat import (
    ChatQueryRequest, ChatQueryResponse, ChatFeedbackRequest, ChatMessageHistoryItem
)
from app.ai.rag_assistant import rag_assistant
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["Core AI Chatbot Module"])

@router.post("/ask", response_model=ChatQueryResponse)
async def ask_banking_assistant(
    payload: ChatQueryRequest,
    current_user: User = Depends(get_any_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Intelligent Banking Assistant:
    1. Smart Intent Classifier Router: Parses query into POLICY_DOC, USER_SQL, or REFUSE_OOS.
    2. Policy Query via RAG: Executes vector search over banking rulebooks with citations.
    3. Live Personal Data Query: User-scoped Text-to-SQL for live balance, cards, and loans.
    4. Conversational Cache Memory: Contextual sliding window and duplicate query caching.
    5. Enterprise Guardrails: PII masking and prompt injection defenses.
    """
    # Validate selected model if supplied
    if payload.model and payload.model not in settings.ALLOWED_AI_MODELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model '{payload.model}'. Supported models: {settings.ALLOWED_AI_MODELS}"
        )

    response = await rag_assistant.process_user_message(
        db=db,
        user_id=current_user.id,
        message=payload.message,
        session_id=payload.session_id,
        model_override=payload.model
    )
    return response

@router.get("/history/{session_id}", response_model=List[ChatMessageHistoryItem])
def get_chat_session_history(
    session_id: str,
    current_user: User = Depends(get_any_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves previous conversation turns for the active session.
    """
    messages = db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id,
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.asc()).all()
    return messages

@router.post("/feedback", status_code=status.HTTP_201_CREATED)
def submit_chat_feedback(
    payload: ChatFeedbackRequest,
    current_user: User = Depends(get_any_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Message-Level Performance Feedback:
    Collects rating and user commentary to monitor model accuracy and prompt effectiveness.
    """
    feedback = ChatFeedback(
        message_id=payload.message_id,
        user_id=current_user.id,
        rating=payload.rating,
        comment=payload.comment
    )
    db.add(feedback)
    db.commit()
    return {"message": "Thank you! Chat feedback recorded successfully."}

@router.get("/models")
def get_available_ai_models():
    """
    Returns list of selectable AI LLM models supported by Capgemini Generative Engine.
    """
    return {
        "default_model": settings.DEFAULT_AI_MODEL,
        "available_models": settings.ALLOWED_AI_MODELS
    }
