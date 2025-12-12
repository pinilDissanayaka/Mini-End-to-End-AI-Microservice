import asyncio
from utils import logger
from cachetools import LRUCache
from sqlalchemy.ext.asyncio import AsyncSession
from prompt import load_agent_prompt



prompt_cache = LRUCache(maxsize=512) 
_prompt_lock = asyncio.Lock()

graph_cache = LRUCache(maxsize=512)
_graph_lock = asyncio.Lock()



async def get_cached_prompt(agent_name: str, db: AsyncSession) -> str:
    async with _prompt_lock:
        if agent_name in prompt_cache:
            return prompt_cache[agent_name]["prompt"]

    prompt = load_agent_prompt()

    async with _prompt_lock:
        prompt_cache[agent_name] = {
            "prompt": prompt
        }

    return prompt



async def get_cached_graph(agent_name: str, db: AsyncSession):
    from agent import build_graph 
    async with _graph_lock:
        if agent_name in graph_cache:
            return graph_cache[agent_name]

    prompt = load_agent_prompt()
    
    graph = await build_graph(
        prompt
    )

    async with _graph_lock:
        graph_cache[agent_name] = graph

        prompt_cache[agent_name] = {
            "prompt": prompt
        }

    return graph



        

        
        

        
        
        
        
        


