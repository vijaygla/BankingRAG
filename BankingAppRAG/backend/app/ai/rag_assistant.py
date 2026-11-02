import time
import json
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.masking import mask_text_pii
from app.ai.intent_classifier import classify_intent
from app.ai.generative_engine import ai_client
from app.ai.vector_store import vector_store
from app.ai.text_to_sql import text_to_sql
from app.ai.cache_service import cache_service
from app.models.rag import ChatHistory
from app.schemas.chat import ChatQueryResponse, CitationItem

SYSTEM_RAG_PROMPT = """You are the Capgemini Apex Commercial Bank AI Assistant.
Your mission is to provide accurate, professional, and compliant answers to banking customers.

CRITICAL OPERATIONAL RULES:
1. Base your answer STRICTLY and SOLELY on the provided Context Documents below.
2. If the answer cannot be determined from the provided documents, politely state:
   "I am sorry, but this specific information is not available in our official banking policy manual. Please contact bank customer support or visit your nearest branch."
3. Do NOT hallucinate, assume, or fabricate any financial rules, interest rates, or fees.
4. When mentioning interest rates, processing fees, or eligibility criteria, cite the exact numbers from the context.
5. In your answer, clearly and explicitly state which specific document/policy file you are retrieving the information from (for example: "According to [Document Title] ([Filename]), ..."), so the user knows exactly where the policy details originate.
6. Keep your tone professional, concise, courteous, and transparent.

CONTEXT DOCUMENTS:
{context_blocks}
"""

class RAGAssistant:
    @staticmethod
    async def process_user_message(
        db: Session,
        user_id: int,
        message: str,
        session_id: Optional[str] = None,
        model_override: Optional[str] = None
    ) -> ChatQueryResponse:
        start_time = time.time()
        active_session_id = session_id or str(uuid.uuid4())
        chosen_model = model_override or settings.DEFAULT_AI_MODEL
        
        # 1. Intent Classification Router
        intent = classify_intent(message)
        
        # ----------------------------------------------------
        # BRANCH A: REFUSE_OOS (Prompt Injection / Out of Scope)
        # ----------------------------------------------------
        if intent == "REFUSE_OOS":
            latency_ms = round((time.time() - start_time) * 1000, 2)
            refusal_msg = (
                "I am sorry, but as an official Capgemini Commercial Bank AI Assistant, "
                "I can only assist with verified banking policies, loan guidelines, interest rates, "
                "and your secure personal account information. Requests outside our banking scope "
                "or attempting prompt overrides are strictly restricted by our security guardrails."
            )
            
            # Save interaction in chat history
            RAGAssistant._save_history(db, user_id, active_session_id, "user", message, intent, chosen_model, 0, latency_ms)
            RAGAssistant._save_history(db, user_id, active_session_id, "assistant", refusal_msg, intent, chosen_model, 0, latency_ms)
            
            return ChatQueryResponse(
                answer=refusal_msg,
                intent="REFUSE_OOS",
                citations=[],
                model_used=chosen_model,
                latency_ms=latency_ms,
                tokens_used=0,
                session_id=active_session_id,
                cached=False
            )

        # ----------------------------------------------------
        # BRANCH B: USER_SQL (Personal Banking Data Query)
        # ----------------------------------------------------
        if intent == "USER_SQL":
            answer_text, sql_statement = text_to_sql.execute_personal_query(db, user_id, message)
            latency_ms = round((time.time() - start_time) * 1000, 2)
            
            # Save interaction in chat history
            RAGAssistant._save_history(db, user_id, active_session_id, "user", message, intent, chosen_model, 0, latency_ms)
            RAGAssistant._save_history(db, user_id, active_session_id, "assistant", answer_text, intent, chosen_model, 0, latency_ms)
            
            return ChatQueryResponse(
                answer=answer_text,
                intent="USER_SQL",
                citations=[],
                model_used="User-Scoped Database Connector",
                latency_ms=latency_ms,
                tokens_used=0,
                session_id=active_session_id,
                cached=False
            )

        # ----------------------------------------------------
        # BRANCH C: POLICY_DOC (RAG Retrieval Pipeline)
        # ----------------------------------------------------
        # Check cache memory first
        cached_result = cache_service.get_cached_response(db, message)
        if cached_result:
            cached_answer, cached_citations = cached_result
            latency_ms = round((time.time() - start_time) * 1000, 2)
            citation_items = [CitationItem(**c) for c in cached_citations]
            
            return ChatQueryResponse(
                answer=cached_answer,
                intent="POLICY_DOC",
                citations=citation_items,
                model_used=f"{chosen_model} (Cached)",
                latency_ms=latency_ms,
                tokens_used=0,
                session_id=active_session_id,
                cached=True
            )

        # Embed query text
        try:
            query_embedding = await ai_client.get_embedding(message)
        except Exception:
            # If embedding fails, fallback to semantic string match
            query_embedding = []

        # Vector Retrieval from MS SQL Chunks
        retrieved_chunks = vector_store.search_similar_chunks(db, query_embedding, top_k=4, query_text=message)
        
        # Prepare context blocks and citations
        context_blocks = ""
        citations: List[CitationItem] = []
        
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            context_blocks += f"\n[Document {idx}: {chunk['title']} | File: {chunk['filename']} | Page/Chunk: {chunk['page_number']}]\n{chunk['content']}\n"
            snippet = chunk['content'][:140] + "..." if len(chunk['content']) > 140 else chunk['content']
            citations.append(CitationItem(
                filename=chunk['filename'],
                title=chunk['title'],
                chunk_index=chunk['chunk_index'],
                score=chunk['score'],
                snippet=snippet
            ))

        if not context_blocks.strip():
            context_blocks = "No specific banking manual was retrieved for this query."

        # Fetch sliding window conversation memory (last 4 turns)
        recent_history = db.query(ChatHistory).filter(
            ChatHistory.session_id == active_session_id,
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.created_at.desc()).limit(4).all()
        recent_history.reverse()

        # Build prompt messages
        system_instruction = SYSTEM_RAG_PROMPT.format(context_blocks=context_blocks)
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_instruction}
        ]
        for turn in recent_history:
            messages.append({"role": turn.role, "content": turn.content})
        messages.append({"role": "user", "content": message})

        # Execute LLM generation
        try:
            generated_answer, tokens_used, actual_model = await ai_client.get_chat_completion(
                messages=messages,
                model=chosen_model
            )
        except Exception as e:
            generated_answer = (
                "Our banking intelligence services are currently experiencing high volume. "
                "Please try again in a few moments or refer directly to your branch loan guidelines."
            )
            tokens_used = 0
            actual_model = chosen_model

        # Mask any sensitive financial tokens in output
        safe_answer = mask_text_pii(generated_answer)
        
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        # Cache response for identical queries
        cache_service.set_cached_response(
            db, message, safe_answer, [c.model_dump() for c in citations]
        )

        # Save conversation history
        RAGAssistant._save_history(db, user_id, active_session_id, "user", message, "POLICY_DOC", actual_model, 0, 0)
        RAGAssistant._save_history(
            db, user_id, active_session_id, "assistant", safe_answer, "POLICY_DOC",
            actual_model, tokens_used, latency_ms, json.dumps([c.model_dump() for c in citations])
        )

        return ChatQueryResponse(
            answer=safe_answer,
            intent="POLICY_DOC",
            citations=citations,
            model_used=actual_model,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            session_id=active_session_id,
            cached=False
        )

    @staticmethod
    def _save_history(
        db: Session,
        user_id: int,
        session_id: str,
        role: str,
        content: str,
        intent: str,
        model_used: str,
        tokens_used: int,
        latency_ms: float,
        citations_json: Optional[str] = None
    ) -> None:
        try:
            record = ChatHistory(
                user_id=user_id,
                session_id=session_id,
                role=role,
                content=content,
                intent=intent,
                citations_json=citations_json,
                model_used=model_used,
                latency_ms=latency_ms,
                tokens_used=tokens_used
            )
            db.add(record)
            db.commit()
        except Exception:
            db.rollback()

rag_assistant = RAGAssistant()
