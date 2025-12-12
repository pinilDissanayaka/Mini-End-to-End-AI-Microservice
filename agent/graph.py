from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from utils import logger, llm
from agent.state import State
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
from agent.tools import lookup_informations


memory = MemorySaver()

    
def handle_tool_error(state) -> dict:
    """
    Function to handle tool errors. When a tool raises an error, this function gets called
    with the current state. It returns a dictionary with the key "messages", which is a list
    of ToolMessage objects. The content of each message is the error message of the tool
    that raised the error and the tool call id is the id of the tool call that raised the
    error. This function is used as a fallback for tool nodes in the state graph, so that
    if a tool raises an error, the error is propagated back to the user.
    """
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    """
    Create a tool node with a fallback to handle tool errors.

    :param tools: the list of tools to include in the tool node
    :type tools: list
    :return: a tool node with a fallback to handle tool errors
    :rtype: dict
    """
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


 
class Assistant:
    def __init__(self, runnable: Runnable):
        """
        Initialize an Assistant object.

        :param runnable: the runnable that will be executed
        :type runnable: Runnable
        """
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        """
        Invoke the runnable with the given state and configuration.

        This function is a simple wrapper around the invoke method of the
        runnable. It adds the passenger_id to the state and breaks the loop
        if the result of the invoke method is not empty.

        :param state: the state of the conversation
        :type state: State
        :param config: the configuration of the runnable
        :type config: RunnableConfig
        :return: a dictionary with the result of the invoke method
        :rtype: dict
        """

        while True:
            configuration = config.get("configurable", {})
            state = {**state}
            result = self.runnable.invoke(state)
            
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}



async def build_graph(
    agent_prompt: str
):
    agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
                agent_prompt
        ),
        ("placeholder", "{messages}"),
    ]
    )

    tools = [
        lookup_informations,
    ]

        


    agent_runnable = agent_prompt | llm.bind_tools(tools)


    builder = StateGraph(State)


    builder.add_node("assistant", Assistant(agent_runnable))
    builder.add_node("tools", create_tool_node_with_fallback(tools))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    builder.add_edge("tools", "assistant")


    noopy_agent_graph = builder.compile(checkpointer=memory)
    
    return noopy_agent_graph


async def get_chat_response(graph, question:str, thread_id:str="1", agent_name:str="default_agent"):
    try:
        config = {
            "configurable": {
                "thread_id": thread_id,
                "agent_name": agent_name
            }
        }
        
        response = ""

        async for chunk in graph.astream(
            {"messages": ("user", question)}, config, stream_mode="values"
        ):
            if chunk["messages"]:
                response = chunk["messages"][-1].content
                

        return response
    except Exception as e:
        logger.error(f"Error getting chat response: {e}")
