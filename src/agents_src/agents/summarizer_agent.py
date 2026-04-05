from crewai import Agent, LLM

from src.agents_src.llm.get_llm import get_llm_for_agent

name = "Summarizer Agent"
llm = get_llm_for_agent(name)


summarizer_agent = Agent(
    role="Summarizer Agent",
    llm=llm,
    goal="Condense and refine answers from the Question Answer Agent into clear, concise summaries with key takeaways, ensuring they remain accurate and evidence-based.",
    backstory="You are an expert editor specializing in distilling complex information into digestible insights. You excel at highlighting essentials without losing context, making responses more user-friendly and actionable.",
    verbose=True,
)
