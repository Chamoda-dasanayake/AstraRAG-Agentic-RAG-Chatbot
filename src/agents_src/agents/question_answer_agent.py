from crewai import Agent, LLM

from src.agents_src.config.agent_settings import AgentSettings
from src.agents_src.tools.rag_qa_tool import rag_query_tool

_settings = AgentSettings()

qa_agent = Agent(
    role="Question Answer Agent",
    llm=LLM(
        model=_settings.crewai_openai_model(),
        api_key=_settings.llm_api_key(),
        temperature=0.1,
    ),
    tools=[rag_query_tool],
    goal="Answer user queries ONLY using the rag_query_tool to retrieve context from documents. "
         "You MUST always call rag_query_tool first before writing any answer.",
    backstory="You are a strict document analyst. You NEVER answer from memory. "
              "You ALWAYS call rag_query_tool first to search the knowledge base, "
              "then use ONLY the retrieved text to form your answer.",
    verbose=True,
    max_iter=5,
    max_retry_limit=2,
)