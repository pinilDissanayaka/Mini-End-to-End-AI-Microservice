from .huggingface_wrapper import embedding_model
from langchain_experimental.text_splitter import SemanticChunker
from langchain_chroma import Chroma
from utils.config import config



class Chroma_VectorStore:
    def __init__(self) -> None:
        """
        Initialize a Chroma VectorStore object.

        Args:
            collection_name (str): The name of the collection to store vectors in.
            persistance_path (str): The path to the directory where the vector store will be persisted.

        Returns:
            None
        """
        self.chroma = Chroma(
            collection_name=config.VECTOR_STORE_COLLECTION,
            embedding_function=embedding_model,
            persist_directory=config.VECTOR_STORE_PATH,
        )
        
    async def build_vector_store(self, text: str) -> None:
        chunker=SemanticChunker(
            embeddings=embedding_model,
        )

        chunked_texts = chunker.split_text(
            text=text
        )
        
        await self.chroma.aadd_texts(
            texts=chunked_texts
        )
        
        return self.chroma
    

    async def query_vector_store(self):
        return self.chroma.as_retriever()
    
    
def get_chroma_vector_store() -> Chroma_VectorStore:
    """
    Get an instance of the Chroma_VectorStore.

    Returns:
        Chroma_VectorStore: The instance of the Chroma_VectorStore.
    """
    return Chroma_VectorStore()