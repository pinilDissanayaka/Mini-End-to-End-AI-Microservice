from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import os
import shutil
from pathlib import Path

from database import get_db
from schema import (
    UploadResponse, 
    ListDocumentsResponse, 
    DocumentInfo,
    QueryRequest, 
    QueryResponse
)
from service.document_service import DocumentService
from utils import logger, Loader, Chroma_VectorStore


router = APIRouter(prefix="/api/v1", tags=["documents"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".json", ".md", ".docx", ".pptx"}


def get_document_service():
    """Dependency to get document service instance"""
    return DocumentService()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    doc_service: DocumentService = Depends(get_document_service),    
):
    """
    Upload a document (PDF, TXT, CSV, JSON, MD, DOCX, PPTX) for processing.
    
    The document will be:
    1. Saved to disk
    2. Metadata stored in database
    3. Text extracted and embedded
    4. Stored in vector database for retrieval
    """
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not supported. Allowed: {ALLOWED_EXTENSIONS}"
            )
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        
        document = await doc_service.save_document_metadata(
            db=db,
            filename=file.filename,
            file_type=file_ext,
            file_path=str(file_path),
            file_size=file_size
        )
        
        try:
            loader = Loader(file_paths=[str(file_path)])
            text_content = await loader.load()
            vector_store = Chroma_VectorStore()
            await vector_store.build_vector_store(
                text=text_content
            )
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
        
        return UploadResponse(
            filename=file.filename,
            file_type=file_ext,
            file_size=file_size,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/list_documents", response_model=ListDocumentsResponse)
async def list_documents(
    db: AsyncSession = Depends(get_db),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    List all uploaded documents with their metadata.
    
    Returns:
    - List of documents with id, filename, type, upload date, size, and status
    - Total count of documents
    """
    try:
        documents = await doc_service.list_all_documents(db)
        
        document_infos = [
            DocumentInfo(
                id=doc.id,
                filename=doc.filename,
                file_type=doc.file_type,
                upload_date=doc.upload_date,
                file_size=doc.file_size,
            )
            for doc in documents
        ]
        
        return ListDocumentsResponse(
            documents=document_infos,
            total_count=len(document_infos)
        )
        
    except Exception as e:
        logger.error(f"List documents error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Query the document knowledge base with a question.
    
    Uses RAG (Retrieval-Augmented Generation) to:
    1. Retrieve relevant document chunks from vector store
    2. Generate answer using LLM with retrieved context
    3. Log query and latency
    
    Parameters:
    - question: The question to ask
    - top_k: Number of relevant chunks to retrieve (default: 3)
    
    Returns:
    - Generated answer
    - Query latency in milliseconds
    - Number of retrieved documents
    - Sources of information
    """
    try:
        result = await doc_service.query_documents(
            db=db,
            question=request.question,
            top_k=request.top_k
        )
        
        return QueryResponse(
            question=request.question,
            answer=result["answer"],
            latency_ms=result["latency_ms"],
            retrieved_docs=result["retrieved_docs"],
            sources=result["sources"]
        )
        
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
