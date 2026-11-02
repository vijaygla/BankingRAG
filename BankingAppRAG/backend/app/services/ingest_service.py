import os
import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.rag import Document, DocumentChunk
from app.ai.chunking import parse_document_content
from app.ai.generative_engine import ai_client
from app.services.audit_service import audit_service
from app.ai.cache_service import cache_service

logger = logging.getLogger(__name__)

class IngestionService:
    @staticmethod
    async def ingest_document(
        db: Session,
        file_bytes: bytes,
        filename: str,
        title: str,
        user_id: int,
        ip_address: str = None
    ) -> Document:
        """
        Parses document (JSON, TXT, PDF), generates 800-token / 120-token overlap chunks,
        creates embeddings, and stores in MS SQL Server.
        """
        ext = filename.split(".")[-1].upper() if "." in filename else "TXT"
        chunks_data = parse_document_content(file_bytes, filename, title)
        
        if not chunks_data:
            raise ValueError(f"No parseable text extracted from {filename}.")

        # Create Document record
        doc_record = Document(
            title=title,
            filename=filename,
            file_type=ext,
            total_chunks=len(chunks_data)
        )
        db.add(doc_record)
        db.flush()

        # Generate embeddings and save chunks
        for idx, item in enumerate(chunks_data):
            chunk_content = item["content"]
            chunk_meta = item["metadata"]
            chunk_meta["chunk_index"] = idx
            
            try:
                emb = await ai_client.get_embedding(chunk_content)
                emb_json = json.dumps(emb)
            except Exception as e:
                logger.warning(f"Embedding generation failed for chunk {idx}: {e}")
                emb_json = None

            chunk_record = DocumentChunk(
                document_id=doc_record.id,
                chunk_index=idx,
                content=chunk_content,
                metadata_json=json.dumps(chunk_meta),
                embedding_vector=emb_json
            )
            db.add(chunk_record)

        db.commit()
        db.refresh(doc_record)

        # Clear query cache so new documents are immediately queryable by RAG
        try:
            cache_service.clear_all(db)
        except Exception as cache_err:
            logger.warning(f"Failed to clear query cache: {cache_err}")

        audit_service.log_action(
            db, action="DOCUMENT_INGESTED", user_id=user_id, ip_address=ip_address,
            details=f"Ingested {filename} ({ext}) with {len(chunks_data)} chunks"
        )
        return doc_record

    @staticmethod
    def list_documents(db: Session) -> List[Dict[str, Any]]:
        """Returns all ingested documents ordered by creation date."""
        docs = db.query(Document).order_by(Document.created_at.desc()).all()
        return [
            {
                "id": d.id,
                "title": d.title,
                "filename": d.filename,
                "file_type": d.file_type,
                "total_chunks": d.total_chunks,
                "created_at": d.created_at.isoformat() if d.created_at else None
            }
            for d in docs
        ]

    @staticmethod
    def delete_document(db: Session, doc_id: int, user_id: int, ip_address: str = None) -> bool:
        """Deletes a document and its cascading chunks, then invalidates cache."""
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return False
        
        fname = doc.filename
        db.delete(doc)
        db.commit()

        try:
            cache_service.clear_all(db)
        except Exception:
            pass

        audit_service.log_action(
            db, action="DOCUMENT_DELETED", user_id=user_id, ip_address=ip_address,
            details=f"Deleted document ID {doc_id} ({fname}) and its associated vector chunks"
        )
        return True

    @staticmethod
    async def seed_sample_knowledge_base(db: Session, admin_user_id: int):
        """
        Auto-seeds the 3 sample files if the documents table is currently empty:
        - banking_interest_rates.json
        - loan_compliance_rules.txt
        - banking_policy.pdf
        """
        count = db.query(Document).count()
        if count > 0:
            logger.info("Knowledge base already seeded.")
            return

        base_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        sample_files = [
            ("banking_interest_rates.json", "Capgemini Commercial Bank Interest Rates & Fixed Deposits"),
            ("loan_compliance_rules.txt", "Retail Lending and Credit Compliance Guidelines"),
            ("banking_policy.pdf", "Official Comprehensive Banking Operating Manual")
        ]

        logger.info(f"Checking for sample knowledge files in {base_data_dir}...")
        for fname, ftitle in sample_files:
            fpath = os.path.join(base_data_dir, fname)
            if os.path.exists(fpath):
                try:
                    with open(fpath, "rb") as f:
                        file_bytes = f.read()
                    logger.info(f"Ingesting default knowledge asset: {fname}...")
                    await IngestionService.ingest_document(
                        db, file_bytes=file_bytes, filename=fname, title=ftitle, user_id=admin_user_id
                    )
                    logger.info(f"Successfully ingested: {fname}")
                except Exception as e:
                    logger.error(f"Failed to ingest sample file {fname}: {e}")

ingest_service = IngestionService()
