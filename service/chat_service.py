from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import ChatMessage
from utils import logger


class ChatService:
    """Service for handling chat message logging operations"""
    
    async def log_chat_message(
        self, 
        db: AsyncSession, 
        thread_id: str,
        question: str,
        answer: str,
        latency_ms: Optional[float] = None
    ) -> ChatMessage:
        """
        Log a chat message to the database.

        Args:
            db (AsyncSession): The database session to use.
            thread_id (str): The unique identifier for the chat thread.
            question (str): The user's question.
            answer (str): The AI's response.
            latency_ms (Optional[float]): The response latency in milliseconds.

        Returns:
            ChatMessage: The saved chat message.

        Raises:
            Exception: If there is an error saving the chat message.
        """
        try:
            chat_message = ChatMessage(
                thread_id=thread_id,
                question=question,
                answer=answer,
                latency_ms=latency_ms,
            )
            db.add(chat_message)
            await db.commit()
            await db.refresh(chat_message)
            logger.info(f"Chat message logged for thread: {thread_id}")
            return chat_message
        except Exception as e:
            await db.rollback()
            logger.error(f"Error logging chat message: {str(e)}")
            raise


def get_chat_service() -> ChatService:
    """
    Get an instance of the ChatService.

    Returns:
        ChatService: The instance of the ChatService.
    """
    return ChatService()
