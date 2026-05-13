from crewai import Agent, LLM

from src.agents_src.config.agent_settings import AgentSettings
from src.agents_src.tools.rag_qa_tool import rag_query_tool

_settings = AgentSettings()

summarizer_agent = Agent(
    role="Summarizer Agent",
    llm=LLM(
        model=_settings.crewai_openai_model(),
        api_key=_settings.OPENAI_API_KEY,
        temperature=0.1,
    ),
    goal="Condense and refine answers into clear, concise summaries with key takeaways, "
         "ensuring they remain accurate and evidence-based.",
    backstory="You are an expert editor specializing in distilling complex information "
              "into digestible insights. You highlight essentials without losing context.",
    verbose=True,
)
