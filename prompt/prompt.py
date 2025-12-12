

def load_agent_prompt()-> str:
    with open("prompt/agent_prompt.md", "r", encoding="utf-8") as file:
        AGENT_PROMPT =  file.read()
        
    return AGENT_PROMPT