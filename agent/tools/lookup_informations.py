from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from service import get_cached_vector_store


@tool
async def lookup_informations(query: str, config:RunnableConfig) -> str:
    """Consult the company FAQ, packages, pricings to answer the user's query."""
    """
    Tool to lookup information from the vector store of the given agent_name.

    Args:
        query (str): The query to search for in the vector store.
        config (RunnableConfig): The configuration for the tool.

    Returns:
        str: The content of the pages that match the query, separated by two newlines.
    """
    agent_name = config.get("configurable", {}).get("agent_name")
    
    vector_store = await get_cached_vector_store(agent_name=agent_name)
    
    retriever = await vector_store.query_vector_store() if vector_store else None
    
    if not retriever:
        return "No information available for the query."


    results = await retriever.ainvoke(query)
    
    
    if not results:
        return "No relevant information found for the query."

    

    return "\n\n".join([result.page_content for result in results])

