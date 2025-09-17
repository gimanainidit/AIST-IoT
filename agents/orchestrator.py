# agents/orchestrator.py
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents.format_scratchpad.openai_functions import format_to_openai_function_messages
from langchain.agents.output_parsers.openai_functions import OpenAIFunctionsAgentOutputParser

# Fungsi ini merakit dan mengembalikan agent yang siap pakai
def create_aist_agent(tools: list, llm):
    """Membangun AIST-IoT Agent dari tools dan LLM yang diberikan."""
    
    llm_with_tools = llm.bind_functions(tools)

    prompt = ChatPromptTemplate.from_messages([...]) # Prompt template sama seperti sebelumnya

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    return AgentExecutor(agent=agent, tools=tools, verbose=True)