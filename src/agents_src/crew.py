from crewai import Crew

from src.agents_src.agents.question_answer_agent import qa_agent
from src.agents_src.tasks.question_answer_task import qa_task
from src.agents_src.agents.summarizer_agent import summarizer_agent
from src.agents_src.tasks.summarizer_task import summarizer_task
from src.agents_src.agents.fact_checker_agent import fact_checker_agent
from src.agents_src.tasks.fact_checker_task import fact_checker_task
from src.agents_src.agents.response_formatter_agent import response_formatter_agent
from src.agents_src.tasks.response_formatter_task import response_formatter_task

qa_crew = Crew(
    agents=[qa_agent, summarizer_agent, fact_checker_agent, response_formatter_agent],
    tasks=[qa_task, summarizer_task, fact_checker_task, response_formatter_task],
    verbose=True,
)