"""
Document service for handling document operations, embeddings, and retrieval.
"""
import os
import time
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Document, QueryLog
from utils.loaders import Loader
from utils.chroma_store import Chroma_VectorStore
from utils import logger


class DocumentService:    
    async def save_document_metadata(
        self, 
        db: AsyncSession, 
        filename: str, 
        file_type: str, 
        file_path: str,
        file_size: int
    ) -> Document:
        """Save document metadata to database"""
        try:
            document = Document(
                filename=filename,
                file_type=file_type,
                file_path=file_path,
                file_size=file_size,
            )
            db.add(document)
            await db.commit()
            await db.refresh(document)
            logger.info(f"Document metadata saved: {filename}")
            return document
        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving document metadata: {str(e)}")
            raise
            
    
    async def list_all_documents(self, db: AsyncSession) -> List[Document]:
        """Retrieve all documents from database"""
        try:
            result = await db.execute(select(Document).order_by(Document.upload_date.desc()))
            documents = result.scalars().all()
            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise
    
