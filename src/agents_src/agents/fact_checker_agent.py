from crewai import Agent, LLM

from src.agents_src.config.agent_settings import AgentSettings
from src.agents_src.tools.rag_qa_tool import rag_query_tool

_settings = AgentSettings()

fact_checker_agent = Agent(
    role="Senior Fact-Checker and Hallucination Auditor",
    llm=LLM(
        model=_settings.crewai_openai_model(),
        api_key=_settings.llm_api_key(),
        temperature=0.1,
    ),
    tools=[rag_query_tool],
    goal="Verify all answers are strictly factual and derived from the retrieved documents. "
         "Reject any hallucinated content.",
    backstory="You are a meticulous auditor. You accept zero hallucination and verify "
              "every claim against the provided evidence before approving the final answer.",
    verbose=True,
    max_iter=3,
    max_retry_limit=2,
)
