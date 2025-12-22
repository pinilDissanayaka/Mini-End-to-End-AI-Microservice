import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv, find_dotenv
from typing import AsyncGenerator
from utils.config import config


load_dotenv(find_dotenv())

Base = declarative_base()


engine = create_async_engine(
    config.DATABASE_URL, 
    echo=config.DATABASE_ECHO, 
    future=True, 
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    A generator that yields a database session object.

    The database session is opened when the generator is called and
    closed when the generator is exited. This function is meant to
    be used as a FastAPI dependency.

    Yields:
        Session: A database session object.
    """
    async with SessionLocal() as session:
        yield session