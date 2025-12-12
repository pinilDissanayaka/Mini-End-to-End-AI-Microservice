from .huggingface_wrapper import embedding_model
from langchain_experimental.text_splitter import SemanticChunker
from langchain_chroma import Chroma



class Chroma_VectorStore:
    def __init__(self, collection_name:str, persistance_path: str) -> None:
        self.chroma = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_model,
            persist_directory=persistance_path,
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