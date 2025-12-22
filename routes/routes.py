from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from service import get_document_service
from sqlalchemy.ext.asyncio import AsyncSession
import os
import shutil
from pathlib import Path
import time
from database import get_db
from schema import (
    UploadResponse, 
    ListDocumentsResponse, 
    DocumentInfo,
    ChatRequest,    
    ChatResponse
)
from service.document_service import DocumentService
from service.chat_service import ChatService, get_chat_service
from utils import logger, Loader, Chroma_VectorStore, get_chroma_vector_store, config
from agent import get_chat_response, build_graph


router = APIRouter(prefix="/api/v1")

# Use config for upload directory
UPLOAD_DIR = Path(config.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = config.ALLOWED_EXTENSIONS



@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    doc_service: DocumentService = Depends(get_document_service),
    vector_store: Chroma_VectorStore = Depends(get_chroma_vector_store),    
):
    """
    Upload a document to the server.

    Args:
        file (UploadFile): The document to upload.
        db (AsyncSession): The database session to use.
        doc_service (DocumentService): The document service to use.
        vector_store (Chroma_VectorStore): The vector store to use.

    Returns:
        UploadResponse: The response containing the filename, file type, and file size.

    Raises:
        HTTPException: If the file type is not supported, or if the upload fails.
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




@router.post("/query", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    background_tasks: BackgroundTasks,
    graph=Depends(build_graph), 
    vector_store: Chroma_VectorStore = Depends(get_chroma_vector_store),
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Process a chat request using the provided graph and vector store.

    Args:
    - request (ChatRequest): The chat request containing the question and thread id.
    - background_tasks (BackgroundTasks): The background tasks to add the logging task to.
    - graph (StateGraph): The graph to use for the chat.
    - vector_store (Chroma_VectorStore): The vector store to use for the chat.
    - db (AsyncSession): The database session to use for logging the chat message.
    - chat_service (ChatService): The chat service to use for logging the chat message.

    Returns:
    - ChatResponse: The response containing the answer to the chat request.

    Raises:
    - HTTPException: If an internal error occurred while processing the request.
    """
    try:
        start_time = time.time()
        
        response = await get_chat_response(
            graph=graph,
            question=request.question,
            thread_id=request.thread_id,
            vector_store=vector_store
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        background_tasks.add_task(
            chat_service.log_chat_message,
            db=db,
            thread_id=request.thread_id,
            question=request.question,
            answer=response,
            latency_ms=latency_ms
        )
        
        return ChatResponse( 
            response=response,
        )
        
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="An internal error occurred while processing the request.")
  
