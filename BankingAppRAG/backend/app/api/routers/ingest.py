from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_admin
from app.models.user import User
from app.schemas.admin import IngestResponse
from app.services.ingest_service import ingest_service

router = APIRouter(prefix="/ingest", tags=["Knowledge Ingestion & System Control Module"])

@router.post("", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_policy_document(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(None),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Manuals & Rules PDF/JSON/TXT Drag-and-Drop Ingestion:
    Allows Bank Admins to upload rulebooks and policy manuals.
    Applies 800-token boundary sizes and 120-token window overlap ratios,
    generates vector embeddings via Capgemini Generative Engine, and indexes in MS SQL.
    """
    filename = file.filename
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ["pdf", "json", "txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. RAG pipeline accepts .pdf, .json, and .txt."
        )

    file_bytes = await file.read()
    doc_title = title or filename.rsplit(".", 1)[0].replace("_", " ").title()

    try:
        ip = request.client.host if request.client else None
        doc = await ingest_service.ingest_document(
            db=db,
            file_bytes=file_bytes,
            filename=filename,
            title=doc_title,
            user_id=current_admin.id,
            ip_address=ip
        )
        return IngestResponse(
            message=f"Document '{filename}' successfully parsed, chunked, vectorized, and indexed.",
            filename=doc.filename,
            file_type=doc.file_type,
            total_chunks=doc.total_chunks,
            document_id=doc.id
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/documents", status_code=status.HTTP_200_OK)
async def list_policy_documents(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    List all ingested banking policy documents and vector assets in the knowledge base.
    Strictly restricted to Bank Admin.
    """
    return ingest_service.list_documents(db)

@router.delete("/documents/{doc_id}", status_code=status.HTTP_200_OK)
async def delete_policy_document(
    doc_id: int,
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Deletes a policy document and its vector chunks from the vector database.
    Strictly restricted to Bank Admin.
    """
    ip = request.client.host if request.client else None
    success = ingest_service.delete_document(db, doc_id=doc_id, user_id=current_admin.id, ip_address=ip)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} not found."
        )
    return {"message": f"Document ID {doc_id} and associated vector embeddings deleted successfully."}

@router.post("/seed", status_code=status.HTTP_200_OK)
async def trigger_sample_ingestion_seed(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Seeds the 3 baseline banking knowledge assets (JSON, TXT, PDF) into the Vector Store.
    """
    await ingest_service.seed_sample_knowledge_base(db, admin_user_id=current_admin.id)
    return {"message": "Knowledge base seeding routine completed."}
