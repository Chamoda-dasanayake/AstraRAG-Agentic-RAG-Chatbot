from crewai import Crew

from src.agents_src.agents.question_answer_agent import qa_agent
from src.agents_src.tasks.question_answer_task import qa_task
from src.agents_src.agents.summarizer_agent import summarizer_agent  # New import
from src.agents_src.tasks.summarizer_task import summarizer_task  # New import


qa_crew = Crew(
    agents=[qa_agent, summarizer_agent],
    tasks=[qa_task, summarizer_task],
    verbose=True,
)