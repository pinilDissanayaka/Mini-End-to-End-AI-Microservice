from database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, func, Float
from typing import Optional
import datetime
import decimal
from sqlalchemy import BigInteger, Boolean, DateTime, Double, Enum, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB


class Document(Base):
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    upload_date: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    file_size: Mapped[int] = mapped_column(Integer, nullable=True)
    
    
class QueryLog(Base):
    """Model for logging queries and their latencies"""
    __tablename__ = "query_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    retrieved_docs: Mapped[int] = mapped_column(Integer, default=0)
    
    
class Conversation(Base):
    pass

    __tablename__ = "conversations"
    
    