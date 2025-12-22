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
        """
        Save document metadata to database.

        Args:
            db (AsyncSession): The database session to use.
            filename (str): The filename of the document.
            file_type (str): The type of the document (e.g. PDF, TXT, etc.).
            file_path (str): The path to the document file.
            file_size (int): The size of the document file in bytes.

        Returns:
            Document: The saved document metadata.

        Raises:
            Exception: If there is an error saving the document metadata.
        """
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
        """
        List all uploaded documents with their metadata.

        Args:
            db (AsyncSession): The database session to use.

        Returns:
            List[Document]: A list of documents with their metadata.

        Raises:
            Exception: If there is an error listing the documents.
        """
        try:
            result = await db.execute(select(Document).order_by(Document.upload_date.desc()))
            documents = result.scalars().all()
            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise
    


def get_document_service() -> DocumentService:
    """
    Get an instance of the DocumentService.

    Returns:
        DocumentService: The instance of the DocumentService.
    """
    return DocumentService()