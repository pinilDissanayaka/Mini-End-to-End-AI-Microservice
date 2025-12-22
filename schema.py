from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    thread_id: str = "1"
    question: str
    
    

class ChatResponse(BaseModel):
    response: str


# New schemas for document QA service
class UploadResponse(BaseModel):
    filename: str
    file_type: str
    file_size: int
    status: str
    message: str


class DocumentInfo(BaseModel):
    id: int
    filename: str
    file_type: str
    upload_date: datetime
    file_size: int
    status: str


class ListDocumentsResponse(BaseModel):
    documents: List[DocumentInfo]
    total_count: int


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3


class QueryResponse(BaseModel):
    question: str
    answer: str
    retrieved_docs: int
    latency_ms: float
    sources: List[str]

