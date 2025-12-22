from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from utils import Chroma_VectorStore


@tool
async def lookup_informations(query: str, config:RunnableConfig) -> str:
    """
    This tool takes in a query and a configuration that contains a reference to a Chroma VectorStore.
    It uses the vector store to query the documents and then returns the relevant information.
    
    If the vector store is not provided, it will return "No information available for the query."
    
    If the query does not return any results, it will return "No relevant information found for the query."
    
    Otherwise, it will return the page content of the relevant documents, separated by two newline characters.
    """
    vector_store: Chroma_VectorStore = config.get("configurable").get("vector_store")
    
    
    retriever = await vector_store.query_vector_store() if vector_store else None
    
    if not retriever:
        return "No information available for the query."


    results = await retriever.ainvoke(query)
    
    
    if not results:
        return "No relevant information found for the query."

    

    return "\n\n".join([result.page_content for result in results])

