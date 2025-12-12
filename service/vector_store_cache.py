import asyncio
from utils import logger, Chroma_VectorStore
from cachetools import LRUCache
from threading import Lock


vector_store_cache = LRUCache(maxsize=64)
_vector_cache_lock = Lock()

async def get_cached_vector_store(agent_name: str) -> Chroma_VectorStore:
    """
    Retrieves a Chroma_VectorStore from the cache or creates a new one if not present.

    Args:
        agent_name (str): The name of the agent for which the vector store is being requested.

    Returns:
        Chroma_VectorStore: The Chroma_VectorStore associated with the given agent name.
    """

    loop = asyncio.get_running_loop()
    with _vector_cache_lock:
        if agent_name in vector_store_cache:
            
            logger.info(f"Using cached vector store for {agent_name}")
            
            return vector_store_cache[agent_name]
    # Create VectorStore outside the lock to avoid blocking
    vector_store = await loop.run_in_executor(None, Chroma_VectorStore, agent_name, "./chroma_db")
    with _vector_cache_lock:
        vector_store_cache[agent_name] = vector_store
    return vector_store


def get_vector_store() -> Chroma_VectorStore:
    """
    Get the default vector store for document QA service.
    
    Returns:
        Chroma_VectorStore: The vector store instance for documents
    """
    return Chroma_VectorStore(
        collection_name="documents",
        persistance_path="./chroma_db"
    )


