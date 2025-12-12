from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    web_name:str = "nolooptech"
    thread_id: str = "1"
    message: str = "Hello"
    
    

class ChatResponse(BaseModel):
    thread_id: str
    response: str
    score: list
    response_type: str = "text"
    tool_data: Optional[list] = None
    suggestions: Optional[list] = None

class LeadScoreGeneratorRequest(BaseModel):
    project_id: int


class ImproveChatRequest(BaseModel):
    user_question: str
    improved_response: str
    
    
class HighlightRequest(BaseModel):
    project_code: str
    
    
class TrainAgentRequest(BaseModel):
    web_name: str = "nolooptech"
    traing_data:str


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

